"""
Run this from your project root:
  python extract_paper_metrics.py

Paste the output back to Claude — it has everything needed for the paper.
"""
import pandas as pd
import numpy as np
from sklearn.metrics import (
    precision_score, recall_score, f1_score,
    accuracy_score, mean_squared_error, classification_report
)
import warnings
warnings.filterwarnings("ignore")

SEP = "=" * 60

def section(title):
    print(f"\n{SEP}\n{title}\n{SEP}")

# ── 1. Dataset overview ──────────────────────────────────────
section("1. DATASET OVERVIEW")
try:
    features  = pd.read_csv("data/processed/final_features.csv")
    conflicts = pd.read_csv("data/processed/measurement_conflicts.csv")
    resolved  = pd.read_csv("data/processed/resolved_maternal_records.csv")
    reliability = pd.read_csv("data/processed/reliability_scored_records.csv")

    print(f"Total patients                : {len(features):,}")
    print(f"Total source records          : {len(reliability):,}  ({reliability['cadre'].nunique()} cadres)")
    print(f"Cadre distribution            : {dict(reliability['cadre'].value_counts())}")
    print(f"Districts covered             : {features['district'].nunique()}")
    print(f"District list                 : {sorted(features['district'].unique().tolist())}")
except Exception as e:
    print(f"ERROR: {e}")

# ── 2. Conflict detection metrics ────────────────────────────
section("2. CONFLICT DETECTION")
try:
    total      = len(conflicts)
    with_conf  = int((conflicts["conflict_types"] != "no_conflict").sum())
    no_conf    = total - with_conf
    conf_rate  = with_conf / total * 100

    print(f"Patients analysed             : {total:,}")
    print(f"Patients with conflicts       : {with_conf:,}  ({conf_rate:.1f}%)")
    print(f"Patients without conflicts    : {no_conf:,}  ({100-conf_rate:.1f}%)")

    # Conflict type breakdown
    type_counts = {}
    for _, row in conflicts[conflicts["conflict_types"] != "no_conflict"].iterrows():
        for t in str(row["conflict_types"]).split(","):
            t = t.strip()
            type_counts[t] = type_counts.get(t, 0) + 1

    print("\nConflict type breakdown:")
    labels = {
        "haemoglobin_conflict":    "Haemoglobin",
        "blood_pressure_conflict": "Blood Pressure",
        "blood_sugar_conflict":    "Blood Sugar",
        "anc_visit_conflict":      "ANC Visits",
        "weight_conflict":         "Body Weight",
        "fundal_height_conflict":  "Fundal Height",
    }
    for k, v in sorted(type_counts.items(), key=lambda x: -x[1]):
        pct = v / with_conf * 100
        print(f"  {labels.get(k, k):<28}: {v:>5,}  ({pct:.1f}%)")

    # Multi-conflict distribution
    print("\nNum conflicts per patient:")
    for n, cnt in conflicts["num_conflicts"].value_counts().sort_index().items():
        print(f"  {n} conflict(s): {cnt:,} patients")

except Exception as e:
    print(f"ERROR: {e}")

# ── 3. Source reliability ─────────────────────────────────────
section("3. SOURCE RELIABILITY SCORES")
try:
    rel_mean = reliability.groupby("cadre")["source_reliability"].agg(["mean","std","min","max"])
    for cadre, row in rel_mean.iterrows():
        print(f"  {cadre:<12}: mean={row['mean']:.4f}  std={row['std']:.4f}  min={row['min']:.4f}  max={row['max']:.4f}")
    print(f"\n  Overall mean reliability      : {reliability['source_reliability'].mean():.4f}")
except Exception as e:
    print(f"ERROR: {e}")

# ── 4. Bayesian EM resolution quality ────────────────────────
section("4. BAYESIAN EM RESOLUTION (vs ground truth)")
try:
    # Use the synthetic dataset ground truth
    raw = pd.read_csv("data/synthetic/maternal_records.csv")
    ground_truth = raw[raw["cadre"] == "PHC"][["patient_id","haemoglobin_gdl","systolic_bp","blood_sugar_fasting","weight_kg","fundal_height_cm","anc_visits_count"]].copy()
    ground_truth.columns = ["patient_id","gt_hb","gt_bp","gt_bs","gt_wt","gt_fh","gt_anc"]

    merged = resolved.merge(ground_truth, on="patient_id", how="inner")

    fields = [
        ("haemoglobin_gdl",     "gt_hb",  "Haemoglobin (g/dL)"),
        ("systolic_bp",         "gt_bp",  "Systolic BP (mmHg)"),
        ("blood_sugar_fasting",  "gt_bs",  "Blood Sugar (mg/dL)"),
        ("weight_kg",           "gt_wt",  "Weight (kg)"),
        ("fundal_height_cm",    "gt_fh",  "Fundal Height (cm)"),
        ("anc_visits_count",    "gt_anc", "ANC Visits"),
    ]

    print(f"\n{'Field':<26} {'RMSE':>8}  {'MAE':>8}  {'R²':>8}")
    print("-" * 55)
    for res_col, gt_col, label in fields:
        if res_col in merged.columns and gt_col in merged.columns:
            y_true = merged[gt_col].dropna()
            y_pred = merged[res_col].dropna()
            idx    = merged[[gt_col, res_col]].dropna().index
            y_true = merged.loc[idx, gt_col]
            y_pred = merged.loc[idx, res_col]
            rmse   = np.sqrt(mean_squared_error(y_true, y_pred))
            mae    = np.abs(y_true - y_pred).mean()
            ss_res = ((y_true - y_pred)**2).sum()
            ss_tot = ((y_true - y_true.mean())**2).sum()
            r2     = 1 - ss_res/ss_tot if ss_tot > 0 else float("nan")
            print(f"  {label:<24} {rmse:>8.4f}  {mae:>8.4f}  {r2:>8.4f}")

    # Also compare a naive baseline (simple mean of all sources)
    print("\nBaseline comparison — simple mean of all sources:")
    naive = reliability.groupby("patient_id")[["haemoglobin_gdl","systolic_bp","blood_sugar_fasting","weight_kg","fundal_height_cm","anc_visits_count"]].mean().reset_index()
    naive.columns = ["patient_id","n_hb","n_bp","n_bs","n_wt","n_fh","n_anc"]
    mn = ground_truth.merge(naive, on="patient_id", how="inner")

    naive_fields = [
        ("n_hb",  "gt_hb",  "Haemoglobin"),
        ("n_bp",  "gt_bp",  "Systolic BP"),
        ("n_bs",  "gt_bs",  "Blood Sugar"),
        ("n_wt",  "gt_wt",  "Weight"),
        ("n_fh",  "gt_fh",  "Fundal Height"),
        ("n_anc", "gt_anc", "ANC Visits"),
    ]
    print(f"\n{'Field':<20} {'Naive RMSE':>12}  {'Bayesian RMSE':>14}  {'Improvement':>12}")
    print("-" * 62)
    for (nf, gf, label), (rf, _, _) in zip(naive_fields, fields):
        idx  = mn[[gf, nf]].dropna().index
        n_rmse = np.sqrt(mean_squared_error(mn.loc[idx, gf], mn.loc[idx, nf]))
        idx2 = merged[[gt_col, res_col]].dropna().index
        # recompute per field
        idx2 = merged[[gf.replace("gt_","").replace("gt_",""), gf]].dropna().index if gf in merged else merged.index
        # simpler:
        yt2 = merged[gf] if gf in merged.columns else None
        yp2 = merged[rf] if rf in merged.columns else None
        if yt2 is not None and yp2 is not None:
            idx2 = merged[[gf, rf]].dropna().index
            b_rmse = np.sqrt(mean_squared_error(merged.loc[idx2, gf], merged.loc[idx2, rf]))
            impr = (n_rmse - b_rmse) / n_rmse * 100
            print(f"  {label:<18} {n_rmse:>12.4f}  {b_rmse:>14.4f}  {impr:>11.1f}%")

except Exception as e:
    print(f"ERROR: {e}")

# ── 5. Risk prediction performance ───────────────────────────
section("5. RISK PREDICTION PERFORMANCE")
try:
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier

    feature_cols = [
        "haemoglobin_gdl","systolic_bp","blood_sugar_fasting",
        "weight_kg","fundal_height_cm","anc_visits_count",
        "severe_anaemia","hypertension_risk","diabetes_risk",
        "low_weight_risk","fundal_height_risk","poor_anc_coverage"
    ]

    X = features[feature_cols]
    y = features["true_high_risk"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = RandomForestClassifier(n_estimators=300, max_depth=12, class_weight="balanced", random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    from sklearn.metrics import roc_auc_score
    print(f"Accuracy   : {accuracy_score(y_test, y_pred):.4f}")
    print(f"Precision  : {precision_score(y_test, y_pred):.4f}")
    print(f"Recall     : {recall_score(y_test, y_pred):.4f}")
    print(f"F1 Score   : {f1_score(y_test, y_pred):.4f}")
    print(f"AUC-ROC    : {roc_auc_score(y_test, y_prob):.4f}")
    print(f"\nHigh risk patients : {int(y.sum()):,} ({y.mean()*100:.1f}%)")
    print(f"Normal patients    : {int((y==0).sum()):,} ({(1-y.mean())*100:.1f}%)")

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Normal","High Risk"]))

    # Feature importance top 6
    imp = sorted(zip(feature_cols, model.feature_importances_), key=lambda x: -x[1])
    print("Top feature importances:")
    for feat, score in imp[:6]:
        print(f"  {feat:<30}: {score:.4f}")

except Exception as e:
    print(f"ERROR: {e}")

# ── 6. Entity resolution ─────────────────────────────────────
section("6. ENTITY RESOLUTION")
try:
    linked = pd.read_csv("data/processed/linked_records.csv")
    print(f"Total source records          : {len(linked):,}")
    print(f"Unified patient entities      : {linked['unified_patient_id'].nunique():,}")
    print(f"Avg records per entity        : {len(linked)/linked['unified_patient_id'].nunique():.2f}")
    print(f"Cadre coverage per entity     : {linked.groupby('unified_patient_id')['cadre'].nunique().mean():.2f} avg cadres")

    # Precision proxy: patient_id consistency within cluster
    cluster_purity = linked.groupby("unified_patient_id")["patient_id"].nunique()
    pure = (cluster_purity == 1).sum()
    total_clusters = len(cluster_purity)
    print(f"Cluster purity (1 true patient/cluster): {pure}/{total_clusters} = {pure/total_clusters*100:.1f}%")
    print(f"Estimated precision           : {pure/total_clusters:.4f}")

    # Recall proxy: how many true patients have all 4 cadres linked
    full_link = (linked.groupby("patient_id")["cadre"].nunique() == 4).sum()
    total_patients = linked["patient_id"].nunique()
    print(f"Patients with all 4 cadres linked: {full_link}/{total_patients} = {full_link/total_patients*100:.1f}%")

except Exception as e:
    print(f"ERROR: {e}")

print(f"\n{SEP}\nDone — paste this output back to Claude\n{SEP}\n")