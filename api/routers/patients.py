from fastapi import APIRouter, Query
from typing import Optional
from api.services.data_loader import FEATURES, CONFLICTS

router = APIRouter(prefix="/patients", tags=["Patients"])


import pandas as pd

AUDIT_LOG = "data/processed/audit_log.csv"

@router.get("/summary")
def patient_summary():

    total = int(len(FEATURES))
    high_risk = int(FEATURES["predicted_high_risk"].sum())
    normal = total - high_risk

    try:
        audit = pd.read_csv(AUDIT_LOG)
        resolved_ids = set(audit["patient_id"].astype(str))
    except:
        resolved_ids = set()

    active_conflicts = CONFLICTS[
        (CONFLICTS["conflict_types"] != "no_conflict")
        &
        (~CONFLICTS["patient_id"].astype(str).isin(resolved_ids))
    ]

    patients_with_conflicts = int(len(active_conflicts))

    patients_analysed = int(len(CONFLICTS))

    conflict_rate = round(
        patients_with_conflicts * 100 / patients_analysed,
        1
    )

    return {
        "total_patients": total,
        "high_risk_patients": high_risk,
        "normal_patients": normal,
        "patients_analysed": patients_analysed,
        "patients_with_conflicts": patients_with_conflicts,
        "conflict_rate": conflict_rate,
    }


@router.get("/")
def all_patients(
    search:     Optional[str] = Query(None),
    district:   Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None, description="high | normal"),
    page:  int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
):
    df = FEATURES.copy()
    name_map = CONFLICTS[["patient_id", "name", "village"]].drop_duplicates("patient_id")
    df = df.merge(name_map, on="patient_id", how="left")

    if risk_level == "high":
        df = df[df["predicted_high_risk"] == 1]
    elif risk_level == "normal":
        df = df[df["predicted_high_risk"] == 0]

    if search:
        s = search.strip().lower()
        mask = (
    df["patient_id"].astype(str).str.lower().str.contains(s, na=False) |
    df["name"].astype(str).str.lower().str.contains(s, na=False) |
    df["district"].astype(str).str.lower().str.contains(s, na=False) |
    df["village_x"].astype(str).str.lower().str.contains(s, na=False)
)
        df = df[mask]

    if district:
        df = df[df["district"].str.lower() == district.strip().lower()]

    total_filtered = len(df)
    start   = (page - 1) * limit
    records = df.iloc[start: start + limit].to_dict(orient="records")

    return {"total": total_filtered, "page": page, "limit": limit, "records": records}


@router.get("/high-risk")
def high_risk_patients(
    search:   Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    page:  int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
):
    df = FEATURES[FEATURES["predicted_high_risk"] == 1].copy()
    name_map = CONFLICTS[["patient_id", "name", "village"]].drop_duplicates("patient_id")
    df = df.merge(name_map, on="patient_id", how="left")

    if search:
        s = search.strip().lower()
        mask = (
            df["patient_id"].str.lower().str.contains(s, na=False) |
            df["name"].str.lower().str.contains(s, na=False) |
            df["district"].str.lower().str.contains(s, na=False)
        )
        df = df[mask]

    if district:
        df = df[df["district"].str.lower() == district.strip().lower()]

    total_filtered = len(df)
    start   = (page - 1) * limit
    records = df.iloc[start: start + limit].to_dict(orient="records")

    return {"total": total_filtered, "page": page, "limit": limit, "records": records}


@router.get("/districts")
def patient_districts():
    return sorted(FEATURES["district"].dropna().unique().tolist())