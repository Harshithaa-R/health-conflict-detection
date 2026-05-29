import pandas as pd
import numpy as np
import os

FIELDS = [
    "haemoglobin_gdl",
    "systolic_bp",
    "blood_sugar_fasting",
    "weight_kg",
    "fundal_height_cm",
    "anc_visits_count"
]


MAX_ITERATIONS = 20
CONVERGENCE_THRESHOLD = 0.0001


def run_em(group, field):

    data = group[
        ["cadre", field]
    ].dropna()

    if len(data) == 0:
        return np.nan

    # ---------------------------------------
    # INITIAL SOURCE RELIABILITY
    # ---------------------------------------

    reliabilities = {
        source: 0.8
        for source in data["cadre"].unique()
    }

    truth = data[field].mean()

    # ---------------------------------------
    # EM ITERATIONS
    # ---------------------------------------

    for _ in range(MAX_ITERATIONS):

        old_truth = truth

        # ==============================
        # E STEP
        # ==============================

        numerator = 0
        denominator = 0

        for _, row in data.iterrows():

            source = row["cadre"]
            value = row[field]

            weight = reliabilities[source]

            numerator += value * weight
            denominator += weight

        truth = numerator / denominator

        # ==============================
        # M STEP
        # ==============================

        for source in reliabilities:

            source_rows = data[
                data["cadre"] == source
            ]

            errors = []

            for _, row in source_rows.iterrows():

                error = abs(
                    row[field] - truth
                )

                errors.append(error)

            mean_error = np.mean(errors)

            reliability = (
                1 /
                (1 + mean_error)
            )

            reliabilities[source] = reliability

        # ==============================
        # CONVERGENCE
        # ==============================

        if abs(truth - old_truth) < CONVERGENCE_THRESHOLD:
            break

    return round(truth, 2)


def resolve_conflicts():

    print(
        "Loading reliability scored records..."
    )

    df = pd.read_csv(
        "data/processed/reliability_scored_records.csv"
    )

    grouped = df.groupby(
        "patient_id"
    )

    resolved_records = []

    for patient_id, group in grouped:

        resolved = {

            "patient_id":
                patient_id,

            "district":
                group.iloc[0]["district"],

            "village":
                group.iloc[0]["village"],

            "true_high_risk":
                group.iloc[0]["true_high_risk"],

            "true_high_risk_reason":
                group.iloc[0]["true_high_risk_reason"]
        }

        for field in FIELDS:

            resolved[field] = run_em(
                group,
                field
            )

        resolved["sources_used"] = len(group)

        resolved_records.append(
            resolved
        )

    resolved_df = pd.DataFrame(
        resolved_records
    )

    os.makedirs(
        "data/processed",
        exist_ok=True
    )

    resolved_df.to_csv(
        "data/processed/resolved_maternal_records.csv",
        index=False
    )

    print("\nBayesian EM Summary")
    print("=" * 50)

    print(
        f"Resolved Patients : "
        f"{len(resolved_df):,}"
    )

    print(
        f"Average Hb : "
        f"{round(resolved_df['haemoglobin_gdl'].mean(), 2)}"
    )

    print(
        f"Average BP : "
        f"{round(resolved_df['systolic_bp'].mean(), 2)}"
    )

    print(
        f"Average Glucose : "
        f"{round(resolved_df['blood_sugar_fasting'].mean(), 2)}"
    )

    print(
        "\nSaved:"
        " data/processed/resolved_maternal_records.csv"
    )

    return resolved_df


if __name__ == "__main__":
    resolve_conflicts()