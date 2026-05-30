import pandas as pd

FEATURES = pd.read_csv(
    "data/processed/final_features.csv"
)

CONFLICTS = pd.read_csv(
    "data/processed/measurement_conflicts.csv"
)

RELIABILITY = pd.read_csv(
    "data/processed/reliability_scored_records.csv"
)

RESOLVED = pd.read_csv(
    "data/processed/resolved_maternal_records.csv"
)