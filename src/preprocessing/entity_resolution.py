import pandas as pd
from rapidfuzz import fuzz
import os


def composite_score(row1, row2):

    # Name similarity
    name_score = fuzz.token_sort_ratio(
        str(row1["name"]),
        str(row2["name"])
    )

    # Age similarity
    age_diff = abs(
        float(row1["age"])
        -
        float(row2["age"])
    )

    age_score = max(
        0,
        100 - (age_diff * 10)
    )

    # Village match
    village_score = (
        100
        if str(row1["village"]).strip().lower()
        ==
        str(row2["village"]).strip().lower()
        else 0
    )

    # Gender match
    gender_score = (
        100
        if str(row1["gender"])
        ==
        str(row2["gender"])
        else 0
    )

    # DOB match
    dob_score = (
        100
        if str(row1["dob"])
        ==
        str(row2["dob"])
        else 0
    )

    final_score = (
        0.50 * name_score +
        0.15 * age_score +
        0.15 * village_score +
        0.10 * gender_score +
        0.10 * dob_score
    )

    return final_score


def resolve_entities():

    print("Loading blocked records...")

    df = pd.read_csv(
        "data/processed/blocked_records.csv"
    )

    linked = []

    matched_truth = 0
    total_matches = 0

    grouped = df.groupby(
        ["district", "village"]
    )

    unified_counter = 1

    for _, group in grouped:

        records = group.to_dict("records")

        visited = set()

        for i in range(len(records)):

            if i in visited:
                continue

            anchor = records[i]

            cluster = [anchor]

            visited.add(i)

            for j in range(i + 1, len(records)):

                if j in visited:
                    continue

                candidate = records[j]

                score = composite_score(
                    anchor,
                    candidate
                )

                if score >= 85:

                    cluster.append(
                        candidate
                    )

                    visited.add(j)

                    total_matches += 1

                    if (
                        anchor["patient_id"]
                        ==
                        candidate["patient_id"]
                    ):
                        matched_truth += 1

            unified_id = (
                f"UID_{unified_counter:06d}"
            )

            unified_counter += 1

            for row in cluster:

                linked.append({

                    "unified_patient_id":
                        unified_id,

                    "source_record_id":
                        row["source_record_id"],

                    "patient_id":
                        row["patient_id"],

                    "cadre":
                        row["cadre"],

                    "name":
                        row["name"],

                    "age":
                        row["age"],

                    "gender":
                        row["gender"],

                    "district":
                        row["district"],

                    "village":
                        row["village"],

                    "haemoglobin_gdl":
                        row["haemoglobin_gdl"],

                    "systolic_bp":
                        row["systolic_bp"],

                    "blood_sugar_fasting":
                        row["blood_sugar_fasting"],

                    "anc_visits_count":
                        row["anc_visits_count"],

                    "weight_kg":
                        row["weight_kg"],

                    "fundal_height_cm":
                        row["fundal_height_cm"]
                })

    linked_df = pd.DataFrame(linked)

    os.makedirs(
        "data/processed",
        exist_ok=True
    )

    linked_df.to_csv(
        "data/processed/linked_records.csv",
        index=False
    )

    precision = (
        matched_truth / total_matches
        if total_matches > 0
        else 0
    )
    
    true_pairs = len(df) - df["patient_id"].nunique()

    recall = (
        matched_truth / true_pairs
        if true_pairs > 0
        else 0
    )

    f1 = (
        (
            2 * precision * recall
        ) /
        (
            precision + recall
        )
        if (precision + recall) > 0
        else 0
    )

    print("\nEntity Resolution Summary")
    print("=" * 50)

    print(
        f"Unified Patients : "
        f"{linked_df['unified_patient_id'].nunique()}"
    )

    print(
        f"Linked Records : "
        f"{len(linked_df)}"
    )

    print(
        f"Precision : "
        f"{precision:.4f}"
    )

    print(
        f"Recall : "
        f"{recall:.4f}"
    )

    print(
        f"F1 Score : "
        f"{f1:.4f}"
    )

    print(
        "\nSaved:"
        " data/processed/linked_records.csv"
    )

    return linked_df


if __name__ == "__main__":

    resolve_entities()