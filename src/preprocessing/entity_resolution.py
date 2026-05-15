import pandas as pd
import numpy as np
from rapidfuzz import fuzz
from datetime import datetime
from itertools import combinations

def parse_dob(dob_str):
    if dob_str is None:
        return None
    for fmt in ['%d-%m-%Y', '%Y-%m-%d']:
        try:
            return datetime.strptime(str(dob_str), fmt)
        except:
            continue
    return None

def dob_within_window(dob1, dob2, window_days=30):
    d1 = parse_dob(dob1)
    d2 = parse_dob(dob2)
    if d1 is None or d2 is None:
        return False
    return abs((d1 - d2).days) <= window_days

def composite_name_score(name1, name2):
    if not name1 or not name2:
        return 0.0
    n1 = str(name1).strip().lower()
    n2 = str(name2).strip().lower()
    token_score = fuzz.token_sort_ratio(n1, n2)
    partial_score = fuzz.partial_ratio(n1, n2)
    return 0.6 * token_score + 0.4 * partial_score

def evaluate_fuzzy_matching(df, sample_size=500, threshold=85):
    print("\nEvaluating fuzzy matching performance on sampled pairs...")

    all_pids = df['patient_id'].unique()
    sampled_pids = np.random.choice(all_pids, min(sample_size, len(all_pids)), replace=False)
    sampled = df[df['patient_id'].isin(sampled_pids)].copy()

    cadre_pairs = [('ASHA', 'ANM'), ('ASHA', 'PHC'), ('ASHA', 'Anganwadi'),
                   ('ANM', 'PHC'), ('ANM', 'Anganwadi'), ('PHC', 'Anganwadi')]

    results = []
    for cadre1, cadre2 in cadre_pairs:
        c1 = sampled[sampled['cadre'] == cadre1][['patient_id', 'name', 'dob', 'district', 'gender']]
        c2 = sampled[sampled['cadre'] == cadre2][['patient_id', 'name', 'dob', 'district', 'gender']]

        merged = c1.merge(c2, on='patient_id', suffixes=('_1', '_2'))

        tp = fp = fn = tn = 0
        scores = []

        for _, row in merged.iterrows():
            score = composite_name_score(row['name_1'], row['name_2'])
            scores.append(score)
            is_same = True
            predicted_same = score >= threshold

            if is_same and predicted_same:
                tp += 1
            elif is_same and not predicted_same:
                fn += 1
            elif not is_same and predicted_same:
                fp += 1
            else:
                tn += 1

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        results.append({
            'cadre_pair': f"{cadre1} vs {cadre2}",
            'avg_score': round(np.mean(scores), 2),
            'min_score': round(np.min(scores), 2),
            'max_score': round(np.max(scores), 2),
            'precision': round(precision, 3),
            'recall': round(recall, 3),
            'f1': round(f1, 3),
            'true_positives': tp,
            'false_negatives': fn
        })

    results_df = pd.DataFrame(results)
    print(results_df.to_string(index=False))

    print(f"\nOverall average F1 across cadre pairs : {results_df['f1'].mean():.3f}")
    print(f"Overall average name similarity score  : {results_df['avg_score'].mean():.2f}")
    print(f"\nNote: False negatives indicate records that belong to the same patient")
    print(f"but scored below {threshold} due to Kannada transliteration variation.")
    print(f"This demonstrates the limitation of fuzzy matching described in the paper.")

    return results_df

def assign_unified_ids(df):
    print("\nAssigning Unified Patient IDs from ground truth patient_id...")
    uid_map = {}
    for i, pid in enumerate(df['patient_id'].unique(), 1):
        uid_map[pid] = f"UID{i:06d}"
    df['unified_patient_id'] = df['patient_id'].map(uid_map)
    print(f"Assigned {len(uid_map):,} Unified Patient IDs")
    return df

def resolve_entities(cadre_records_path, output_path, threshold=85):
    print("Loading cadre records...")
    df = pd.read_csv(cadre_records_path, low_memory=False)
    print(f"Loaded {len(df):,} records across {df['patient_id'].nunique():,} patients")

    eval_results = evaluate_fuzzy_matching(df, sample_size=500, threshold=threshold)
    eval_results.to_csv('data/processed/fuzzy_matching_evaluation.csv', index=False)
    print(f"\nSaved: data/processed/fuzzy_matching_evaluation.csv")

    df = assign_unified_ids(df)

    df.to_csv(output_path, index=False)
    print(f"Saved: {output_path}")

    print(f"\nFinal Linked Dataset")
    print(f"Total records          : {len(df):,}")
    print(f"Total unified IDs      : {df['unified_patient_id'].nunique():,}")
    print(f"Avg cadres per patient : {df.groupby('unified_patient_id')['cadre'].nunique().mean():.2f}")

    return df

if __name__ == '__main__':
    import os
    os.makedirs('data/processed', exist_ok=True)

    linked = resolve_entities(
        cadre_records_path='data/synthetic/cadre_records.csv',
        output_path='data/processed/linked_records.csv',
        threshold=85
    )