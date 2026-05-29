import os

print("\n" + "=" * 60)
print("MATERNAL HEALTH CONFLICT RESOLUTION PIPELINE")
print("=" * 60)

# ---------------------------------------------------
# STEP 1
# ---------------------------------------------------

print("\nSTEP 1: GENERATING DATASETS\n")

os.system(
    "python src/data_generation/generate_maternal_dataset.py"
)

# ---------------------------------------------------
# STEP 2
# ---------------------------------------------------

print("\nSTEP 2: STANDARDIZATION\n")

os.system(
    "python src/ingestion/standardizer.py"
)

# ---------------------------------------------------
# STEP 3
# ---------------------------------------------------

print("\nSTEP 3: BLOCKING\n")

os.system(
    "python src/preprocessing/blocker.py"
)

# ---------------------------------------------------
# STEP 4
# ---------------------------------------------------

print("\nSTEP 4: ENTITY RESOLUTION\n")

os.system(
    "python src/preprocessing/entity_resolution.py"
)

# ---------------------------------------------------
# STEP 5
# ---------------------------------------------------

print("\nSTEP 5: CONFLICT DETECTION\n")

os.system(
    "python src/conflict_detection/measurement_conflict.py"
)

# ---------------------------------------------------
# STEP 6
# ---------------------------------------------------

print("\nSTEP 6: RELIABILITY SCORING\n")

os.system(
    "python src/resolution/reliability_scorer.py"
)

# ---------------------------------------------------
# STEP 7
# ---------------------------------------------------

print("\nSTEP 7: BAYESIAN RESOLUTION\n")

os.system(
    "python src/resolution/bayesian_em.py"
)

# ---------------------------------------------------
# STEP 8
# ---------------------------------------------------

print("\nSTEP 8: FEATURE ENGINEERING\n")

os.system(
    "python src/risk_prediction/feature_builder.py"
)

# ---------------------------------------------------
# STEP 9
# ---------------------------------------------------

print("\nSTEP 9: RISK CLASSIFICATION\n")

os.system(
    "python src/risk_prediction/risk_classifier.py"
)

# ---------------------------------------------------
# COMPLETE
# ---------------------------------------------------

print("\n" + "=" * 60)
print("PIPELINE EXECUTED SUCCESSFULLY")
print("=" * 60)