import pandas as pd
import numpy as np
import os


# ---------------------------------------------------
# DOMAIN-SPECIFIC FIELDS FOR BAYESIAN RESOLUTION
# ---------------------------------------------------

DOMAIN_FIELDS = {

    "maternal": [
        "haemoglobin_gdl",
        "systolic_bp",
        "blood_sugar_fasting",
        "weight_kg",
        "fundal_height_cm",
        "anc_visits_count",
    ],

    "child": [
        "weight_child_kg",
        "height_cm",
        "muac_cm",
        "waz_score",
        "haz_score",
        "haemoglobin_child",
    ],

    "chronic": [
        "fasting_blood_sugar",
        "postprandial_blood_sugar",
        "bp_systolic_reading1",
        "bp_diastolic_reading1",
        "hba1c",
        "missed_doses_count",
        "tb_weight_kg",
        "creatinine",
        "bmi",
    ],
}

DOMAIN_OUTPUT = {
    "maternal": "data/processed/resolved_maternal_records.csv",
    "child":    "data/processed/resolved_child_records.csv",
    "chronic":  "data/processed/resolved_chronic_records.csv",
}

MAX_ITERATIONS        = 20
CONVERGENCE_THRESHOLD = 0.0001

# Pre-computed base reliability per cadre — used as
# initial weights in EM instead of uniform 0.8.
# These reflect actual source accuracy from reliability_scorer.py
BASE_RELIABILITY = {
    "PHC":       0.95,
    "ANM":       0.90,
    "ANGANWADI": 0.75,
    "ASHA":      0.70,
}


def run_em(group, field):
    """
    Bayesian EM resolution for a single numeric field.
    Initial weights come from pre-computed source reliability
    scores (PHC=0.95, ANM=0.90, etc.) rather than uniform 0.8.
    This ensures PHC values dominate the initial truth estimate,
    and the EM refines from there based on observed agreement.
    """

    # Use per-record reliability if available, else base rates
    if "source_reliability" in group.columns:
        data = group[["cadre", field, "source_reliability"]].dropna(subset=[field])
    else:
        data = group[["cadre", field]].dropna(subset=[field])
        data = data.copy()
        data["source_reliability"] = data["cadre"].map(BASE_RELIABILITY).fillna(0.75)

    if len(data) == 0:
        return np.nan

    # Initialise reliabilities from pre-computed scores
    # (mean per cadre in this patient group)
    reliabilities = (
        data.groupby("cadre")["source_reliability"]
        .mean()
        .to_dict()
    )

    # Initial truth = reliability-weighted average (not simple mean)
    num = sum(
        row[field] * reliabilities.get(row["cadre"], 0.75)
        for _, row in data.iterrows()
    )
    den = sum(reliabilities.get(c, 0.75) for c in data["cadre"])
    truth = num / den if den > 0 else data[field].mean()

    # EM iterations
    for _ in range(MAX_ITERATIONS):

        old_truth = truth

        # E-step: compute weighted truth
        numerator   = 0
        denominator = 0

        for _, row in data.iterrows():
            weight      = reliabilities[row["cadre"]]
            numerator  += row[field] * weight
            denominator += weight

        truth = numerator / denominator if denominator > 0 else old_truth

        # M-step: update reliability based on agreement with truth
        for source in reliabilities:

            source_rows = data[data["cadre"] == source]

            if source_rows.empty:
                continue

            errors = [
                abs(r[field] - truth)
                for _, r in source_rows.iterrows()
            ]

            mean_error = np.mean(errors)

            # Update reliability — but anchor to base rate
            # to prevent degenerate solutions
            base = BASE_RELIABILITY.get(source, 0.75)
            em_reliability = 1 / (1 + mean_error)

            # Blend: 60% EM-derived, 40% base rate anchor
            reliabilities[source] = (
                0.6 * em_reliability +
                0.4 * base
            )

        if abs(truth - old_truth) < CONVERGENCE_THRESHOLD:
            break

    return round(truth, 2)


def resolve_domain(df_domain, domain):

    fields  = DOMAIN_FIELDS.get(domain, [])
    grouped = df_domain.groupby("patient_id")

    resolved_records = []

    for patient_id, group in grouped:

        resolved = {
            "patient_id":            patient_id,
            "domain":                domain,
            "district":              group.iloc[0]["district"],
            "village":               group.iloc[0]["village"],
            "true_high_risk":        group.iloc[0]["true_high_risk"],
            "true_high_risk_reason": group.iloc[0]["true_high_risk_reason"],
        }

        if domain == "chronic" and "chronic_condition" in group.columns:
            resolved["chronic_condition"] = group.iloc[0]["chronic_condition"]

        for field in fields:
            if field in group.columns:
                resolved[field] = run_em(group, field)
            else:
                resolved[field] = np.nan

        resolved["sources_used"] = len(group)

        resolved_records.append(resolved)

    return pd.DataFrame(resolved_records)


def resolve_conflicts():

    print("Loading reliability scored records...")

    df = pd.read_csv(
        "data/processed/reliability_scored_records.csv",
        low_memory=False
    )

    if "domain" not in df.columns:
        df["domain"] = "maternal"

    # Standardise cadre names
    df["cadre"] = df["cadre"].astype(str).str.upper().str.strip()

    os.makedirs("data/processed", exist_ok=True)

    all_resolved = []

    for domain in ["maternal", "child", "chronic"]:

        domain_df = df[df["domain"] == domain]

        if domain_df.empty:
            print(f"No records for domain: {domain} — skipping")
            continue

        print(f"\nResolving {domain} domain ({len(domain_df):,} records)...")

        resolved_df = resolve_domain(domain_df, domain)

        resolved_df.to_csv(
            DOMAIN_OUTPUT[domain],
            index=False
        )

        print(f"  Resolved patients : {len(resolved_df):,}")

        all_resolved.append(resolved_df)

    combined = pd.concat(all_resolved, ignore_index=True)

    combined.to_csv(
        "data/processed/resolved_all_records.csv",
        index=False
    )

    print("\nBayesian EM Summary")
    print("=" * 50)
    print(f"Total Resolved Patients : {len(combined):,}")

    for domain in ["maternal", "child", "chronic"]:
        count = (combined["domain"] == domain).sum()
        print(f"  {domain:<10} : {count:,}")

    mat = combined[combined["domain"] == "maternal"]
    if len(mat) > 0 and "haemoglobin_gdl" in mat.columns:
        print(f"\nMaternal — Avg Hb : {mat['haemoglobin_gdl'].mean():.2f}")
        print(f"Maternal — Avg BP : {mat['systolic_bp'].mean():.2f}")

    chd = combined[combined["domain"] == "child"]
    if len(chd) > 0 and "muac_cm" in chd.columns:
        print(f"Child    — Avg MUAC : {chd['muac_cm'].mean():.2f}")

    chr_ = combined[combined["domain"] == "chronic"]
    if len(chr_) > 0 and "fasting_blood_sugar" in chr_.columns:
        print(f"Chronic  — Avg FBS  : {chr_['fasting_blood_sugar'].mean():.2f}")

    print("\nSaved:")
    for domain, path in DOMAIN_OUTPUT.items():
        print(f"  {path}")
    print("  data/processed/resolved_all_records.csv")

    return combined


if __name__ == "__main__":

    resolve_conflicts()