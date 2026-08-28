import pandas as pd
import os


# ===================================================
# RELIABILITY CONFIGURATION
# ===================================================

BASE_RELIABILITY = {
    "PHC": 0.95,
    "ANM": 0.90,
    "ANGANWADI": 0.75,
    "ASHA": 0.70,
}

# Penalty applied for each missing important field
MISSING_FIELD_PENALTY = 0.05

# Cadre-specific adjustments
CADRE_ADJUSTMENTS = {
    "ASHA": -0.05,
    "PHC": 0.02,
}

# Domain-specific adjustments
DOMAIN_ADJUSTMENTS = {
    "maternal": {
        "ANC_COMPLETENESS": 0.03,
    },
    "child": {
        "ANGANWADI_CHILD": 0.03,
    },
    "chronic": {
        "PHC_LAB": 0.02,
        "ASHA_CHRONIC": -0.03,
    },
}

# Reliability score limits
MIN_RELIABILITY = 0.10
MAX_RELIABILITY = 0.99


# ===================================================
# IMPORTANT FIELDS PER DOMAIN
# ===================================================

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


# ===================================================
# RELIABILITY CALCULATION
# ===================================================

def calculate_record_reliability(row):

    cadre = str(
        row.get("cadre", "ASHA")
    ).upper()

    domain = str(
        row.get("domain", "maternal")
    ).lower()

    # ---------------------------------------------------
    # Base reliability
    # ---------------------------------------------------

    score = BASE_RELIABILITY.get(
        cadre,
        0.50
    )

    # ---------------------------------------------------
    # Missing important fields
    # ---------------------------------------------------

    fields = IMPORTANT_FIELDS.get(
        domain,
        IMPORTANT_FIELDS["maternal"]
    )

    missing_count = sum(
        1
        for field in fields
        if field in row.index
        and pd.isna(row[field])
    )

    score -= (
        missing_count
        * MISSING_FIELD_PENALTY
    )

    # ---------------------------------------------------
    # Cadre adjustment
    # ---------------------------------------------------

    score += CADRE_ADJUSTMENTS.get(
        cadre,
        0.0
    )

    # ---------------------------------------------------
    # Domain-specific adjustments
    # ---------------------------------------------------

    if domain == "maternal":

        anc = row.get(
            "anc_visits_count",
            None
        )

        if (
            pd.notna(anc)
            and anc >= 4
        ):
            score += DOMAIN_ADJUSTMENTS[
                "maternal"
            ]["ANC_COMPLETENESS"]

    elif domain == "child":

        if cadre == "ANGANWADI":

            age_months = row.get(
                "child_age_months",
                999
            )

            if (
                pd.notna(age_months)
                and age_months <= 72
            ):
                score += DOMAIN_ADJUSTMENTS[
                    "child"
                ]["ANGANWADI_CHILD"]

    elif domain == "chronic":

        if cadre == "PHC":
            score += DOMAIN_ADJUSTMENTS[
                "chronic"
            ]["PHC_LAB"]

        if cadre == "ASHA":
            score += DOMAIN_ADJUSTMENTS[
                "chronic"
            ]["ASHA_CHRONIC"]

    # ---------------------------------------------------
    # Clip reliability to configured range
    # ---------------------------------------------------

    score = max(
        MIN_RELIABILITY,
        min(
            MAX_RELIABILITY,
            score
        )
    )

    return round(
        score,
        3
    )


# ===================================================
# GENERATE RELIABILITY SCORES
# ===================================================

def generate_reliability_scores():

    print(
        "Loading standardized records..."
    )

    std_path = (
        "data/processed/"
        "standardized_records.csv"
    )

    raw_path = (
        "data/synthetic/"
        "unified_health_records.csv"
    )

    mat_path = (
        "data/synthetic/"
        "maternal_records.csv"
    )

    if os.path.exists(std_path):

        df = pd.read_csv(
            std_path,
            low_memory=False
        )

    elif os.path.exists(raw_path):

        df = pd.read_csv(
            raw_path,
            low_memory=False
        )

    else:

        print(
            "Falling back to "
            "maternal_records.csv..."
        )

        df = pd.read_csv(
            mat_path,
            low_memory=False
        )

    if "domain" not in df.columns:
        df["domain"] = "maternal"

    if "cadre" in df.columns:

        df["cadre"] = (
            df["cadre"]
            .astype(str)
            .str.upper()
            .str.strip()
        )

    df["source_reliability"] = df.apply(
        calculate_record_reliability,
        axis=1
    )

    os.makedirs(
        "data/processed",
        exist_ok=True
    )

    output_path = (
        "data/processed/"
        "reliability_scored_records.csv"
    )

    df.to_csv(
        output_path,
        index=False
    )

    # ---------------------------------------------------
    # Summary
    # ---------------------------------------------------

    print(
        "\nReliability Summary"
    )
    print("=" * 50)

    print(
        "\nBy Cadre (all domains):"
    )

    print(
        df.groupby("cadre")[
            "source_reliability"
        ]
        .mean()
        .round(4)
        .to_string()
    )

    print(
        "\nBy Domain + Cadre:"
    )

    summary = (
        df.groupby(
            ["domain", "cadre"]
        )[
            "source_reliability"
        ]
        .mean()
        .round(4)
    )

    print(
        summary.to_string()
    )

    print(
        f"\nOverall Average : "
        f"{df['source_reliability'].mean():.4f}"
    )

    print(
        f"\nSaved: {output_path}"
    )

    return df


# ===================================================
# MAIN
# ===================================================

if __name__ == "__main__":

    generate_reliability_scores()