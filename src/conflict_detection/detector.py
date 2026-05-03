"""
src/conflict_detection/detector.py
====================================
ML-based conflict detector for multi-source health records.

Uses a hybrid of rule-based constraints and XGBoost classifier
to flag records with conflicts and classify the conflict type.
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.preprocessing import LabelEncoder
import joblib
import logging

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Medical domain constraints (hard rules)
# ──────────────────────────────────────────────────────────────────────────────

PHYSIOLOGICAL_CONSTRAINTS = {
    "hemoglobin":      (3.0, 20.0),
    "sbp":             (70, 230),
    "dbp":             (40, 140),
    "weight_kg":       (20.0, 200.0),
    "height_cm":       (100.0, 210.0),
    "bmi":             (10.0, 70.0),
    "fasting_glucose": (40.0, 600.0),
    "age_recorded":    (0, 100),
}

CROSS_FIELD_RULES = [
    # (condition_fn, conflict_label)
    (lambda r: r["dbp"] >= r["sbp"],                    "dbp_exceeds_sbp"),
    (lambda r: r["bmi"] > 0 and abs(
        r["weight_kg"] / ((r["height_cm"]/100)**2) - r["bmi"]
    ) > 3.0,                                            "bmi_height_weight_inconsistent"),
    (lambda r: not r["is_pregnant"] and r["anc_visits"] > 0, "anc_without_pregnancy"),
    (lambda r: r["hemoglobin"] < 5.0 and not r.get("hospitalised", False),
                                                        "severe_anaemia_unflagged"),
]


class RuleBasedDetector:
    """Fast rule engine for physiologically impossible values."""

    def check(self, record: dict) -> list[dict]:
        flags = []

        # Hard physiological bounds
        for field, (lo, hi) in PHYSIOLOGICAL_CONSTRAINTS.items():
            val = record.get(field)
            if val is not None and not (lo <= val <= hi):
                flags.append({
                    "field": field,
                    "value": val,
                    "rule": "physiological_bound",
                    "conflict_type": "physiological_impossibility",
                    "severity": "high",
                })

        # Cross-field logical rules
        for rule_fn, label in CROSS_FIELD_RULES:
            try:
                if rule_fn(record):
                    flags.append({
                        "field": "multi_field",
                        "rule": label,
                        "conflict_type": "cross_field_contradiction",
                        "severity": "medium",
                    })
            except (KeyError, TypeError, ZeroDivisionError):
                pass

        return flags

    def check_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        results = []
        for _, row in df.iterrows():
            flags = self.check(row.to_dict())
            results.append({
                "record_id": row.get("record_id"),
                "rule_flags": flags,
                "rule_conflict_detected": len(flags) > 0,
                "rule_conflict_count": len(flags),
            })
        return pd.DataFrame(results)


# ──────────────────────────────────────────────────────────────────────────────
# ML-based conflict detector
# ──────────────────────────────────────────────────────────────────────────────

class ConflictDetector(BaseEstimator, ClassifierMixin):
    """
    Hybrid conflict detection model.

    Stage 1: Rule engine catches hard physiological violations.
    Stage 2: XGBoost classifies soft/contextual conflicts.
    Stage 3: Source reliability weighting adjusts confidence.
    """

    FEATURE_COLS = [
        "age_recorded", "height_cm", "weight_kg", "bmi",
        "hemoglobin", "sbp", "dbp", "fasting_glucose",
        "anc_visits", "source_reliability",
        # Derived features (computed in feature_engineering)
        "bmi_calc_delta", "hb_z_score", "sbp_z_score",
        "pulse_pressure", "age_source_delta",
    ]

    CONFLICT_TYPES = [
        "numeric_outlier", "categorical_mismatch", "temporal_inconsistency",
        "demographic_drift", "physiological_impossibility",
        "cross_field_contradiction", "no_conflict",
    ]

    def __init__(self, model=None):
        self.model = model
        self.label_encoder = LabelEncoder()
        self.rule_detector = RuleBasedDetector()
        self._is_fitted = False

    def feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute derived features for ML stage."""
        df = df.copy()

        # BMI recalculated from height/weight vs stored BMI
        df["bmi_calc"] = df["weight_kg"] / ((df["height_cm"] / 100) ** 2)
        df["bmi_calc_delta"] = abs(df["bmi_calc"] - df["bmi"])

        # Z-score relative to Karnataka NFHS-5 population norms
        df["hb_z_score"] = (df["hemoglobin"] - 11.8) / 2.1
        df["sbp_z_score"] = (df["sbp"] - 115.0) / 16.0

        # Pulse pressure (SBP - DBP)
        df["pulse_pressure"] = df["sbp"] - df["dbp"]

        # Age delta (placeholder; computed cross-source in pipeline)
        if "age_source_delta" not in df.columns:
            df["age_source_delta"] = 0.0

        return df

    def fit(self, X: pd.DataFrame, y: pd.Series):
        """Train the XGBoost conflict classifier."""
        try:
            from xgboost import XGBClassifier
        except ImportError:
            from sklearn.ensemble import GradientBoostingClassifier as XGBClassifier
            logger.warning("XGBoost not installed; falling back to sklearn GBM.")

        X_feat = self.feature_engineering(X)
        available = [c for c in self.FEATURE_COLS if c in X_feat.columns]
        X_ml = X_feat[available].fillna(0)

        y_enc = self.label_encoder.fit_transform(y)

        self.model = XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            use_label_encoder=False,
            eval_metric="mlogloss",
            random_state=42,
        )
        self.model.fit(X_ml, y_enc)
        self._is_fitted = True
        logger.info(f"ConflictDetector trained on {len(X)} records.")
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict conflict type for each record."""
        if not self._is_fitted:
            raise RuntimeError("Model not fitted. Call fit() first.")
        X_feat = self.feature_engineering(X)
        available = [c for c in self.FEATURE_COLS if c in X_feat.columns]
        X_ml = X_feat[available].fillna(0)
        y_enc = self.model.predict(X_ml)
        return self.label_encoder.inverse_transform(y_enc)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        X_feat = self.feature_engineering(X)
        available = [c for c in self.FEATURE_COLS if c in X_feat.columns]
        X_ml = X_feat[available].fillna(0)
        return self.model.predict_proba(X_ml)

    def detect(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Full hybrid detection pipeline.
        Returns original DataFrame with conflict annotations added.
        """
        results = df.copy()

        # Stage 1: Rule-based
        rule_results = self.rule_detector.check_batch(df)
        results = results.merge(rule_results[["record_id", "rule_conflict_detected", "rule_conflict_count"]],
                                on="record_id", how="left")

        # Stage 2: ML-based (if fitted)
        if self._is_fitted:
            results["ml_conflict_type"] = self.predict(df)
            results["ml_conflict_proba"] = self.predict_proba(df).max(axis=1)
        else:
            results["ml_conflict_type"] = "unknown"
            results["ml_conflict_proba"] = 0.0

        # Stage 3: Combined flag
        results["conflict_detected"] = (
            results["rule_conflict_detected"] |
            (results["ml_conflict_type"] != "no_conflict")
        )

        # Confidence weighted by source reliability
        if "source_reliability" in results.columns:
            results["adjusted_confidence"] = (
                results["ml_conflict_proba"] * (1 - results["source_reliability"] * 0.3)
            )

        return results

    def save(self, path: str):
        joblib.dump(self, path)
        logger.info(f"Model saved to {path}")

    @classmethod
    def load(cls, path: str) -> "ConflictDetector":
        model = joblib.load(path)
        logger.info(f"Model loaded from {path}")
        return model
