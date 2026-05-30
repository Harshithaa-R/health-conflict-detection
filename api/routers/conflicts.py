from fastapi import APIRouter

from api.services.data_loader import (
    CONFLICTS
)

from api.services.conflict_services import (
    get_patient_conflict
)

router = APIRouter(
    prefix="/conflicts",
    tags=["Conflicts"]
)


@router.get("/summary")
def conflict_summary():

    total = len(CONFLICTS)

    conflict_count = len(

        CONFLICTS[
            CONFLICTS[
                "conflict_types"
            ] != "no_conflict"
        ]
    )

    return {

        "patients_analysed":
            int(total),

        "patients_with_conflicts":
            int(conflict_count)
    }


@router.get("/")
def all_conflicts():

    return CONFLICTS.head(
        100
    ).to_dict(
        orient="records"
    )


@router.get("/{patient_id}")
def patient_conflict(
    patient_id: str
):

    return get_patient_conflict(
        patient_id
    )