from fastapi import APIRouter, Query
from typing import Optional
from api.services.data_loader import CONFLICTS
from api.services.conflict_services import get_patient_conflict
import pandas as pd
from datetime import datetime
from pydantic import BaseModel

class ResolveRequest(BaseModel):
    resolved_by: str = "District Health Officer"

router = APIRouter(prefix="/conflicts", tags=["Conflicts"])
AUDIT_LOG = "data/processed/audit_log.csv"

# Human-readable conflict field labels
FIELD_LABELS = {
    "haemoglobin_conflict":     "Haemoglobin Level",
    "blood_pressure_conflict":  "Blood Pressure",
    "blood_sugar_conflict":     "Blood Sugar (Fasting)",
    "anc_visit_conflict":       "ANC Visits",
    "weight_conflict":          "Body Weight",
    "fundal_height_conflict":   "Fundal Height",
    "no_conflict":              "No Conflict",
}

def humanise_conflicts(raw: str) -> str:
    """Convert 'blood_pressure_conflict,anc_visit_conflict' → 'Blood Pressure, ANC Visits'"""
    if not raw or raw == "no_conflict":
        return "No Conflict"
    parts = [c.strip() for c in raw.split(",")]
    return ", ".join(FIELD_LABELS.get(p, p.replace("_", " ").title()) for p in parts)

def enrich_row(row: dict) -> dict:
    row["conflict_label"] = humanise_conflicts(row.get("conflict_types", ""))
    return row


@router.get("/summary")
def conflict_summary():

    total = len(CONFLICTS)

    try:
        audit = pd.read_csv(AUDIT_LOG)

        resolved_ids = set(
            audit["patient_id"].astype(str)
        )

        resolved_count = len(audit)

    except:
        resolved_ids = set()
        resolved_count = 0

    active = CONFLICTS[
        (CONFLICTS["conflict_types"] != "no_conflict")
        &
        (~CONFLICTS["patient_id"].astype(str).isin(resolved_ids))
    ]

    conflict_count = int(active.shape[0])

    return {
        "patients_analysed": int(total),
        "patients_with_conflicts": conflict_count,
        "resolved_conflicts": resolved_count
    }


@router.get("/count")
def conflict_count():
    """Returns just the number of active (unresolved) conflicts — for sidebar badge."""
    try:
        audit = pd.read_csv(AUDIT_LOG)
        resolved_ids = set(audit["patient_id"].astype(str))
    except:
        resolved_ids = set()

    active = CONFLICTS[
        (CONFLICTS["conflict_types"] != "no_conflict")
        &
        (~CONFLICTS["patient_id"].astype(str).isin(resolved_ids))
    ]

    count = int(active.shape[0])
    return {"count": count}


@router.get("/")
def all_conflicts(
    search:   Optional[str] = Query(None, description="Search by name, patient_id, district, or village"),
    district: Optional[str] = Query(None),
    conflict_type: Optional[str] = Query(None, description="e.g. haemoglobin_conflict"),
    has_conflict: Optional[bool] = Query(None),
    page:  int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
):
    df = CONFLICTS.copy()
    try:
        audit = pd.read_csv(AUDIT_LOG)
        resolved_ids = set(audit["patient_id"].astype(str))
        df = df[
            ~df["patient_id"].astype(str).isin(resolved_ids)
        ]
    except:
        pass

    # Search across name, patient_id, district, village
    if search:
        s = search.strip().lower()
        mask = (
            df["name"].str.lower().str.contains(s, na=False) |
            df["patient_id"].str.lower().str.contains(s, na=False) |
            df["district"].str.lower().str.contains(s, na=False) |
            df["village"].str.lower().str.contains(s, na=False)
        )
        df = df[mask]

    if district:
        df = df[df["district"].str.lower() == district.strip().lower()]

    if conflict_type:
        df = df[df["conflict_types"].str.contains(conflict_type, na=False)]

    if has_conflict is not None:
        df = df[df["has_conflict"] == has_conflict]

    total_filtered = len(df)
    start = (page - 1) * limit
    end = start + limit
    page_df = df.iloc[start:end]

    records = [enrich_row(r) for r in page_df.to_dict(orient="records")]

    return {
        "total":   total_filtered,
        "page":    page,
        "limit":   limit,
        "records": records,
    }


@router.get("/districts")
def list_districts():
    """All unique districts — for filter dropdown."""
    return sorted(CONFLICTS["district"].dropna().unique().tolist())


@router.get("/conflict-types")
def list_conflict_types():
    """All unique conflict type keys — for filter dropdown."""
    return [
        {"key": k, "label": v}
        for k, v in FIELD_LABELS.items()
        if k != "no_conflict"
    ]


@router.get("/{patient_id}")
def patient_conflict(patient_id: str):
    result = get_patient_conflict(patient_id)
    if "error" not in result:
        result["conflict_label"] = humanise_conflicts(result.get("conflict_types", ""))
    return result

@router.post("/resolve/{patient_id}")
def resolve_conflict(
    patient_id: str,
    payload: ResolveRequest
):
    row = CONFLICTS[
        (CONFLICTS["patient_id"] == patient_id)
        & (CONFLICTS["conflict_types"] != "no_conflict")
    ]

    if row.empty:
        return {"success": False, "message": "Conflict not found"}

    row = row.iloc[0]

    try:
        audit = pd.read_csv(AUDIT_LOG)
    except:
        audit = pd.DataFrame(columns=[
            "patient_id",
            "name",
            "district",
            "conflict_types",
            "resolution_method",
            "resolved_by",
            "resolved_at"
        ])

    if patient_id not in audit["patient_id"].astype(str).values:
        audit.loc[len(audit)] = {
            "patient_id": patient_id,
            "name": row["name"],
            "district": row["district"],
            "conflict_types": row["conflict_types"],
            "resolution_method": "Bayesian Accepted",
            "resolved_by": payload.resolved_by,
            "resolved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        audit.to_csv(AUDIT_LOG, index=False)

    return {
        "success": True,
        "patient_id": patient_id
    }