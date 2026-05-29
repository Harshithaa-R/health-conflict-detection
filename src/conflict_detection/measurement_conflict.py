import pandas as pd
import numpy as np
import os


# ---------------------------------------------------
# THRESHOLDS
# ---------------------------------------------------

HB_THRESHOLD = 1.0
BP_THRESHOLD = 10
GLUCOSE_THRESHOLD = 15
ANC_THRESHOLD = 1
WEIGHT_THRESHOLD = 3
FUNDAL_HEIGHT_THRESHOLD = 3


def detect_measurement_conflicts():

    print("Loading linked maternal records...")

    df = pd.read_csv(
        "data/processed/linked_records.csv"
    )

    conflicts = []

    grouped = df.groupby(
        "unified_patient_id"
    )

    total_conflicts = 0
    multi_conflict_cases = 0

    for uid, group in grouped:

        patient_conflicts = []

        # ---------------------------------------------------
        # HEMOGLOBIN CONFLICT
        # ---------------------------------------------------

        hb_values = (
            group["haemoglobin_gdl"]
            .dropna()
            .tolist()
        )

        if (
            len(hb_values) > 1
            and
            (
                max(hb_values)
                -
                min(hb_values)
            ) >= HB_THRESHOLD
        ):

            patient_conflicts.append(
                "haemoglobin_conflict"
            )

        # ---------------------------------------------------
        # BP CONFLICT
        # ---------------------------------------------------

        bp_values = (
            group["systolic_bp"]
            .dropna()
            .tolist()
        )

        if (
            len(bp_values) > 1
            and
            (
                max(bp_values)
                -
                min(bp_values)
            ) >= BP_THRESHOLD
        ):

            patient_conflicts.append(
                "blood_pressure_conflict"
            )

        # ---------------------------------------------------
        # GLUCOSE CONFLICT
        # ---------------------------------------------------

        glucose_values = (
            group["blood_sugar_fasting"]
            .dropna()
            .tolist()
        )

        if (
            len(glucose_values) > 1
            and
            (
                max(glucose_values)
                -
                min(glucose_values)
            ) >= GLUCOSE_THRESHOLD
        ):

            patient_conflicts.append(
                "blood_sugar_conflict"
            )

        # ---------------------------------------------------
        # ANC VISIT CONFLICT
        # ---------------------------------------------------

        anc_values = (
            group["anc_visits_count"]
            .dropna()
            .tolist()
        )

        if (
            len(anc_values) > 1
            and
            (
                max(anc_values)
                -
                min(anc_values)
            ) >= ANC_THRESHOLD
        ):

            patient_conflicts.append(
                "anc_visit_conflict"
            )

        # ---------------------------------------------------
        # WEIGHT CONFLICT
        # ---------------------------------------------------

        weight_values = (
            group["weight_kg"]
            .dropna()
            .tolist()
        )

        if (
            len(weight_values) > 1
            and
            (
                max(weight_values)
                -
                min(weight_values)
            ) >= WEIGHT_THRESHOLD
        ):

            patient_conflicts.append(
                "weight_conflict"
            )

        # ---------------------------------------------------
        # FUNDAL HEIGHT CONFLICT
        # ---------------------------------------------------

        fh_values = (
            group["fundal_height_cm"]
            .dropna()
            .tolist()
        )

        if (
            len(fh_values) > 1
            and
            (
                max(fh_values)
                -
                min(fh_values)
            ) >= FUNDAL_HEIGHT_THRESHOLD
        ):

            patient_conflicts.append(
                "fundal_height_conflict"
            )

        # ---------------------------------------------------
        # FINAL OUTPUT
        # ---------------------------------------------------

        if len(patient_conflicts) > 0:

            total_conflicts += 1

        if len(patient_conflicts) > 1:

            multi_conflict_cases += 1

        conflicts.append({

            "unified_patient_id":
                uid,

            "patient_id":
                group.iloc[0]["patient_id"],

            "name":
                group.iloc[0]["name"],

            "district":
                group.iloc[0]["district"],

            "village":
                group.iloc[0]["village"],

            "num_conflicts":
                len(patient_conflicts),

            "conflict_types":
                (
                    ",".join(patient_conflicts)
                    if patient_conflicts
                    else "no_conflict"
                ),

            "has_conflict":
                (
                    len(patient_conflicts) > 0
                )
        })

    conflicts_df = pd.DataFrame(
        conflicts
    )

    os.makedirs(
        "data/processed",
        exist_ok=True
    )

    conflicts_df.to_csv(
        "data/processed/measurement_conflicts.csv",
        index=False
    )

    print("\nMeasurement Conflict Summary")
    print("=" * 50)

    print(
        f"Patients Analysed : "
        f"{len(conflicts_df):,}"
    )

    print(
        f"Patients With Conflicts : "
        f"{total_conflicts:,}"
    )

    print(
        f"Patients With Multiple Conflicts : "
        f"{multi_conflict_cases:,}"
    )

    print("\nConflict Distribution")

    print(
        conflicts_df["conflict_types"]
        .value_counts()
        .head(15)
    )

    print(
        "\nSaved:"
        " data/processed/measurement_conflicts.csv"
    )

    return conflicts_df


if __name__ == "__main__":

    detect_measurement_conflicts()