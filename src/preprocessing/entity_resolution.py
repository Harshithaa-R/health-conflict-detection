import pandas as pd
from rapidfuzz import fuzz
import os


# ---------------------------------------------------
# COMPOSITE SCORE
# Domain-aware: only compare patients within same domain
# ---------------------------------------------------

def composite_score(row1, row2):

    # Must be same domain — never link a child to a maternal patient
    if str(row1.get("domain", "")) != str(row2.get("domain", "")):
        return 0.0

    name_score = fuzz.token_sort_ratio(
        str(row1["name"]),
        str(row2["name"])
    )

    age_diff = abs(
        float(row1["age"]) - float(row2["age"])
    )

    age_score = max(0, 100 - (age_diff * 10))

    village_score = (
        100
        if str(row1["village"]).strip().lower()
        == str(row2["village"]).strip().lower()
        else 0
    )

    gender_score = (
        100
        if str(row1.get("gender", ""))
        == str(row2.get("gender", ""))
        else 0
    )

    dob_score = (
        100
        if str(row1.get("dob", "X"))
        == str(row2.get("dob", "Y"))
        else 0
    )

    final_score = (
        0.50 * name_score  +
        0.15 * age_score   +
        0.15 * village_score +
        0.10 * gender_score +
        0.10 * dob_score
    )

    return final_score


# ---------------------------------------------------
# FIELDS TO CARRY THROUGH — all domains
# ---------------------------------------------------

CORE_FIELDS = [
    "unified_patient_id", "source_record_id", "patient_id",
    "domain", "cadre", "name", "age", "gender",
    "district", "village",
]

MATERNAL_FIELDS = [
    "haemoglobin_gdl", "systolic_bp", "blood_sugar_fasting",
    "anc_visits_count", "weight_kg", "fundal_height_cm",
    "diastolic_bp", "gestational_age_weeks",
]

CHILD_FIELDS = [
    "child_age_months", "weight_child_kg", "height_cm",
    "muac_cm", "waz_score", "haz_score", "sam_status",
    "haemoglobin_child",
    "bcg_given", "opv0_given", "opv1_given", "opv2_given", "opv3_given",
    "dpt1_given", "dpt2_given", "dpt3_given", "hepatitis_b_given",
    "measles_given", "mmr_given", "pentavalent_given",
    "vitamin_a_given", "ifa_child_given", "deworming_given",
    "developmental_milestone_met",
]

CHRONIC_FIELDS = [
    "chronic_condition",
    "fasting_blood_sugar", "postprandial_blood_sugar",
    "hba1c", "random_blood_glucose", "insulin_dependent",
    "diabetes_medication_adherence", "bmi", "waist_circumference",
    "foot_examination_done", "eye_examination_done",
    "creatinine", "urine_microalbumin",
    "bp_systolic_reading1", "bp_systolic_reading2",
    "bp_diastolic_reading1", "bp_diastolic_reading2",
    "pulse_rate", "hypertension_medication_adherence",
    "salt_intake_compliant", "physical_activity_compliant",
    "fundoscopy_done", "ecg_done", "potassium",
    "sputum_smear_result", "genexpert_result", "chest_xray_result",
    "treatment_category", "treatment_phase", "dots_provider",
    "missed_doses_count", "tb_weight_kg", "side_effects_reported",
    "hiv_coinfection", "contact_tracing_done",
]

ALL_CARRY_FIELDS = CORE_FIELDS + MATERNAL_FIELDS + CHILD_FIELDS + CHRONIC_FIELDS


def resolve_entities():

    print("Loading blocked records...")

    df = pd.read_csv(
        "data/processed/blocked_records.csv",
        low_memory=False
    )

    # Ensure domain column exists
    if "domain" not in df.columns:
        df["domain"] = "maternal"

    linked         = []
    matched_truth  = 0
    total_matches  = 0
    unified_counter = 1

    # ---------------------------------------------------
    # GROUP BY domain + district + village
    # Keeps domains separated — no cross-domain linking
    # ---------------------------------------------------

    group_cols = ["domain", "district", "village"]

    grouped = df.groupby(group_cols)

    for _, group in grouped:

        records = group.to_dict("records")
        visited = set()

        for i in range(len(records)):

            if i in visited:
                continue

            anchor  = records[i]
            cluster = [anchor]
            visited.add(i)

            for j in range(i + 1, len(records)):

                if j in visited:
                    continue

                candidate = records[j]

                score = composite_score(anchor, candidate)

                if score >= 85:

                    cluster.append(candidate)
                    visited.add(j)
                    total_matches += 1

                    if (
                        anchor["patient_id"]
                        == candidate["patient_id"]
                    ):
                        matched_truth += 1

            unified_id = f"UID_{unified_counter:06d}"
            unified_counter += 1

            for row in cluster:

                out = {"unified_patient_id": unified_id}

                for field in ALL_CARRY_FIELDS[1:]:  # skip unified_patient_id
                    out[field] = row.get(field, None)

                linked.append(out)

    linked_df = pd.DataFrame(linked)

    os.makedirs("data/processed", exist_ok=True)

    linked_df.to_csv(
        "data/processed/linked_records.csv",
        index=False
    )

    precision = (
        matched_truth / total_matches
        if total_matches > 0 else 0
    )

    true_pairs = len(df) - df["patient_id"].nunique()

    recall = (
        matched_truth / true_pairs
        if true_pairs > 0 else 0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0 else 0
    )

    print("\nEntity Resolution Summary")
    print("=" * 50)
    print(f"Unified Patients : {linked_df['unified_patient_id'].nunique():,}")
    print(f"Linked Records   : {len(linked_df):,}")
    print(f"Precision        : {precision:.4f}")
    print(f"Recall           : {recall:.4f}")
    print(f"F1 Score         : {f1:.4f}")

    if "domain" in linked_df.columns:
        print("\nLinked Records by Domain:")
        print(linked_df["domain"].value_counts().to_string())

    print("\nSaved: data/processed/linked_records.csv")

    return linked_df


if __name__ == "__main__":

    resolve_entities()