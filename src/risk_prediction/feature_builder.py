import pandas as pd
import numpy as np
import os


def build_features():

    print(
        "Loading resolved maternal records..."
    )

    df = pd.read_csv(
        "data/processed/resolved_maternal_records.csv"
    )

    # ---------------------------------------------------
    # HIGH RISK FEATURES
    # ---------------------------------------------------

    df["severe_anaemia"] = np.where(
        df["haemoglobin_gdl"] < 9,
        1,
        0
    )

    df["hypertension_risk"] = np.where(
        df["systolic_bp"] >= 140,
        1,
        0
    )

    df["diabetes_risk"] = np.where(
        df["blood_sugar_fasting"] >= 140,
        1,
        0
    )

    df["low_weight_risk"] = np.where(
        df["weight_kg"] < 45,
        1,
        0
    )

    df["fundal_height_risk"] = np.where(
        (
            df["fundal_height_cm"] < 20
        )
        |
        (
            df["fundal_height_cm"] > 38
        ),
        1,
        0
    )

    df["poor_anc_coverage"] = np.where(
        df["anc_visits_count"] < 2,
        1,
        0
    )

    # ---------------------------------------------------
    # COMPOSITE RISK SCORE
    # ---------------------------------------------------

    df["maternal_risk_score"] = (

        (df["severe_anaemia"] * 3)
        +
        (df["hypertension_risk"] * 3)
        +
        (df["diabetes_risk"] * 3)
        +
        (df["low_weight_risk"] * 2)
        +
        (df["fundal_height_risk"] * 2)
        +
        (df["poor_anc_coverage"] * 2)

    )

    # ---------------------------------------------------
    # FINAL RISK LABEL
    # ---------------------------------------------------

    df["predicted_high_risk"] = np.where(
        df["maternal_risk_score"] >= 3,
        1,
        0
    )

    os.makedirs(
        "data/processed",
        exist_ok=True
    )

    df.to_csv(
        "data/processed/final_features.csv",
        index=False
    )

    # ---------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------

    print("\nFeature Engineering Summary")
    print("=" * 50)

    print(
        f"Total Patients : "
        f"{len(df):,}"
    )

    print(
        "\nPredicted High Risk Cases"
    )

    print(
        df["predicted_high_risk"]
        .value_counts()
    )

    print(
        "\nAverage Risk Score"
    )

    print(
        round(
            df["maternal_risk_score"].mean(),
            2
        )
    )

    print(
        "\nSaved:"
        " data/processed/final_features.csv"
    )

    return df


if __name__ == "__main__":

    build_features()