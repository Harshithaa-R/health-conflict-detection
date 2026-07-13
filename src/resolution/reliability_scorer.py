import pandas as pd
import numpy as np
import os


# ---------------------------------------------------
# BASE SOURCE RELIABILITY
# Same cadre hierarchy applies across all domains —
# PHC has lab access, ASHA has community-level accuracy
# ---------------------------------------------------

BASE_RELIABILITY = {
    "PHC":       0.95,
    "ANM":       0.90,
    "ANGANWADI": 0.75,
    "ASHA":      0.70,
}


# ---------------------------------------------------
# IMPORTANT FIELDS PER DOMAIN
# Missing values in these fields penalise reliability
# ---------------------------------------------------

IMPORTANT_FIELDS = {

    "maternal": [
        "haemoglobin_gdl",
        "systolic_bp",
        "blood_sugar_fasting",
        "weight_kg",
        "fundal_height_cm",
    ],

    "child": [
        "weight_child_kg",
        "height_cm",
        "muac_cm",
        "haemoglobin_child",
    ],

    "chronic": [
        "fasting_blood_sugar",
        "bp_systolic_reading1",
        "hba1c",
        "creatinine",
    ],
}


def calculate_record_reliability(row):

    cadre  = str(row.get("cadre", "ASHA")).upper()
    domain = str(row.get("domain", "maternal")).lower()

    score = BASE_RELIABILITY.get(cadre, 0.5)

    # ---------------------------------------------------
    # MISSING VALUE PENALTY
    # -0.05 per missing important field for this domain
    # ---------------------------------------------------

    fields = IMPORTANT_FIELDS.get(domain, IMPORTANT_FIELDS["maternal"])

    missing_count = sum(
        1 for f in fields
        if f in row.index and pd.isna(row[f])
    )

    score -= missing_count * 0.05

    # ---------------------------------------------------
    # CADRE-LEVEL VARIANCE ADJUSTMENTS
    # ---------------------------------------------------

    if cadre == "ASHA":
        score -= 0.05   # higher noise in community recordings

    if cadre == "PHC":
        score += 0.02   # lab-verified, most accurate

    # ---------------------------------------------------
    # DOMAIN-SPECIFIC BONUSES
    # ---------------------------------------------------

    if domain == "maternal":
        # ANC completeness bonus
        anc = row.get("anc_visits_count", None)
        if pd.notna(anc) and anc >= 4:
            score += 0.03

    elif domain == "child":
        # Anganwadi is strong for under-6 nutrition data
        if cadre == "ANGANWADI":
            age_months = row.get("child_age_months", 999)
            if pd.notna(age_months) and age_months <= 72:
                score += 0.03

    elif domain == "chronic":
        # PHC bonus for lab fields (HbA1c, creatinine, GeneXpert)
        if cadre == "PHC":
            score += 0.02

        # ASHA stronger penalty for chronic — mostly adherence tracking
        if cadre == "ASHA":
            score -= 0.03

    # ---------------------------------------------------
    # NORMALISE
    # ---------------------------------------------------

    score = max(0.10, min(0.99, score))

    return round(score, 3)


def generate_reliability_scores():

    print("Loading standardized records...")

    # Prefer standardized (processed) over raw synthetic
    std_path = "data/processed/standardized_records.csv"
    raw_path = "data/synthetic/unified_health_records.csv"
    mat_path = "data/synthetic/maternal_records.csv"

    if os.path.exists(std_path):
        df = pd.read_csv(std_path, low_memory=False)
    elif os.path.exists(raw_path):
        df = pd.read_csv(raw_path, low_memory=False)
    else:
        print("Falling back to maternal_records.csv...")
        df = pd.read_csv(mat_path, low_memory=False)

    if "domain" not in df.columns:
        df["domain"] = "maternal"

    if "cadre" in df.columns:
        df["cadre"] = df["cadre"].astype(str).str.upper().str.strip()

    df["source_reliability"] = df.apply(
        calculate_record_reliability,
        axis=1
    )

    os.makedirs("data/processed", exist_ok=True)

    df.to_csv(
        "data/processed/reliability_scored_records.csv",
        index=False
    )

    # ---------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------

    print("\nReliability Summary")
    print("=" * 50)

    print("\nBy Cadre (all domains):")
    print(
        df.groupby("cadre")["source_reliability"]
        .mean()
        .round(4)
        .to_string()
    )

    if "domain" in df.columns:
        print("\nBy Domain + Cadre:")
        summary = (
            df.groupby(["domain", "cadre"])["source_reliability"]
            .mean()
            .round(4)
        )
        print(summary.to_string())

    print(
        f"\nOverall Average : "
        f"{round(df['source_reliability'].mean(), 4)}"
    )

    print(
        "\nSaved: data/processed/reliability_scored_records.csv"
    )

    return df


if __name__ == "__main__":

    generate_reliability_scores()