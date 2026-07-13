from fastapi import APIRouter, Query
from typing import Optional
from api.services.data_loader import CONFLICTS
import pandas as pd

router = APIRouter(prefix="/audit", tags=["Audit"])
AUDIT_LOG = "data/processed/audit_log.csv"

@router.get("/pipeline")
def pipeline_status():
    return {
        "dataset_generation":  True,
        "standardization":     True,
        "blocking":            True,
        "entity_resolution":   True,
        "conflict_detection":  True,
        "reliability_scoring": True,
        "bayesian_resolution": True,
        "risk_prediction":     True,
    }


@router.get("/resolved")
def resolved_records(
    search: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
):
    try:
        df = pd.read_csv(AUDIT_LOG)
    except:
        df = pd.DataFrame(columns=[
            "patient_id",
            "name",
            "district",
            "conflict_types",
            "resolution_method",
            "resolved_by",
            "resolved_at"
        ])

    if search:
        s = search.strip().lower()
        mask = (
            df["patient_id"].astype(str).str.lower().str.contains(s, na=False)
            |
            df["name"].astype(str).str.lower().str.contains(s, na=False)
            |
            df["district"].astype(str).str.lower().str.contains(s, na=False)
        )
        df = df[mask]

    if district:
        df = df[
            df["district"].astype(str).str.lower()
            == district.strip().lower()
        ]

    total_filtered = len(df)

    start = (page - 1) * limit

    records = df.iloc[
        start:start + limit
    ].to_dict(orient="records")

    return {
        "total": total_filtered,
        "page": page,
        "limit": limit,
        "records": records,
    }

@router.get("/stats")
def audit_stats():
    try:
        audit = pd.read_csv(AUDIT_LOG)
        total_resolved = len(audit)
    except:
        total_resolved = 0

    active_conflicts = int(
        CONFLICTS[
            CONFLICTS["conflict_types"] != "no_conflict"
        ].shape[0]
    ) - total_resolved

    return {
        "total_resolved": total_resolved,
        "with_conflicts": active_conflicts,
        "auto_resolved": total_resolved,
        "manual_pending": active_conflicts,
    }