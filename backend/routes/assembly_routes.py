
from fastapi import APIRouter, HTTPException

from backend.schemas.assembly_schema import (
    AssessmentAssemblyRequest,
    AssessmentAssemblyResponse,
)
from backend.services.assembly_service import assemble_assessment

router = APIRouter(
    prefix="/assessments",
    tags=["Assessment Assembly"],
)


@router.post(
    "/assemble",
    response_model=AssessmentAssemblyResponse,
)
def create_complete_assessment(
    request: AssessmentAssemblyRequest,
):
    try:
        return assemble_assessment(request)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Assessment assembly failed: {str(exc)}",
        ) from exc
