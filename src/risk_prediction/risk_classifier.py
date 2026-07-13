import pandas as pd
import numpy as np
import os
import joblib

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, classification_report,
    confusion_matrix
)

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    print("WARNING: xgboost not installed.")
    XGBOOST_AVAILABLE = False


# ---------------------------------------------------
# FEATURE COLUMNS PER DOMAIN
# Strictly raw continuous clinical measurements only.
# No binary flags derived from the same thresholds
# that define true_high_risk (direct leakage), and
# no comorbidity indicators derived from disease
# assignment logic (indirect leakage).
# ---------------------------------------------------

DOMAIN_FEATURES = {

    "maternal": [
        "haemoglobin_gdl",
        "systolic_bp",
        "diastolic_bp",
        "blood_sugar_fasting",
        "weight_kg",
        "fundal_height_cm",
        "anc_visits_count",
        "gestational_age_weeks",
    ],

    "child": [
        "weight_child_kg",
        "height_cm",
        "muac_cm",
        "waz_score",
        "haz_score",
        "haemoglobin_child",
        "child_age_months",
        "immunization_score",
    ],

    "chronic": [
        # Raw lab measurements only
        # Removed: cardiometabolic_risk (= diabetes+hypertension flag)
        # Removed: tb_hiv_comorbidity (= disease assignment flag)
        "fasting_blood_sugar",
        "postprandial_blood_sugar",
        "hba1c",
        "bp_systolic_reading1",
        "bp_diastolic_reading1",
        "creatinine",
        "bmi",
        "missed_doses_count",
    ],
}


def prepare_data(df_domain, domain):

    feature_cols = [
        f for f in DOMAIN_FEATURES[domain]
        if f in df_domain.columns
    ]

    X = df_domain[feature_cols].copy()
    y = df_domain["true_high_risk"].copy()

    valid = X.dropna(how="all").index
    X = X.loc[valid]
    y = y.loc[valid]

    X = X.fillna(X.median(numeric_only=True))

    return X, y, feature_cols


def run_cv(model, X, y, cv=5):
    """5-fold stratified CV — returns mean and std F1."""
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
    scores = cross_val_score(model, X, y, cv=skf, scoring="f1", n_jobs=-1)
    return round(scores.mean(), 4), round(scores.std(), 4)


def evaluate_model(model, X_train, X_test, y_train, y_test, X_all, y_all, name):

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    # CV on full data
    cv_mean, cv_std = run_cv(
        model.__class__(**model.get_params()),
        X_all, y_all
    )

    metrics = {
        "model":     name,
        "accuracy":  round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "recall":    round(recall_score(y_test, y_pred, zero_division=0), 4),
        "f1":        round(f1_score(y_test, y_pred, zero_division=0), 4),
        "auc_roc":   round(roc_auc_score(y_test, y_prob), 4),
        "cv_f1_mean": cv_mean,
        "cv_f1_std":  cv_std,
    }

    print(f"\n    [{name}]")
    print(f"    Accuracy      : {metrics['accuracy']:.4f}")
    print(f"    Precision     : {metrics['precision']:.4f}")
    print(f"    Recall        : {metrics['recall']:.4f}")
    print(f"    F1 Score      : {metrics['f1']:.4f}")
    print(f"    AUC-ROC       : {metrics['auc_roc']:.4f}")
    print(f"    5-Fold CV F1  : {cv_mean:.4f} ± {cv_std:.4f}")

    report = classification_report(
        y_test, y_pred,
        target_names=["Normal", "High Risk"]
    )
    for line in report.split("\n"):
        print(f"      {line}")

    cm = confusion_matrix(y_test, y_pred)
    print(f"    Confusion Matrix:")
    print(f"      {cm[0]}")
    print(f"      {cm[1]}")

    return model, metrics


def train_domain(df_domain, domain):

    print(f"\n  Domain: {domain.upper()} ({len(df_domain):,} patients)")
    print(f"  {'─'*55}")

    X, y, feature_cols = prepare_data(df_domain, domain)

    if y.nunique() < 2:
        print(f"  Only one class — skipping")
        return None, None

    hr_pct = round(y.mean() * 100, 1)
    print(f"  Features   : {len(feature_cols)} (raw continuous measurements only)")
    print(f"  High Risk  : {int(y.sum()):,} / {len(y):,} ({hr_pct}%)")
    print(f"  Feature list: {feature_cols}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    results = []
    trained_models = {}
    all_imp = []

    # ── Random Forest ────────────────────────────
    rf = RandomForestClassifier(
        n_estimators=300,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )

    rf_model, rf_metrics = evaluate_model(
        rf, X_train, X_test, y_train, y_test, X, y, "Random Forest"
    )
    rf_metrics.update({
        "domain": domain, "high_risk_pct": hr_pct,
        "n_train": len(X_train), "n_test": len(X_test),
    })
    results.append(rf_metrics)
    trained_models["rf"] = rf_model

    rf_imp = pd.DataFrame({
        "feature": feature_cols,
        "importance": rf_model.feature_importances_,
        "model": "Random Forest", "domain": domain,
    }).sort_values("importance", ascending=False)

    print(f"\n    Top Features (RF):")
    for _, row in rf_imp.head(5).iterrows():
        print(f"      {row['feature']:<35}: {row['importance']:.4f}")
    all_imp.append(rf_imp)

    # ── XGBoost ──────────────────────────────────
    if XGBOOST_AVAILABLE:

        neg = int((y_train == 0).sum())
        pos = int((y_train == 1).sum())
        scale_pos = round(neg / pos, 2) if pos > 0 else 1

        xgb = XGBClassifier(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=scale_pos,
            eval_metric="logloss",
            random_state=42,
            verbosity=0,
        )

        xgb_model, xgb_metrics = evaluate_model(
            xgb, X_train, X_test, y_train, y_test, X, y, "XGBoost"
        )
        xgb_metrics.update({
            "domain": domain, "high_risk_pct": hr_pct,
            "n_train": len(X_train), "n_test": len(X_test),
        })
        results.append(xgb_metrics)
        trained_models["xgb"] = xgb_model

        xgb_imp = pd.DataFrame({
            "feature": feature_cols,
            "importance": xgb_model.feature_importances_,
            "model": "XGBoost", "domain": domain,
        }).sort_values("importance", ascending=False)

        print(f"\n    Top Features (XGBoost):")
        for _, row in xgb_imp.head(5).iterrows():
            print(f"      {row['feature']:<35}: {row['importance']:.4f}")
        all_imp.append(xgb_imp)

        best_model = xgb_model if xgb_metrics["f1"] >= rf_metrics["f1"] else rf_model
        best_name  = "XGBoost" if xgb_metrics["f1"] >= rf_metrics["f1"] else "Random Forest"

    else:
        best_model = rf_model
        best_name  = "Random Forest"

    print(f"\n    Best model for {domain}: {best_name}")

    os.makedirs("models/trained", exist_ok=True)
    joblib.dump(best_model, f"models/trained/risk_classifier_{domain}.pkl")
    for key, model in trained_models.items():
        joblib.dump(model, f"models/trained/risk_classifier_{domain}_{key}.pkl")

    return results, pd.concat(all_imp, ignore_index=True)


def train_risk_classifier():

    print("Loading feature dataset...")

    df = pd.read_csv("data/processed/final_features.csv", low_memory=False)

    if "domain" not in df.columns:
        df["domain"] = "maternal"

    os.makedirs("models/trained", exist_ok=True)
    os.makedirs("results", exist_ok=True)

    all_metrics     = []
    all_importances = []

    print("\n" + "=" * 65)
    print("TRAINING RISK CLASSIFIERS")
    print("Raw continuous measurements only — no engineered leakage")
    print("=" * 65)

    for domain in ["maternal", "child", "chronic"]:

        domain_df = df[df["domain"] == domain].copy()

        if domain_df.empty:
            print(f"\nNo data for {domain} — skipping")
            continue

        results, imp_df = train_domain(domain_df, domain)

        if results is None:
            continue

        all_metrics.extend(results)
        if imp_df is not None:
            all_importances.append(imp_df)

    # ── Summary ──────────────────────────────────
    print("\n" + "=" * 80)
    print("COMBINED RESULTS SUMMARY")
    print("=" * 80)

    metrics_df = pd.DataFrame(all_metrics)

    for domain in ["maternal", "child", "chronic"]:
        dm = metrics_df[metrics_df["domain"] == domain]
        if dm.empty:
            continue
        print(f"\n{domain.upper()}")
        print(f"  {'Model':<20} {'Acc':>8} {'Prec':>8} {'Rec':>8} {'F1':>8} {'AUC':>8} {'CV F1':>14}")
        print(f"  {'-'*76}")
        for _, r in dm.iterrows():
            print(
                f"  {r['model']:<20} "
                f"{r['accuracy']:>8.4f} "
                f"{r['precision']:>8.4f} "
                f"{r['recall']:>8.4f} "
                f"{r['f1']:>8.4f} "
                f"{r['auc_roc']:>8.4f} "
                f"  {r['cv_f1_mean']:.4f}±{r['cv_f1_std']:.4f}"
            )

    print(f"\nMACRO AVERAGES")
    print(f"  {'-'*76}")
    for model_name in metrics_df["model"].unique():
        m = metrics_df[metrics_df["model"] == model_name]
        print(
            f"  {model_name:<20} "
            f"F1={m['f1'].mean():.4f}  "
            f"AUC={m['auc_roc'].mean():.4f}  "
            f"CV F1={m['cv_f1_mean'].mean():.4f}±{m['cv_f1_std'].mean():.4f}"
        )

    metrics_df.to_csv("results/risk_classifier_metrics.csv", index=False)

    if all_importances:
        pd.concat(all_importances, ignore_index=True).to_csv(
            "results/feature_importance.csv", index=False
        )

    print("\nSaved: results/risk_classifier_metrics.csv")

    return metrics_df


if __name__ == "__main__":
    train_risk_classifier()