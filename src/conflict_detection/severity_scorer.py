import pandas as pd
import numpy as np
import os


# ---------------------------------------------------
# SEVERITY WEIGHTS — clinical significance
# ---------------------------------------------------

MEASUREMENT_WEIGHTS = {
    # Maternal
    "haemoglobin_conflict":         3.0,
    "blood_pressure_conflict":      3.0,
    "blood_sugar_conflict":         3.0,
    "anc_visit_conflict":           2.0,
    "weight_conflict":              1.5,
    "fundal_height_conflict":       1.5,
    # Child
    "child_weight_conflict":        2.0,
    "child_height_conflict":        1.5,
    "muac_conflict":                3.0,
    "waz_conflict":                 2.5,
    "haz_conflict":                 2.0,
    "child_haemoglobin_conflict":   2.5,
    # Immunization
    "immunization_conflict_bcg_given":         2.0,
    "immunization_conflict_opv0_given":        1.5,
    "immunization_conflict_opv1_given":        1.5,
    "immunization_conflict_opv2_given":        1.5,
    "immunization_conflict_opv3_given":        1.5,
    "immunization_conflict_dpt1_given":        2.0,
    "immunization_conflict_dpt2_given":        2.0,
    "immunization_conflict_dpt3_given":        2.0,
    "immunization_conflict_measles_given":     2.0,
    "immunization_conflict_mmr_given":         1.5,
    "immunization_conflict_hepatitis_b_given": 2.0,
    "immunization_conflict_pentavalent_given": 2.0,
    # Chronic
    "fasting_glucose_conflict":     3.0,
    "postprandial_glucose_conflict":2.5,
    "hba1c_conflict":               3.0,
    "bp_systolic_conflict":         3.0,
    "bp_diastolic_conflict":        2.5,
    "missed_doses_conflict":        3.0,
    "creatinine_conflict":          2.5,
    "bmi_conflict":                 1.5,
}

IDENTITY_WEIGHTS = {
    "name_conflict":   2.0,
    "age_conflict":    2.5,
    "gender_conflict": 3.0,
}

TEMPORAL_WEIGHTS = {
    "visit_date_conflict":       1.5,
    "edd_conflict":              2.0,
    "lmp_conflict":              2.0,
    "stale_record_conflict":     1.0,
    "gestational_age_conflict":  2.5,
}

SEVERITY_TIERS = {
    "critical": (8.0, float("inf")),
    "high":     (5.0, 8.0),
    "medium":   (2.5, 5.0),
    "low":      (0.1, 2.5),
    "none":     (0.0, 0.1),
}


def parse_score(raw: str, weight_map: dict) -> float:
    if not raw or raw in (
        "no_conflict", "no_identity_conflict", "no_temporal_conflict"
    ):
        return 0.0
    score = 0.0
    for conflict in str(raw).split(","):
        conflict = conflict.strip()
        # immunization conflicts use prefix match
        matched = weight_map.get(conflict, None)
        if matched is None:
            for key in weight_map:
                if conflict.startswith(key) or key.startswith(conflict):
                    matched = weight_map[key]
                    break
        score += matched if matched is not None else 1.0
    return score


def get_tier(score: float) -> str:
    for tier, (lo, hi) in SEVERITY_TIERS.items():
        if lo <= score < hi:
            return tier
    return "none"


def score_severity():

    print("Loading conflict datasets...")

    # Measurement conflicts — required
    measurement = pd.read_csv(
        "data/processed/measurement_conflicts.csv",
        low_memory=False
    )

    # Identity conflicts — optional
    try:
        identity = pd.read_csv("data/processed/identity_conflicts.csv")
    except FileNotFoundError:
        print("  identity_conflicts.csv not found — skipping")
        identity = None

    # Temporal conflicts — optional
    try:
        temporal = pd.read_csv("data/processed/temporal_conflicts.csv")
    except FileNotFoundError:
        print("  temporal_conflicts.csv not found — skipping")
        temporal = None

    df = measurement[[
        "patient_id", "domain", "name", "district", "village",
        "num_conflicts", "conflict_types", "has_conflict"
    ]].copy()

    # Merge identity
    if identity is not None:
        df = df.merge(
            identity[["patient_id", "identity_conflict_types", "has_identity_conflict"]],
            on="patient_id", how="left"
        )
    else:
        df["identity_conflict_types"] = "no_identity_conflict"
        df["has_identity_conflict"]   = False

    # Merge temporal
    if temporal is not None:
        df = df.merge(
            temporal[["patient_id", "temporal_conflict_types", "has_temporal_conflict"]],
            on="patient_id", how="left"
        )
    else:
        df["temporal_conflict_types"] = "no_temporal_conflict"
        df["has_temporal_conflict"]   = False

    df["identity_conflict_types"]  = df["identity_conflict_types"].fillna("no_identity_conflict")
    df["temporal_conflict_types"]  = df["temporal_conflict_types"].fillna("no_temporal_conflict")
    df["has_identity_conflict"]    = df["has_identity_conflict"].fillna(False)
    df["has_temporal_conflict"]    = df["has_temporal_conflict"].fillna(False)

    # Compute scores
    df["measurement_severity"] = df["conflict_types"].apply(
        lambda x: parse_score(x, MEASUREMENT_WEIGHTS)
    )
    df["identity_severity"] = df["identity_conflict_types"].apply(
        lambda x: parse_score(x, IDENTITY_WEIGHTS)
    )
    df["temporal_severity"] = df["temporal_conflict_types"].apply(
        lambda x: parse_score(x, TEMPORAL_WEIGHTS)
    )

    df["total_severity_score"] = (
        df["measurement_severity"] +
        df["identity_severity"]    +
        df["temporal_severity"]
    ).round(2)

    df["severity_tier"] = df["total_severity_score"].apply(get_tier)

    df["has_any_conflict"] = (
        df["has_conflict"] |
        df["has_identity_conflict"] |
        df["has_temporal_conflict"]
    )

    os.makedirs("data/processed", exist_ok=True)

    df.to_csv(
        "data/processed/severity_scored_conflicts.csv",
        index=False
    )

    print("\nSeverity Scoring Summary")
    print("=" * 50)

    total    = len(df)
    with_any = int(df["has_any_conflict"].sum())

    print(f"Total Patients     : {total:,}")
    print(f"With Any Conflict  : {with_any:,}  ({with_any/total*100:.1f}%)")

    print("\nSeverity Tier Distribution:")
    for tier in ["critical", "high", "medium", "low", "none"]:
        count = int((df["severity_tier"] == tier).sum())
        print(f"  {tier.upper():<10}: {count:>5,}  ({count/total*100:.1f}%)")

    print(f"\nAvg Severity Score : {df['total_severity_score'].mean():.2f}")
    print(f"Max Severity Score : {df['total_severity_score'].max():.2f}")

    print("\nBy Domain:")
    for domain in ["maternal", "child", "chronic"]:
        d = df[df["domain"] == domain]
        if len(d) == 0:
            continue
        wc  = int(d["has_any_conflict"].sum())
        avg = d["total_severity_score"].mean()
        print(f"  {domain:<10}: {wc:,} / {len(d):,} with conflicts  |  avg score {avg:.2f}")

    print("\nSaved: data/processed/severity_scored_conflicts.csv")

    return df


if __name__ == "__main__":

    score_severity()