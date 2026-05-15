import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
import json
import os

np.random.seed(42)


def inject_age_conflicts(df):
    df = df.copy()

    if 'dob' not in df.columns or 'cadre' not in df.columns:
        return df

    df['dob'] = pd.to_datetime(df['dob'], errors='coerce')

    current_year = pd.Timestamp.now().year

    df['base_age'] = current_year - df['dob'].dt.year

    def modify_age(row):
        age = row['base_age']

        if pd.isna(age):
            return np.nan

        cadre = str(row['cadre']).strip()

        if cadre == 'ASHA':
            if np.random.rand() < 0.30:
                return max(0, age + np.random.choice([-1, 1]))

        elif cadre == 'ANM':
            if np.random.rand() < 0.05:
                return max(0, age + np.random.choice([-1, 1]))

        elif cadre == 'PHC':
            if np.random.rand() < 0.15:
                return max(0, age + np.random.choice([-2, -1, 1, 2]))

        elif cadre == 'Anganwadi':
            if np.random.rand() < 0.25:
                return max(0, age - 1)

        return age

    df['age'] = df.apply(modify_age, axis=1)

    df.drop(columns=['base_age'], inplace=True)

    return df


def evaluate_conflict_resolution():

    linked_path = 'data/processed/linked_records.csv'
    truth_path = 'data/synthetic/ground_truth.csv'

    if not os.path.exists(linked_path):
        print(f"❌ File not found: {linked_path}")
        return

    if not os.path.exists(truth_path):
        print(f"❌ File not found: {truth_path}")
        return

    linked_df = pd.read_csv(linked_path, low_memory=False)
    ground_truth_df = pd.read_csv(truth_path, low_memory=False)

    if linked_df.empty:
        print("❌ linked_records.csv is empty")
        return

    if ground_truth_df.empty:
        print("❌ ground_truth.csv is empty")
        return

    linked_df = inject_age_conflicts(linked_df)

    if 'dob' in linked_df.columns:
        linked_df['dob'] = pd.to_datetime(
            linked_df['dob'],
            errors='coerce'
        )

        current_year = pd.Timestamp.now().year

        linked_df['true_age'] = (
            current_year - linked_df['dob'].dt.year
        )

    if 'patient_id' not in linked_df.columns:
        print("❌ patient_id missing in linked_records.csv")
        return

    if 'patient_id' not in ground_truth_df.columns:
        print("❌ patient_id missing in ground_truth.csv")
        return

    eval_df = linked_df.merge(
        ground_truth_df,
        on='patient_id',
        how='inner'
    )

    if eval_df.empty:
        print("❌ No matching patient IDs found")
        return

    fields_map = {
        'age': ('age', 'true_age'),
        'weight': ('weight_kg', 'true_weight_kg'),
        'bp_systolic': ('systolic_bp', 'true_systolic_bp'),
        'hemoglobin': ('haemoglobin_gdl', 'true_haemoglobin_gdl')
    }

    results = {}

    for field, (source_field, true_field) in fields_map.items():

        print(f"\n{'=' * 60}")
        print(f"EVALUATING: {field.upper()}")
        print(f"{'=' * 60}")

        if source_field not in eval_df.columns:
            print(f"⚠️ Missing column: {source_field}")
            continue

        if true_field not in eval_df.columns:
            print(f"⚠️ Missing column: {true_field}")
            continue

        baseline_vals = []
        true_vals = []

        grouped = eval_df.groupby('patient_id')

        for _, group in grouped:

            source_vals = pd.to_numeric(
                group[source_field],
                errors='coerce'
            ).dropna()

            if len(source_vals) == 0:
                continue

            true_val = pd.to_numeric(
                pd.Series([group[true_field].iloc[0]]),
                errors='coerce'
            ).iloc[0]

            if pd.isna(true_val):
                continue

            baseline_vals.append(float(np.median(source_vals)))
            true_vals.append(float(true_val))

        if len(true_vals) == 0:
            print("⚠️ No valid records found")
            continue

        baseline_mae = mean_absolute_error(
            true_vals,
            baseline_vals
        )

        baseline_rmse = np.sqrt(
            mean_squared_error(
                true_vals,
                baseline_vals
            )
        )

        print("\nBaseline:")
        print(f"  MAE:  {baseline_mae:.4f}")
        print(f"  RMSE: {baseline_rmse:.4f}")
        print(f"  Records evaluated: {len(baseline_vals)}")

        results[field] = {
            'baseline_mae': round(float(baseline_mae), 4),
            'baseline_rmse': round(float(baseline_rmse), 4),
            'records_evaluated': int(len(baseline_vals))
        }

    os.makedirs('results', exist_ok=True)

    with open('results/evaluation.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\n✓ Results saved to results/evaluation.json")


if __name__ == "__main__":
    evaluate_conflict_resolution()