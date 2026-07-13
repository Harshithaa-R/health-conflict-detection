import pandas as pd
import numpy as np
import os


# ---------------------------------------------------
# DOMAIN-SPECIFIC CONFLICT THRESHOLDS
# Based on clinical significance per field
# ---------------------------------------------------

THRESHOLDS = {

    "maternal": {
        "haemoglobin_gdl":     1.0,   # g/dL
        "systolic_bp":         10,    # mmHg
        "blood_sugar_fasting": 15,    # mg/dL
        "anc_visits_count":    1,     # visits
        "weight_kg":           3,     # kg
        "fundal_height_cm":    3,     # cm
    },

    "child": {
        "weight_child_kg":     0.5,   # kg — small children, tight threshold
        "height_cm":           2.0,   # cm
        "muac_cm":             0.8,   # cm
        "waz_score":           0.5,   # Z-score units
        "haz_score":           0.5,   # Z-score units
        "haemoglobin_child":   1.0,   # g/dL
    },

    "chronic": {
        "fasting_blood_sugar":      20,   # mg/dL
        "postprandial_blood_sugar": 30,   # mg/dL
        "hba1c":                    0.5,  # %
        "bp_systolic_reading1":     10,   # mmHg
        "bp_diastolic_reading1":    8,    # mmHg
        "missed_doses_count":       2,    # doses
        "creatinine":               0.3,  # mg/dL
        "bmi":                      2.0,  # kg/m²
    },
}

# Human-readable labels for all conflict fields
FIELD_LABELS = {
    # Maternal
    "haemoglobin_conflict":         "Haemoglobin Level",
    "blood_pressure_conflict":      "Blood Pressure",
    "blood_sugar_conflict":         "Blood Sugar (Fasting)",
    "anc_visit_conflict":           "ANC Visits",
    "weight_conflict":              "Body Weight",
    "fundal_height_conflict":       "Fundal Height",
    # Child
    "child_weight_conflict":        "Child Weight",
    "child_height_conflict":        "Child Height",
    "muac_conflict":                "MUAC",
    "waz_conflict":                 "Weight-for-Age Z-Score",
    "haz_conflict":                 "Height-for-Age Z-Score",
    "child_haemoglobin_conflict":   "Child Haemoglobin",
    # Chronic
    "fasting_glucose_conflict":     "Fasting Blood Sugar",
    "postprandial_glucose_conflict":"Postprandial Blood Sugar",
    "hba1c_conflict":               "HbA1c",
    "bp_systolic_conflict":         "Systolic BP",
    "bp_diastolic_conflict":        "Diastolic BP",
    "missed_doses_conflict":        "Missed TB Doses",
    "creatinine_conflict":          "Creatinine",
    "bmi_conflict":                 "BMI",
}


def check_conflict(group, field, threshold):
    """Return True if range of non-null values exceeds threshold."""
    vals = group[field].dropna().tolist()
    if len(vals) < 2:
        return False
    return (max(vals) - min(vals)) >= threshold


def detect_maternal_conflicts(group):

    t = THRESHOLDS["maternal"]
    conflicts = []

    field_map = [
        ("haemoglobin_gdl",     t["haemoglobin_gdl"],     "haemoglobin_conflict"),
        ("systolic_bp",         t["systolic_bp"],          "blood_pressure_conflict"),
        ("blood_sugar_fasting", t["blood_sugar_fasting"],  "blood_sugar_conflict"),
        ("anc_visits_count",    t["anc_visits_count"],     "anc_visit_conflict"),
        ("weight_kg",           t["weight_kg"],            "weight_conflict"),
        ("fundal_height_cm",    t["fundal_height_cm"],     "fundal_height_conflict"),
    ]

    for field, threshold, label in field_map:
        if field in group.columns and check_conflict(group, field, threshold):
            conflicts.append(label)

    return conflicts


def detect_child_conflicts(group):

    t = THRESHOLDS["child"]
    conflicts = []

    field_map = [
        ("weight_child_kg",  t["weight_child_kg"],  "child_weight_conflict"),
        ("height_cm",        t["height_cm"],         "child_height_conflict"),
        ("muac_cm",          t["muac_cm"],            "muac_conflict"),
        ("waz_score",        t["waz_score"],          "waz_conflict"),
        ("haz_score",        t["haz_score"],          "haz_conflict"),
        ("haemoglobin_child", t["haemoglobin_child"], "child_haemoglobin_conflict"),
    ]

    for field, threshold, label in field_map:
        if field in group.columns and check_conflict(group, field, threshold):
            conflicts.append(label)

    # Immunization conflicts — any disagreement across cadres
    imm_fields = [
        "bcg_given", "opv0_given", "opv1_given", "opv2_given", "opv3_given",
        "dpt1_given", "dpt2_given", "dpt3_given", "hepatitis_b_given",
        "measles_given", "mmr_given", "pentavalent_given",
    ]

    for f in imm_fields:
        if f in group.columns:
            vals = group[f].dropna().unique()
            if len(vals) > 1:
                conflicts.append(f"immunization_conflict_{f}")

    return conflicts


def detect_chronic_conflicts(group):

    t = THRESHOLDS["chronic"]
    conflicts = []

    field_map = [
        ("fasting_blood_sugar",      t["fasting_blood_sugar"],      "fasting_glucose_conflict"),
        ("postprandial_blood_sugar", t["postprandial_blood_sugar"],  "postprandial_glucose_conflict"),
        ("hba1c",                    t["hba1c"],                     "hba1c_conflict"),
        ("bp_systolic_reading1",     t["bp_systolic_reading1"],      "bp_systolic_conflict"),
        ("bp_diastolic_reading1",    t["bp_diastolic_reading1"],     "bp_diastolic_conflict"),
        ("missed_doses_count",       t["missed_doses_count"],        "missed_doses_conflict"),
        ("creatinine",               t["creatinine"],                "creatinine_conflict"),
        ("bmi",                      t["bmi"],                       "bmi_conflict"),
    ]

    for field, threshold, label in field_map:
        if field in group.columns and check_conflict(group, field, threshold):
            conflicts.append(label)

    return conflicts


def detect_measurement_conflicts():

    print("Loading linked maternal records...")

    df = pd.read_csv(
        "data/processed/linked_records.csv",
        low_memory=False
    )

    if "domain" not in df.columns:
        df["domain"] = "maternal"

    conflicts_all = []

    total_with_conflicts = 0
    multi_conflict_cases = 0

    grouped = df.groupby("unified_patient_id")

    for uid, group in grouped:

        domain = group.iloc[0].get("domain", "maternal")

        if domain == "maternal":
            patient_conflicts = detect_maternal_conflicts(group)
        elif domain == "child":
            patient_conflicts = detect_child_conflicts(group)
        elif domain == "chronic":
            patient_conflicts = detect_chronic_conflicts(group)
        else:
            patient_conflicts = []

        if len(patient_conflicts) > 0:
            total_with_conflicts += 1

        if len(patient_conflicts) > 1:
            multi_conflict_cases += 1

        conflicts_all.append({
            "unified_patient_id": uid,
            "patient_id":         group.iloc[0]["patient_id"],
            "domain":             domain,
            "name":               group.iloc[0]["name"],
            "district":           group.iloc[0]["district"],
            "village":            group.iloc[0]["village"],
            "num_conflicts":      len(patient_conflicts),
            "conflict_types": (
                ",".join(patient_conflicts)
                if patient_conflicts else "no_conflict"
            ),
            "has_conflict":       len(patient_conflicts) > 0,
        })

    conflicts_df = pd.DataFrame(conflicts_all)

    os.makedirs("data/processed", exist_ok=True)

    conflicts_df.to_csv(
        "data/processed/measurement_conflicts.csv",
        index=False
    )

    # ---------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------

    print("\nMeasurement Conflict Summary")
    print("=" * 50)

    total = len(conflicts_df)
    print(f"Patients Analysed          : {total:,}")
    print(f"Patients With Conflicts    : {total_with_conflicts:,}  ({total_with_conflicts/total*100:.1f}%)")
    print(f"Multi-conflict Cases       : {multi_conflict_cases:,}")

    print("\nBy Domain:")
    for domain in ["maternal", "child", "chronic"]:
        d = conflicts_df[conflicts_df["domain"] == domain]
        wc = int(d["has_conflict"].sum())
        if len(d) > 0:
            print(f"  {domain:<10}: {wc:,} / {len(d):,} ({wc/len(d)*100:.1f}%)")

    print("\nTop Conflict Types:")
    type_counts = {}
    for _, row in conflicts_df[conflicts_df["has_conflict"]].iterrows():
        for t in str(row["conflict_types"]).split(","):
            t = t.strip()
            type_counts[t] = type_counts.get(t, 0) + 1

    for k, v in sorted(type_counts.items(), key=lambda x: -x[1])[:10]:
        label = FIELD_LABELS.get(k, k)
        print(f"  {label:<35}: {v:,}")

    print(
        "\nSaved: data/processed/measurement_conflicts.csv"
    )

    return conflicts_df


if __name__ == "__main__":

    detect_measurement_conflicts()