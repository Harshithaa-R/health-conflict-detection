import pandas as pd
import numpy as np
import os


# ---------------------------------------------------
# BASE SOURCE RELIABILITY
# ---------------------------------------------------

BASE_RELIABILITY = {

    "PHC": 0.95,
    "ANM": 0.90,
    "ANGANWADI": 0.75,
    "ASHA": 0.70
}


# ---------------------------------------------------
# FIELD WEIGHTS
# ---------------------------------------------------

FIELD_IMPORTANCE = {

    "haemoglobin_gdl": 1.0,
    "systolic_bp": 1.0,
    "blood_sugar_fasting": 1.0,
    "weight_kg": 0.7,
    "fundal_height_cm": 0.7,
    "anc_visits_count": 0.6
}


def calculate_record_reliability(row):

    score = BASE_RELIABILITY.get(
        row["cadre"],
        0.5
    )

    # ---------------------------------------------------
    # MISSING VALUE PENALTY
    # ---------------------------------------------------

    important_fields = [

        "haemoglobin_gdl",
        "systolic_bp",
        "blood_sugar_fasting",
        "weight_kg",
        "fundal_height_cm"
    ]

    missing_count = 0

    for field in important_fields:

        if pd.isna(row[field]):

            missing_count += 1

    score -= (missing_count * 0.05)

    # ---------------------------------------------------
    # HIGH VARIANCE PENALTY
    # ---------------------------------------------------

    if row["cadre"] == "ASHA":

        score -= 0.05

    if row["cadre"] == "PHC":

        score += 0.02

    # ---------------------------------------------------
    # ANC COMPLETENESS BONUS
    # ---------------------------------------------------

    if row["anc_visits_count"] >= 4:

        score += 0.03

    # ---------------------------------------------------
    # NORMALIZE
    # ---------------------------------------------------

    score = max(
        0.1,
        min(0.99, score)
    )

    return round(score, 3)


def generate_reliability_scores():

    print(
        "Loading maternal records..."
    )

    df = pd.read_csv(
        "data/synthetic/maternal_records.csv"
    )

    df["source_reliability"] = df.apply(
        calculate_record_reliability,
        axis=1
    )

    os.makedirs(
        "data/processed",
        exist_ok=True
    )

    df.to_csv(
        "data/processed/reliability_scored_records.csv",
        index=False
    )

    # ---------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------

    print("\nReliability Summary")
    print("=" * 50)

    print(
        df.groupby("cadre")[
            "source_reliability"
        ].mean()
    )

    print("\nOverall Average")

    print(
        round(
            df["source_reliability"].mean(),
            3
        )
    )

    print(
        "\nSaved:"
        " data/processed/reliability_scored_records.csv"
    )

    return df


if __name__ == "__main__":

    generate_reliability_scores()