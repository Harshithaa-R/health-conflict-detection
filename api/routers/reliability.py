from fastapi import APIRouter

from api.services.data_loader import (
    RELIABILITY
)

router = APIRouter(
    prefix="/reliability",
    tags=["Reliability"]
)


@router.get("/")
def reliability_scores():

    result = (

        RELIABILITY

        .groupby("cadre")[
            "source_reliability"
        ]

        .mean()

        .reset_index()
    )

    return result.to_dict(
        orient="records"
    )