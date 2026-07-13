import pandas as pd
import numpy as np
import os


# ---------------------------------------------------
# MATERNAL RISK FEATURES
# ---------------------------------------------------

def build_maternal_features(df):

    df["severe_anaemia"]      = np.where(df["haemoglobin_gdl"] < 9,       1, 0)
    df["hypertension_risk"]   = np.where(df["systolic_bp"] >= 140,         1, 0)
    df["diabetes_risk"]       = np.where(df["blood_sugar_fasting"] >= 140, 1, 0)
    df["low_weight_risk"]     = np.where(df["weight_kg"] < 45,             1, 0)
    df["fundal_height_risk"]  = np.where(
        (df["fundal_height_cm"] < 20) | (df["fundal_height_cm"] > 38), 1, 0
    )
    df["poor_anc_coverage"]   = np.where(df["anc_visits_count"] < 2,       1, 0)

    df["maternal_risk_score"] = (
        df["severe_anaemia"]     * 3 +
        df["hypertension_risk"]  * 3 +
        df["diabetes_risk"]      * 3 +
        df["low_weight_risk"]    * 2 +
        df["fundal_height_risk"] * 2 +
        df["poor_anc_coverage"]  * 2
    )

    df["predicted_high_risk"] = np.where(
        df["maternal_risk_score"] >= 3, 1, 0
    )

    return df


# ---------------------------------------------------
# CHILD RISK FEATURES
# ---------------------------------------------------

def build_child_features(df):

    # Helper — safely get column or zeros
    def col(name):
        if name in df.columns:
            return df[name]
        return pd.Series(np.nan, index=df.index)

    df["severe_acute_malnutrition"] = np.where(
        (col("muac_cm") < 11.5) | (col("waz_score") < -3), 1, 0
    )

    df["moderate_malnutrition"] = np.where(
        col("muac_cm").between(11.5, 12.4) |
        col("waz_score").between(-3, -2),
        1, 0
    )

    df["stunting_risk"] = np.where(
        col("haz_score") < -2, 1, 0
    )

    df["anaemia_child"] = np.where(
        col("haemoglobin_child") < 9, 1, 0
    )

    # Immunization completeness
    imm_fields = [
        "bcg_given", "opv1_given", "dpt1_given",
        "measles_given", "pentavalent_given",
    ]
    available_imm = [f for f in imm_fields if f in df.columns]

    if available_imm:
        df["immunization_score"] = df[available_imm].sum(axis=1)
        df["incomplete_immunization"] = np.where(
            df["immunization_score"] < len(available_imm), 1, 0
        )
    else:
        df["immunization_score"]      = 0
        df["incomplete_immunization"] = 0

    # Developmental delay — safely handle missing column
    if "developmental_milestone_met" in df.columns:
        df["developmental_delay"] = np.where(
            df["developmental_milestone_met"] == 0, 1, 0
        )
    else:
        df["developmental_delay"] = 0

    df["child_risk_score"] = (
        df["severe_acute_malnutrition"] * 4 +
        df["moderate_malnutrition"]     * 2 +
        df["stunting_risk"]             * 2 +
        df["anaemia_child"]             * 2 +
        df["incomplete_immunization"]   * 1 +
        df["developmental_delay"]       * 2
    )

    df["predicted_high_risk"] = np.where(
        df["child_risk_score"] >= 3, 1, 0
    )

    return df


# ---------------------------------------------------
# CHRONIC DISEASE RISK FEATURES
# ---------------------------------------------------

def build_chronic_features(df):

    def col(name):
        if name in df.columns:
            return df[name]
        return pd.Series(np.nan, index=df.index)

    df["uncontrolled_diabetes"] = np.where(
        col("hba1c").notna() & (col("hba1c") > 9), 1, 0
    )

    df["high_fasting_glucose"] = np.where(
        col("fasting_blood_sugar").notna() &
        (col("fasting_blood_sugar") > 200), 1, 0
    )

    df["poor_dm_adherence"] = np.where(
        col("diabetes_medication_adherence") == 0, 1, 0
    )

    df["severe_hypertension"] = np.where(
        col("bp_systolic_reading1").notna() &
        (col("bp_systolic_reading1") > 160), 1, 0
    )

    df["poor_htn_adherence"] = np.where(
        col("hypertension_medication_adherence") == 0, 1, 0
    )

    df["tb_default_risk"] = np.where(
        col("missed_doses_count").notna() &
        (col("missed_doses_count") > 5), 1, 0
    )

    df["tb_hiv_comorbidity"] = np.where(
        col("hiv_coinfection") == 1, 1, 0
    )

    if "chronic_condition" in df.columns:
        df["cardiometabolic_risk"] = np.where(
            df["chronic_condition"].str.contains(
                "diabetes_hypertension", na=False
            ), 1, 0
        )
    else:
        df["cardiometabolic_risk"] = 0

    df["renal_risk"] = np.where(
        col("creatinine").notna() & (col("creatinine") > 2.0), 1, 0
    )

    df["obesity_risk"] = np.where(
        col("bmi").notna() & (col("bmi") > 30), 1, 0
    )

    df["chronic_risk_score"] = (
        df["uncontrolled_diabetes"]  * 3 +
        df["high_fasting_glucose"]   * 2 +
        df["poor_dm_adherence"]      * 2 +
        df["severe_hypertension"]    * 3 +
        df["poor_htn_adherence"]     * 2 +
        df["tb_default_risk"]        * 3 +
        df["tb_hiv_comorbidity"]     * 4 +
        df["cardiometabolic_risk"]   * 3 +
        df["renal_risk"]             * 2 +
        df["obesity_risk"]           * 1
    )

    df["predicted_high_risk"] = np.where(
        df["chronic_risk_score"] >= 3, 1, 0
    )

    return df


# ---------------------------------------------------
# MAIN
# ---------------------------------------------------

def build_features():

    print("Loading resolved records...")

    resolved_path = "data/processed/resolved_all_records.csv"

    if os.path.exists(resolved_path):
        df = pd.read_csv(resolved_path, low_memory=False)
    else:
        print(
            "resolved_all_records.csv not found — "
            "falling back to resolved_maternal_records.csv"
        )
        df = pd.read_csv(
            "data/processed/resolved_maternal_records.csv"
        )
        if "domain" not in df.columns:
            df["domain"] = "maternal"

    # ---------------------------------------------------
    # MERGE BACK NON-NUMERIC FIELDS LOST IN BAYESIAN EM
    # bayesian_em.py only resolves numeric fields — boolean
    # flags like developmental_milestone_met, immunization
    # fields, chronic_condition etc are not carried through.
    # We re-merge them from the linked_records.csv using
    # the mode (most common value) per patient.
    # ---------------------------------------------------

    print("Merging non-numeric fields from linked records...")

    try:
        linked = pd.read_csv(
            "data/processed/linked_records.csv",
            low_memory=False
        )

        bool_and_cat_fields = [
            # child
            "bcg_given", "opv0_given", "opv1_given", "opv2_given",
            "opv3_given", "dpt1_given", "dpt2_given", "dpt3_given",
            "hepatitis_b_given", "measles_given", "mmr_given",
            "pentavalent_given", "vitamin_a_given", "ifa_child_given",
            "deworming_given", "developmental_milestone_met", "sam_status",
            # chronic
            "chronic_condition", "insulin_dependent",
            "diabetes_medication_adherence", "foot_examination_done",
            "eye_examination_done", "hypertension_medication_adherence",
            "salt_intake_compliant", "physical_activity_compliant",
            "fundoscopy_done", "ecg_done", "side_effects_reported",
            "hiv_coinfection", "contact_tracing_done",
            "sputum_smear_result", "genexpert_result",
            "chest_xray_result", "treatment_category",
            "treatment_phase", "dots_provider", "medication_name",
            # maternal
            "tt_1_given", "tt_2_given", "oedema_present",
            "pallor_present", "urine_albumin",
        ]

        available = [
            f for f in bool_and_cat_fields
            if f in linked.columns
        ]

        # Mode per patient for each field
        def safe_mode(x):
            m = x.dropna().mode()
            return m.iloc[0] if len(m) > 0 else np.nan

        extra = (
            linked.groupby("patient_id")[available]
            .agg(safe_mode)
            .reset_index()
        )

        # Merge into resolved df
        before_cols = set(df.columns)
        df = df.merge(extra, on="patient_id", how="left", suffixes=("", "_linked"))

        # Drop duplicate _linked columns if any
        dup_cols = [c for c in df.columns if c.endswith("_linked")]
        df.drop(columns=dup_cols, inplace=True)

        new_cols = set(df.columns) - before_cols
        print(f"  Merged {len(new_cols)} non-numeric fields")

    except Exception as e:
        print(f"  Warning: could not merge linked fields — {e}")

    # ---------------------------------------------------
    # BUILD FEATURES PER DOMAIN
    # ---------------------------------------------------

    os.makedirs("data/processed", exist_ok=True)

    all_featured = []

    for domain in ["maternal", "child", "chronic"]:

        domain_df = df[df["domain"] == domain].copy()

        if domain_df.empty:
            print(f"No records for domain: {domain} — skipping")
            continue

        print(f"\nBuilding features for {domain} ({len(domain_df):,} patients)...")

        if domain == "maternal":
            domain_df = build_maternal_features(domain_df)
        elif domain == "child":
            domain_df = build_child_features(domain_df)
        elif domain == "chronic":
            domain_df = build_chronic_features(domain_df)

        all_featured.append(domain_df)

    combined = pd.concat(all_featured, ignore_index=True)

    combined.to_csv(
        "data/processed/final_features.csv",
        index=False
    )

    # ---------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------

    print("\nFeature Engineering Summary")
    print("=" * 50)
    print(f"Total Patients : {len(combined):,}")

    for domain in ["maternal", "child", "chronic"]:

        d = combined[combined["domain"] == domain]

        if d.empty:
            continue

        hr = int(d["predicted_high_risk"].sum())
        print(
            f"\n{domain.upper()} — "
            f"{hr:,} high risk / {len(d):,} total "
            f"({hr/len(d)*100:.1f}%)"
        )

        score_col = {
            "maternal": "maternal_risk_score",
            "child":    "child_risk_score",
            "chronic":  "chronic_risk_score",
        }.get(domain)

        if score_col and score_col in d.columns:
            print(f"  Avg risk score : {d[score_col].mean():.2f}")

    print("\nSaved: data/processed/final_features.csv")

    return combined


if __name__ == "__main__":

    build_features()