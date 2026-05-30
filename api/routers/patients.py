from fastapi import APIRouter

from api.services.data_loader import (
    FEATURES
)

router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


@router.get("/summary")
def patient_summary():

    return {

        "total_patients":
            int(len(FEATURES)),

        "high_risk_patients":
            int(
                FEATURES[
                    "predicted_high_risk"
                ].sum()
            ),

        "normal_patients":
            int(
                len(FEATURES)
                -
                FEATURES[
                    "predicted_high_risk"
                ].sum()
            )
    }


@router.get("/high-risk")
def high_risk_patients():

    data = FEATURES[
        FEATURES[
            "predicted_high_risk"
        ] == 1
    ]

    return data.head(
        100
    ).to_dict(
        orient="records"
    )