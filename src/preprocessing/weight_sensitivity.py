import os
import sys

import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score


# ---------------------------------------------------
# Import actual entity-resolution scoring function
# ---------------------------------------------------

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from entity_resolution import normalize_name
from rapidfuzz import fuzz


# ---------------------------------------------------
# Weight configurations
# ---------------------------------------------------

WEIGHT_CONFIGS = {
    "W1_Current": {
        "name": 0.50,
        "age": 0.15,
        "village": 0.15,
        "gender": 0.10,
        "dob": 0.10
    },

    "W2_Name_Heavy": {
        "name": 0.60,
        "age": 0.10,
        "village": 0.10,
        "gender": 0.10,
        "dob": 0.10
    },

    "W3_Balanced": {
        "name": 0.40,
        "age": 0.20,
        "village": 0.15,
        "gender": 0.15,
        "dob": 0.10
    },

    "W4_Age_Heavy": {
        "name": 0.50,
        "age": 0.20,
        "village": 0.10,
        "gender": 0.10,
        "dob": 0.10
    }
}


THRESHOLD = 85

DATA_PATH = os.path.join(
    "data",
    "processed",
    "blocked_records.csv"
)


# ---------------------------------------------------
# Weight-aware composite score
# ---------------------------------------------------

def weighted_composite_score(
    row1,
    row2,
    weights
):

    # Never compare patients across domains
    if str(row1.get("domain", "")) != str(
        row2.get("domain", "")
    ):
        return 0.0

    # -----------------------------
    # Name
    # -----------------------------

    name_score = fuzz.token_sort_ratio(
        normalize_name(row1.get("name")),
        normalize_name(row2.get("name"))
    )

    # -----------------------------
    # Age
    # -----------------------------

    age1 = pd.to_numeric(
        row1.get("age"),
        errors="coerce"
    )

    age2 = pd.to_numeric(
        row2.get("age"),
        errors="coerce"
    )

    if pd.isna(age1) or pd.isna(age2):
        age_score = None
    else:
        age_diff = abs(age1 - age2)
        age_score = max(
            0,
            100 - (age_diff * 10)
        )

    # -----------------------------
    # Village
    # -----------------------------

    village1 = row1.get("village")
    village2 = row2.get("village")

    if pd.isna(village1) or pd.isna(village2):
        village_score = None
    else:
        village_score = (
            100
            if str(village1).strip().lower()
            == str(village2).strip().lower()
            else 0
        )

    # -----------------------------
    # Gender
    # -----------------------------

    gender1 = row1.get("gender")
    gender2 = row2.get("gender")

    if pd.isna(gender1) or pd.isna(gender2):
        gender_score = None
    else:
        gender_score = (
            100
            if str(gender1).strip().lower()
            == str(gender2).strip().lower()
            else 0
        )

    # -----------------------------
    # DOB
    # -----------------------------

    dob1 = row1.get("dob")
    dob2 = row2.get("dob")

    if pd.isna(dob1) or pd.isna(dob2):
        dob_score = None
    else:
        dob_score = (
            100
            if str(dob1).strip()
            == str(dob2).strip()
            else 0
        )

    components = [
        (weights["name"], name_score),
        (weights["age"], age_score),
        (weights["village"], village_score),
        (weights["gender"], gender_score),
        (weights["dob"], dob_score)
    ]

    # Ignore unavailable attributes
    available = [
        (weight, score)
        for weight, score in components
        if score is not None
    ]

    if not available:
        return 0.0

    # Normalize remaining weights
    total_weight = sum(
        weight
        for weight, _ in available
    )

    return sum(
        weight * score
        for weight, score in available
    ) / total_weight


# ---------------------------------------------------
# Run experiment
# ---------------------------------------------------

def run_weight_experiment():

    print("Loading blocked records...")

    df = pd.read_csv(
        DATA_PATH,
        low_memory=False
    )

    print(
        f"Records loaded: {len(df):,}"
    )

    results = []

    group_cols = [
        "domain",
        "district",
        "village"
    ]

    grouped = df.groupby(group_cols)

    for config_name, weights in WEIGHT_CONFIGS.items():

        print(
            f"\nTesting configuration: "
            f"{config_name}"
        )

        y_true = []
        y_pred = []

        for _, group in grouped:

            records = group.to_dict(
                "records"
            )

            for i in range(len(records)):

                for j in range(
                    i + 1,
                    len(records)
                ):

                    record1 = records[i]
                    record2 = records[j]

                    score = weighted_composite_score(
                        record1,
                        record2,
                        weights
                    )

                    predicted_match = (
                        score >= THRESHOLD
                    )

                    actual_match = (
                        record1["patient_id"]
                        == record2["patient_id"]
                    )

                    y_true.append(
                        int(actual_match)
                    )

                    y_pred.append(
                        int(predicted_match)
                    )

        precision = precision_score(
            y_true,
            y_pred,
            zero_division=0
        )

        recall = recall_score(
            y_true,
            y_pred,
            zero_division=0
        )

        f1 = f1_score(
            y_true,
            y_pred,
            zero_division=0
        )

        false_links = sum(
            1
            for actual, predicted
            in zip(y_true, y_pred)
            if predicted == 1
            and actual == 0
        )

        missed_links = sum(
            1
            for actual, predicted
            in zip(y_true, y_pred)
            if actual == 1
            and predicted == 0
        )

        results.append({
            "Configuration": config_name,
            "Name": weights["name"],
            "Age": weights["age"],
            "Village": weights["village"],
            "Gender": weights["gender"],
            "DOB": weights["dob"],
            "Precision": precision,
            "Recall": recall,
            "F1": f1,
            "False_Links": false_links,
            "Missed_Links": missed_links
        })

    results_df = pd.DataFrame(results)

    print("\n")
    print("=" * 110)
    print("SIMILARITY-WEIGHT SENSITIVITY ANALYSIS")
    print("=" * 110)

    print(
        results_df.to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}"
        )
    )

    print("=" * 110)

    # Save results
    output_path = os.path.join(
        "data",
        "processed",
        "weight_sensitivity_results.csv"
    )

    results_df.to_csv(
        output_path,
        index=False
    )

    print(
        f"\nResults saved to: {output_path}"
    )

    # Best configuration by F1
    best_row = results_df.loc[
        results_df["F1"].idxmax()
    ]

    print("\nBest configuration by F1:")
    print(
        f"Configuration = "
        f"{best_row['Configuration']}"
    )
    print(
        f"F1            = "
        f"{best_row['F1']:.4f}"
    )
    print(
        f"Precision     = "
        f"{best_row['Precision']:.4f}"
    )
    print(
        f"Recall        = "
        f"{best_row['Recall']:.4f}"
    )


if __name__ == "__main__":

    run_weight_experiment()