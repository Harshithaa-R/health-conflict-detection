import pandas as pd
import os


# ---------------------------------------------------
# NUMERIC COLUMNS PER DOMAIN
# ---------------------------------------------------

MATERNAL_NUMERIC = [
    "age", "haemoglobin_gdl", "systolic_bp", "diastolic_bp",
    "blood_sugar_fasting", "weight_kg", "fundal_height_cm",
    "anc_visits_count", "gestational_age_weeks",
    "gravida", "parity", "ifa_tablets_given",
]

CHILD_NUMERIC = [
    "age", "child_age_months", "weight_child_kg", "height_cm",
    "muac_cm", "waz_score", "haz_score", "haemoglobin_child",
]

CHRONIC_NUMERIC = [
    "age", "fasting_blood_sugar", "postprandial_blood_sugar",
    "hba1c", "random_blood_glucose", "bmi", "waist_circumference",
    "creatinine", "urine_microalbumin",
    "bp_systolic_reading1", "bp_systolic_reading2",
    "bp_diastolic_reading1", "bp_diastolic_reading2",
    "pulse_rate", "potassium", "missed_doses_count", "tb_weight_kg",
]

ALL_NUMERIC = list(set(MATERNAL_NUMERIC + CHILD_NUMERIC + CHRONIC_NUMERIC))

BOOL_FIELDS = [
    "tt_1_given", "tt_2_given", "oedema_present", "pallor_present",
    "sam_status", "bcg_given", "opv0_given", "opv1_given", "opv2_given",
    "opv3_given", "dpt1_given", "dpt2_given", "dpt3_given",
    "hepatitis_b_given", "measles_given", "mmr_given", "pentavalent_given",
    "vitamin_a_given", "ifa_child_given", "deworming_given",
    "developmental_milestone_met", "insulin_dependent",
    "diabetes_medication_adherence", "foot_examination_done",
    "eye_examination_done", "hypertension_medication_adherence",
    "salt_intake_compliant", "physical_activity_compliant",
    "fundoscopy_done", "ecg_done", "side_effects_reported",
    "hiv_coinfection", "contact_tracing_done", "true_high_risk",
]


def standardize_records():

    print("Loading unified source records...")

    unified_path = "data/synthetic/unified_health_records.csv"

    if os.path.exists(unified_path):

        df = pd.read_csv(unified_path, low_memory=False)

    else:

        print(
            "unified_health_records.csv not found — "
            "falling back to per-cadre maternal files..."
        )

        asha      = pd.read_csv("data/synthetic/asha_maternal.csv")
        anm       = pd.read_csv("data/synthetic/anm_maternal.csv")
        phc       = pd.read_csv("data/synthetic/phc_maternal.csv")
        anganwadi = pd.read_csv("data/synthetic/anganwadi_maternal.csv")

        df = pd.concat(
            [asha, anm, phc, anganwadi],
            ignore_index=True
        )

        if "domain" not in df.columns:
            df["domain"] = "maternal"

    # Column names
    df.columns = df.columns.str.lower().str.strip()

    # String fields
    for col in ["name", "district", "village", "taluk"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .str.title()
                .replace("Nan", pd.NA)
            )

    # Cadre normalise
    if "cadre" in df.columns:
        df["cadre"] = df["cadre"].astype(str).str.upper().str.strip()

    # Numeric coercion
    for col in ALL_NUMERIC:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Boolean coercion
    for col in BOOL_FIELDS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    os.makedirs("data/processed", exist_ok=True)

    df.to_csv(
        "data/processed/standardized_records.csv",
        index=False
    )

    print("\nStandardization Complete")
    print("=" * 50)
    print(f"Total Records   : {len(df):,}")
    print(f"Unique Patients : {df['patient_id'].nunique():,}")

    print("\nCadre Distribution:")
    print(df["cadre"].value_counts().to_string())

    if "domain" in df.columns:
        print("\nDomain Distribution:")
        print(df["domain"].value_counts().to_string())

    print("\nSaved: data/processed/standardized_records.csv")

    return df


if __name__ == "__main__":

    standardize_records()