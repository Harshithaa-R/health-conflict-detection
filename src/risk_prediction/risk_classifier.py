import pandas as pd
import numpy as np
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

import joblib


def train_risk_classifier():

    print(
        "Loading feature dataset..."
    )

    df = pd.read_csv(
        "data/processed/final_features.csv"
    )

    # ---------------------------------------------------
    # FEATURES
    # ---------------------------------------------------

    feature_cols = [

        "haemoglobin_gdl",
        "systolic_bp",
        "blood_sugar_fasting",
        "weight_kg",
        "fundal_height_cm",
        "anc_visits_count",

        "severe_anaemia",
        "hypertension_risk",
        "diabetes_risk",
        "low_weight_risk",
        "fundal_height_risk",
        "poor_anc_coverage"
    ]

    X = df[feature_cols]

    y = df["true_high_risk"]

    # ---------------------------------------------------
    # TRAIN TEST SPLIT
    # ---------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(

        X,
        y,

        test_size=0.2,
        random_state=42,

        stratify=y
    )

    # ---------------------------------------------------
    # MODEL
    # ---------------------------------------------------

    model = RandomForestClassifier(

        n_estimators=300,

        max_depth=12,

        min_samples_split=4,

        min_samples_leaf=2,

        class_weight="balanced",

        random_state=42
    )
    model.fit(
        X_train,
        y_train
    )

    # ---------------------------------------------------
    # PREDICTIONS
    # ---------------------------------------------------

    y_pred = model.predict(
        X_test
    )

    # ---------------------------------------------------
    # METRICS
    # ---------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    precision = precision_score(
        y_test,
        y_pred
    )

    recall = recall_score(
        y_test,
        y_pred
    )

    f1 = f1_score(
        y_test,
        y_pred
    )

    print("\nRisk Prediction Results")
    print("=" * 50)

    print(
        f"Accuracy  : {accuracy:.4f}"
    )

    print(
        f"Precision : {precision:.4f}"
    )

    print(
        f"Recall    : {recall:.4f}"
    )

    print(
        f"F1 Score  : {f1:.4f}"
    )

    print("\nConfusion Matrix")

    print(
        confusion_matrix(
            y_test,
            y_pred
        )
    )

    print("\nClassification Report")

    print(
        classification_report(
            y_test,
            y_pred
        )
    )

    # ---------------------------------------------------
    # FEATURE IMPORTANCE
    # ---------------------------------------------------

    importance_df = pd.DataFrame({

        "feature":
            feature_cols,

        "importance":
            model.feature_importances_
    })

    importance_df = importance_df.sort_values(
        by="importance",
        ascending=False
    )

    print("\nTop Feature Importance")

    print(
        importance_df.head(10)
    )

    # ---------------------------------------------------
    # SAVE MODEL
    # ---------------------------------------------------

    os.makedirs(
        "models/trained",
        exist_ok=True
    )

    joblib.dump(

        model,

        "models/trained/risk_classifier.pkl"
    )

    importance_df.to_csv(

        "results/feature_importance.csv",

        index=False
    )

    print(
        "\nSaved:"
        " models/trained/risk_classifier.pkl"
    )

    return model


if __name__ == "__main__":

    train_risk_classifier()