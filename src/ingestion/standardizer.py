import pandas as pd
import os


def standardize_records():

    print("Loading source datasets...")

    asha = pd.read_csv(
        "data/synthetic/asha_maternal.csv"
    )

    anm = pd.read_csv(
        "data/synthetic/anm_maternal.csv"
    )

    phc = pd.read_csv(
        "data/synthetic/phc_maternal.csv"
    )

    anganwadi = pd.read_csv(
        "data/synthetic/anganwadi_maternal.csv"
    )

    datasets = [
        asha,
        anm,
        phc,
        anganwadi
    ]

    standardized = []

    for df in datasets:

        df.columns = (
            df.columns
            .str.lower()
            .str.strip()
        )

        df["name"] = (
            df["name"]
            .astype(str)
            .str.strip()
            .str.title()
        )

        df["district"] = (
            df["district"]
            .astype(str)
            .str.strip()
            .str.title()
        )

        df["village"] = (
            df["village"]
            .astype(str)
            .str.strip()
            .str.title()
        )

        numeric_cols = [

            "age",

            "haemoglobin_gdl",

            "systolic_bp",
            "diastolic_bp",

            "blood_sugar_fasting",

            "weight_kg",

            "fundal_height_cm",

            "anc_visits_count"
        ]

        for col in numeric_cols:

            if col in df.columns:

                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                )

        standardized.append(df)

    merged_df = pd.concat(
        standardized,
        ignore_index=True
    )

    os.makedirs(
        "data/processed",
        exist_ok=True
    )

    merged_df.to_csv(
        "data/processed/standardized_records.csv",
        index=False
    )

    print("\nStandardization Complete")
    print("=" * 50)

    print(
        f"Total Records : {len(merged_df):,}"
    )

    print(
        f"Unique Patients : "
        f"{merged_df['patient_id'].nunique():,}"
    )

    print("\nCadre Distribution")

    print(
        merged_df["cadre"]
        .value_counts()
    )

    print(
        "\nSaved: "
        "data/processed/standardized_records.csv"
    )

    return merged_df


if __name__ == "__main__":

    standardize_records()