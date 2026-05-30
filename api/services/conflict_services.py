from api.services.data_loader import (
    CONFLICTS,
    RELIABILITY,
    RESOLVED,
    FEATURES
)


def get_patient_conflict(patient_id):

    conflict_row = CONFLICTS[
        CONFLICTS["patient_id"] == patient_id
    ]

    if len(conflict_row) == 0:

        return {
            "error": "Patient not found"
        }

    conflict_row = conflict_row.iloc[0]

    source_rows = RELIABILITY[
        RELIABILITY["patient_id"] == patient_id
    ]

    resolved_row = RESOLVED[
        RESOLVED["patient_id"] == patient_id
    ].iloc[0]

    feature_row = FEATURES[
        FEATURES["patient_id"] == patient_id
    ].iloc[0]

    sources = []

    for _, row in source_rows.iterrows():

        sources.append({

            "cadre":
                row["cadre"],

            "haemoglobin":
                float(row["haemoglobin_gdl"]),

            "blood_pressure":
                float(row["systolic_bp"]),

            "blood_sugar":
                float(row["blood_sugar_fasting"]),

            "reliability":
                round(
                    float(
                        row["source_reliability"]
                    ),
                    3
                )
        })

    return {

        "patient_id":
            patient_id,

        "conflict_types":
            conflict_row["conflict_types"],

        "district":
            conflict_row["district"],

        "village":
            conflict_row["village"],

        "sources":
            sources,

        "resolved_values": {

            "haemoglobin":
                float(
                    resolved_row[
                        "haemoglobin_gdl"
                    ]
                ),

            "blood_pressure":
                float(
                    resolved_row[
                        "systolic_bp"
                    ]
                ),

            "blood_sugar":
                float(
                    resolved_row[
                        "blood_sugar_fasting"
                    ]
                )
        },

        "predicted_high_risk":
            int(
                feature_row[
                    "predicted_high_risk"
                ]
            ),

        "risk_score":
            round(
                float(
                    feature_row[
                        "maternal_risk_score"
                    ]
                ),
                2
            )
    }