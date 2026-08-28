import os
import sys

import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score


# ---------------------------------------------------
# Import the actual entity-resolution implementation
# ---------------------------------------------------

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from entity_resolution import composite_score


# ---------------------------------------------------
# Configuration
# ---------------------------------------------------

THRESHOLDS = [75, 80, 85, 90, 95]

DATA_PATH = os.path.join(
    "data",
    "processed",
    "blocked_records.csv"
)


# ---------------------------------------------------
# Threshold sensitivity experiment
# ---------------------------------------------------

def run_threshold_experiment():

    print("Loading blocked records...")

    df = pd.read_csv(
        DATA_PATH,
        low_memory=False
    )

    print(f"Records loaded: {len(df):,}")

    group_cols = [
        "domain",
        "district",
        "village"
    ]

    results = []

    grouped = df.groupby(group_cols)

    for threshold in THRESHOLDS:

        print(
            f"\nTesting threshold: {threshold}"
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

                    score = composite_score(
                        record1,
                        record2
                    )

                    predicted_match = (
                        score >= threshold
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
            "Threshold": threshold,
            "Precision": precision,
            "Recall": recall,
            "F1": f1,
            "False_Links": false_links,
            "Missed_Links": missed_links
        })

    results_df = pd.DataFrame(results)

    # ---------------------------------------------------
    # Display results
    # ---------------------------------------------------

    print("\n")
    print("=" * 90)
    print("ENTITY-RESOLUTION THRESHOLD SENSITIVITY ANALYSIS")
    print("=" * 90)

    print(
        results_df.to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}"
        )
    )

    print("=" * 90)

    # ---------------------------------------------------
    # Save results
    # ---------------------------------------------------

    output_dir = os.path.join(
        "data",
        "processed"
    )

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    output_path = os.path.join(
        output_dir,
        "threshold_sensitivity_results.csv"
    )

    results_df.to_csv(
        output_path,
        index=False
    )

    print(
        f"\nResults saved to: {output_path}"
    )

    # ---------------------------------------------------
    # Identify best F1
    # ---------------------------------------------------

    best_row = results_df.loc[
        results_df["F1"].idxmax()
    ]

    print("\nBest F1 threshold:")
    print(
        f"Threshold = {int(best_row['Threshold'])}"
    )
    print(
        f"F1        = {best_row['F1']:.4f}"
    )
    print(
        f"Precision = {best_row['Precision']:.4f}"
    )
    print(
        f"Recall    = {best_row['Recall']:.4f}"
    )

    return results_df


# ---------------------------------------------------
# Run experiment
# ---------------------------------------------------

if __name__ == "__main__":

    run_threshold_experiment()