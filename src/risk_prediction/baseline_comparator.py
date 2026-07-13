import pandas as pd
import numpy as np
import os
from sklearn.metrics import mean_squared_error


# ---------------------------------------------------
# FIELDS PER DOMAIN
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
        "creatinine",
        "bmi",
    ],
}

FIELD_LABELS = {
    "haemoglobin_gdl":          "Haemoglobin (g/dL)",
    "systolic_bp":              "Systolic BP (mmHg)",
    "blood_sugar_fasting":      "Blood Sugar (mg/dL)",
    "weight_kg":                "Weight (kg)",
    "fundal_height_cm":         "Fundal Height (cm)",
    "anc_visits_count":         "ANC Visits",
    "weight_child_kg":          "Child Weight (kg)",
    "height_cm":                "Height (cm)",
    "muac_cm":                  "MUAC (cm)",
    "waz_score":                "WAZ Score",
    "haz_score":                "HAZ Score",
    "haemoglobin_child":        "Child Haemoglobin (g/dL)",
    "fasting_blood_sugar":      "Fasting Blood Sugar (mg/dL)",
    "postprandial_blood_sugar": "Postprandial Sugar (mg/dL)",
    "bp_systolic_reading1":     "Systolic BP Reading (mmHg)",
    "bp_diastolic_reading1":    "Diastolic BP Reading (mmHg)",
    "hba1c":                    "HbA1c (%)",
    "creatinine":               "Creatinine (mg/dL)",
    "bmi":                      "BMI (kg/m²)",
}

SOURCE_PRIORITY = {
    "PHC": 1, "ANM": 2, "ANGANWADI": 3, "ASHA": 4
}


# ---------------------------------------------------
# BUILD GROUND TRUTH
# Average of ANM + PHC records (both low-noise sources)
# excludes ASHA (high noise) and Anganwadi (limited fields)
# This avoids the HSW=0 problem from comparing PHC to PHC
# ---------------------------------------------------

def build_ground_truth(raw, domain, fields):
    """
    Ground truth = weighted average of ANM and PHC records.
    PHC weight=2, ANM weight=1 (reflects reliability ratio).
    This gives a stable reference that no single baseline
    can trivially match.
    """
    trusted = raw[
        (raw["domain"] == domain) &
        (raw["cadre"].isin(["PHC", "ANM"]))
    ].copy()

    trusted["cadre_weight"] = trusted["cadre"].map({"PHC": 2, "ANM": 1})

    results = {"patient_id": []}
    for f in fields:
        results[f"gt_{f}"] = []

    for pid, group in trusted.groupby("patient_id"):
        results["patient_id"].append(pid)
        for f in fields:
            if f not in group.columns:
                results[f"gt_{f}"].append(np.nan)
                continue
            vals   = group[[f, "cadre_weight"]].dropna(subset=[f])
            if vals.empty:
                results[f"gt_{f}"].append(np.nan)
                continue
            # Weighted average
            wt_avg = (
                vals[f] * vals["cadre_weight"]
            ).sum() / vals["cadre_weight"].sum()
            results[f"gt_{f}"].append(round(wt_avg, 4))

    return pd.DataFrame(results)


# ---------------------------------------------------
# BASELINE STRATEGIES
# ---------------------------------------------------

def most_recent_wins(group, field):
    dated = group[["record_entry_date", field]].dropna(subset=[field]).copy()
    if dated.empty:
        return np.nan
    dated["record_entry_date"] = pd.to_datetime(
        dated["record_entry_date"], dayfirst=True, errors="coerce"
    )
    dated = dated.dropna(subset=["record_entry_date"])
    if dated.empty:
        return group[field].dropna().iloc[0]
    return dated.sort_values("record_entry_date", ascending=False).iloc[0][field]


def highest_source_wins(group, field):
    available = group[["cadre", field]].dropna(subset=[field]).copy()
    if available.empty:
        return np.nan
    available["priority"] = available["cadre"].map(SOURCE_PRIORITY).fillna(99)
    return available.sort_values("priority").iloc[0][field]


def majority_vote(group, field):
    vals = group[field].dropna()
    return vals.mean() if not vals.empty else np.nan


# ---------------------------------------------------
# COMPUTE METRICS
# ---------------------------------------------------

def compute_rmse(y_true, y_pred):
    df = pd.DataFrame({"t": y_true.values, "p": y_pred.values}).dropna()
    if len(df) == 0:
        return np.nan
    return round(np.sqrt(mean_squared_error(df["t"], df["p"])), 4)


# ---------------------------------------------------
# MAIN
# ---------------------------------------------------

def run_baseline_comparison():

    print("Loading data...")

    reliability = pd.read_csv(
        "data/processed/reliability_scored_records.csv",
        low_memory=False
    )

    resolved_all = pd.read_csv(
        "data/processed/resolved_all_records.csv",
        low_memory=False
    )

    raw = pd.read_csv(
        "data/synthetic/unified_health_records.csv",
        low_memory=False
    )

    if "domain" not in reliability.columns:
        reliability["domain"] = "maternal"
    if "domain" not in resolved_all.columns:
        resolved_all["domain"] = "maternal"

    # Standardise cadre names
    reliability["cadre"] = reliability["cadre"].astype(str).str.upper().str.strip()
    raw["cadre"]         = raw["cadre"].astype(str).str.upper().str.strip()

    os.makedirs("results", exist_ok=True)

    all_summary_rows = []

    strategies = {
        "Most-Recent-Wins":     "mrw",
        "Highest-Source-Wins":  "hsw",
        "Majority-Vote":        "mv",
        "Bayesian EM (Ours)":   "bay",
    }

    for domain in ["maternal", "child", "chronic"]:

        fields       = DOMAIN_FIELDS.get(domain, [])
        rel_domain   = reliability[reliability["domain"] == domain]
        res_domain   = resolved_all[resolved_all["domain"] == domain]

        # Ground truth: weighted avg of PHC + ANM
        gt_df        = build_ground_truth(raw, domain, fields)
        actual_fields = [f for f in fields if f"gt_{f}" in gt_df.columns]

        # Build baseline results per patient
        results = {"patient_id": []}
        for strategy in ["mrw", "hsw", "mv"]:
            for f in actual_fields:
                results[f"{strategy}_{f}"] = []

        for pid, group in rel_domain.groupby("patient_id"):
            results["patient_id"].append(pid)
            for f in actual_fields:
                if f not in group.columns:
                    results[f"mrw_{f}"].append(np.nan)
                    results[f"hsw_{f}"].append(np.nan)
                    results[f"mv_{f}"].append(np.nan)
                else:
                    results[f"mrw_{f}"].append(most_recent_wins(group, f))
                    results[f"hsw_{f}"].append(highest_source_wins(group, f))
                    results[f"mv_{f}"].append(majority_vote(group, f))

        baseline_df = pd.DataFrame(results)

        # Merge ground truth + bayesian + baselines
        merged = gt_df.merge(baseline_df, on="patient_id", how="inner")

        bay_cols = {
            f: f"bay_{f}"
            for f in actual_fields
            if f in res_domain.columns
        }
        merged = merged.merge(
            res_domain[["patient_id"] + list(bay_cols.keys())].rename(
                columns=bay_cols
            ),
            on="patient_id", how="inner"
        )

        # Print table
        print(f"\n{'='*90}")
        print(f"DOMAIN: {domain.upper()}")
        print(f"  Ground truth = weighted avg of PHC (w=2) + ANM (w=1) records")
        print(f"{'='*90}")

        header = f"  {'Field':<30}"
        for name in strategies:
            header += f"  {name[:16]:>16}"
        print(header + "  (RMSE)")
        print("-" * 98)

        domain_rows = []

        for f in actual_fields:

            label  = FIELD_LABELS.get(f, f)
            gt_col = f"gt_{f}"
            row    = f"  {label:<30}"
            field_row = {"domain": domain, "field": label}

            for name, prefix in strategies.items():
                pred_col = f"{prefix}_{f}"
                if pred_col not in merged.columns or gt_col not in merged.columns:
                    row += f"  {'N/A':>16}"
                    continue
                rmse = compute_rmse(merged[gt_col], merged[pred_col])
                row += f"  {rmse:>16.4f}"
                field_row[name] = rmse

            print(row)
            domain_rows.append(field_row)

        # Average RMSE
        print("-" * 98)
        avg_row = f"  {'Average RMSE':<30}"
        avg_results = {}

        for name, prefix in strategies.items():
            rmses = []
            for f in actual_fields:
                pred_col = f"{prefix}_{f}"
                gt_col   = f"gt_{f}"
                if pred_col not in merged.columns or gt_col not in merged.columns:
                    continue
                rmse = compute_rmse(merged[gt_col], merged[pred_col])
                if not np.isnan(rmse):
                    rmses.append(rmse)
            avg = round(np.mean(rmses), 4) if rmses else np.nan
            avg_row += f"  {avg:>16.4f}"
            avg_results[name] = avg

        print(avg_row)

        # Improvement of Bayesian EM over best non-Bayesian baseline
        bay_avg = avg_results.get("Bayesian EM (Ours)", np.nan)
        baselines_only = {
            k: v for k, v in avg_results.items()
            if k != "Bayesian EM (Ours)" and not np.isnan(v) and v > 0
        }

        if baselines_only and not np.isnan(bay_avg):
            best_name = min(baselines_only, key=lambda k: baselines_only[k])
            best_rmse = baselines_only[best_name]
            improvement = (best_rmse - bay_avg) / best_rmse * 100
            print(f"\n  Best baseline : {best_name} (RMSE={best_rmse:.4f})")
            print(f"  Bayesian EM   : RMSE={bay_avg:.4f}")
            print(f"  Improvement   : {improvement:.2f}%")

        all_summary_rows.extend(domain_rows)

    summary_df = pd.DataFrame(all_summary_rows)
    summary_df.to_csv("results/baseline_comparison.csv", index=False)
    print(f"\nSaved: results/baseline_comparison.csv")

    return summary_df


if __name__ == "__main__":

    run_baseline_comparison()