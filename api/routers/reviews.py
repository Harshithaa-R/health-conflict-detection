from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field

from api.routers.auth import current_user, require_roles
from api.services.data_loader import CONFLICTS

router = APIRouter(prefix="/reviews", tags=["Reviews"])
OVERRIDES_PATH = Path(__file__).resolve().parents[2] / "data" / "processed" / "manual_overrides.csv"


class OverrideRequest(BaseModel):
    patient_id: str
    field: str = Field(min_length=1, max_length=100)
    source: str = Field(min_length=1, max_length=100)
    chosen_value: str = Field(min_length=1, max_length=500)
    reason: str = Field(min_length=3, max_length=1000)
    status: str = "approved"
    notes: Optional[str] = Field(default="", max_length=2000)


@router.get("/queue")
def review_queue(
    search: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    status_filter: str = Query("pending", alias="status"),
    limit: int = Query(100, ge=1, le=500),
    user: dict = Depends(current_user),
):
    df = CONFLICTS.copy()
    df = df[df["conflict_types"].astype(str) != "no_conflict"]
    if district:
        df = df[df["district"].astype(str).str.casefold() == district.casefold()]
    if search:
        needle = search.casefold()
        cols = [c for c in ("patient_id", "name", "district", "village", "conflict_types") if c in df.columns]
        mask = pd.Series(False, index=df.index)
        for col in cols:
            mask |= df[col].astype(str).str.casefold().str.contains(needle, na=False)
        df = df[mask]

    overrides = _read_overrides()
    status_by_patient = {}
    if not overrides.empty:
        status_by_patient = overrides.sort_values("created_at").groupby("patient_id")["status"].last().to_dict()
    df = df.copy()
    df["review_status"] = df["patient_id"].astype(str).map(status_by_patient).fillna("pending")
    if status_filter != "all":
        df = df[df["review_status"] == status_filter]

    if user["role"] == "chw":
        villages = user.get("assigned_villages", [])
        if not villages:
            df = df.iloc[0:0]
        elif "village" in df:
            df = df[df["village"].astype(str).isin(villages)]

    sort_cols = [c for c in ("severity_score", "num_conflicts") if c in df.columns]
    if sort_cols:
        df = df.sort_values(sort_cols, ascending=False)
    return {"total": int(len(df)), "records": df.head(limit).to_dict(orient="records")}


@router.post("/overrides")
def create_override(payload: OverrideRequest, user: dict = Depends(require_roles("admin", "reviewer"))):
    if payload.status not in {"approved", "rejected", "escalated", "flagged_for_review"}:
        raise HTTPException(status_code=422, detail="Invalid review status")
    matches = CONFLICTS[CONFLICTS["patient_id"].astype(str) == payload.patient_id]
    if matches.empty:
        raise HTTPException(status_code=404, detail="Patient not found in conflict records")

    OVERRIDES_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = _read_overrides()
    row = {
        "patient_id": payload.patient_id,
        "name": str(matches.iloc[0].get("name", "")),
        "district": str(matches.iloc[0].get("district", "")),
        "field": payload.field.strip(),
        "source": payload.source.strip(),
        "chosen_value": payload.chosen_value.strip(),
        "reason": payload.reason.strip(),
        "notes": payload.notes or "",
        "status": payload.status,
        "reviewed_by": user["email"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    pd.concat([df, pd.DataFrame([row])], ignore_index=True).to_csv(OVERRIDES_PATH, index=False)
    return {"success": True, "override": row}


@router.get("/overrides")
def list_overrides(limit: int = Query(200, ge=1, le=1000), user: dict = Depends(current_user)):
    df = _read_overrides()
    if user["role"] == "chw":
        villages = user.get("assigned_villages", [])
        if "village" in df and villages:
            df = df[df["village"].astype(str).isin(villages)]
        else:
            df = df.iloc[0:0]
    return {"total": int(len(df)), "records": df.tail(limit).iloc[::-1].to_dict(orient="records")}


def _read_overrides() -> pd.DataFrame:
    if not OVERRIDES_PATH.exists():
        return pd.DataFrame(columns=["patient_id", "field", "source", "chosen_value", "reason", "notes", "status", "reviewed_by", "created_at"])
    try:
        return pd.read_csv(OVERRIDES_PATH).fillna("")
    except (OSError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=["patient_id", "field", "source", "chosen_value", "reason", "notes", "status", "reviewed_by", "created_at"])
