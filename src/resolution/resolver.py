"""
src/resolution/resolver.py
============================
Conflict resolution engine using source reliability priors
and recency weighting to produce a reconciled patient record.
"""

import logging
from datetime import date
from statistics import median
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

SOURCE_RELIABILITY = {
    "district_hospital": 0.97,
    "phc_doctor":        0.95,
    "chc":               0.93,
    "anm":               0.88,
    "asha":              0.74,
    "aww":               0.71,
}

NUMERIC_FIELDS = [
    "hemoglobin", "weight_kg", "height_cm", "bmi",
    "sbp", "dbp", "fasting_glucose", "age_recorded",
]

CATEGORICAL_FIELDS = ["vacc_status", "is_pregnant"]

RECENCY_HALF_LIFE_DAYS = 90  # records older than this get down-weighted


def recency_weight(entry_date_str: str) -> float:
    """Exponential decay weight based on how recent the record is."""
    try:
        entry = date.fromisoformat(entry_date_str)
        age_days = (date.today() - entry).days
        return float(np.exp(-age_days / RECENCY_HALF_LIFE_DAYS))
    except Exception:
        return 0.5


class ConflictResolver:
    """
    Resolves conflicts across multiple source records for the same patient.

    Resolution strategies (per field):
        NUMERIC  → confidence-weighted mean (source reliability × recency)
        CATEGORICAL → weighted majority vote
        DATE     → most reliable source's value
    """

    def __init__(self, strategy: str = "weighted"):
        assert strategy in ("weighted", "most_reliable", "most_recent", "median")
        self.strategy = strategy

    def _weights(self, records: list[dict]) -> list[float]:
        weights = []
        for r in records:
            src_w = SOURCE_RELIABILITY.get(r.get("source", "asha"), 0.7)
            rec_w = recency_weight(r.get("entry_date", date.today().isoformat()))
            weights.append(src_w * rec_w)
        total = sum(weights) or 1.0
        return [w / total for w in weights]

    def resolve_numeric(self, field: str, records: list[dict]) -> dict[str, Any]:
        """Weighted mean of numeric field across non-null records."""
        valid = [(r, r[field]) for r in records if r.get(field) is not None]
        if not valid:
            return {"resolved_value": None, "resolution_method": "no_data", "n_sources": 0}

        if self.strategy == "most_reliable":
            best = max(valid, key=lambda rv: SOURCE_RELIABILITY.get(rv[0].get("source", "asha"), 0.7))
            return {"resolved_value": best[1], "resolution_method": "most_reliable", "n_sources": len(valid)}

        if self.strategy == "median":
            return {"resolved_value": median([v for _, v in valid]), "resolution_method": "median", "n_sources": len(valid)}

        if self.strategy == "most_recent":
            best = max(valid, key=lambda rv: rv[0].get("entry_date", "2000-01-01"))
            return {"resolved_value": best[1], "resolution_method": "most_recent", "n_sources": len(valid)}

        # Weighted mean
        weights = self._weights([r for r, _ in valid])
        resolved = sum(w * v for w, (_, v) in zip(weights, valid))
        return {
            "resolved_value": round(resolved, 2),
            "resolution_method": "weighted_mean",
            "n_sources": len(valid),
            "weight_distribution": {
                r.get("source", "unknown"): round(w, 3)
                for w, (r, _) in zip(weights, valid)
            },
        }

    def resolve_categorical(self, field: str, records: list[dict]) -> dict[str, Any]:
        """Weighted majority vote for categorical fields."""
        valid = [(r, r[field]) for r in records if r.get(field) is not None]
        if not valid:
            return {"resolved_value": None, "resolution_method": "no_data", "n_sources": 0}

        weights = self._weights([r for r, _ in valid])
        vote_scores: dict[str, float] = {}
        for w, (_, v) in zip(weights, valid):
            vote_scores[v] = vote_scores.get(v, 0.0) + w

        winner = max(vote_scores, key=vote_scores.get)
        confidence = vote_scores[winner] / sum(vote_scores.values())

        return {
            "resolved_value": winner,
            "resolution_method": "weighted_majority_vote",
            "n_sources": len(valid),
            "vote_scores": {k: round(v, 3) for k, v in vote_scores.items()},
            "confidence": round(confidence, 3),
        }

    def resolve_patient(self, patient_records: list[dict]) -> dict:
        """
        Produce a single reconciled record from all source records
        for one patient. Returns resolved values + audit trail.
        """
        if not patient_records:
            return {}

        patient_id = patient_records[0].get("patient_id")
        resolution = {
            "patient_id": patient_id,
            "n_sources": len(patient_records),
            "sources_used": list({r.get("source") for r in patient_records}),
            "fields": {},
        }

        for field in NUMERIC_FIELDS:
            resolution["fields"][field] = self.resolve_numeric(field, patient_records)

        for field in CATEGORICAL_FIELDS:
            resolution["fields"][field] = self.resolve_categorical(field, patient_records)

        # Date of resolution
        resolution["resolved_at"] = date.today().isoformat()
        resolution["strategy"] = self.strategy

        # Flag if any field had high disagreement
        disagreements = []
        for field, result in resolution["fields"].items():
            if field in NUMERIC_FIELDS and result.get("n_sources", 0) > 1:
                vals = [r[field] for r in patient_records if r.get(field) is not None]
                if len(vals) > 1 and (max(vals) - min(vals)) / (abs(np.mean(vals)) + 1e-6) > 0.3:
                    disagreements.append(field)

        resolution["high_disagreement_fields"] = disagreements
        resolution["requires_manual_review"] = len(disagreements) >= 2

        return resolution

    def resolve_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """Resolve all patients in a source records DataFrame."""
        results = []
        for pid, group in df.groupby("patient_id"):
            records = group.to_dict("records")
            resolved = self.resolve_patient(records)
            # Flatten for DataFrame output
            row = {"patient_id": pid}
            for field, info in resolved.get("fields", {}).items():
                row[f"{field}_resolved"] = info.get("resolved_value")
                row[f"{field}_method"] = info.get("resolution_method")
                row[f"{field}_n_sources"] = info.get("n_sources")
            row["requires_manual_review"] = resolved.get("requires_manual_review", False)
            row["high_disagreement_fields"] = str(resolved.get("high_disagreement_fields", []))
            results.append(row)
        return pd.DataFrame(results)
