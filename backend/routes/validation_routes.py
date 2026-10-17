
from fastapi import APIRouter, HTTPException

from backend.schemas.validation_schema import (
    AssessmentValidationRequest,
    AssessmentValidationResponse,
)
from backend.services.validation_service import validate_assessment

router = APIRouter(
    prefix="/assessments",
    tags=["Assessment Validation"],
)


@router.post(
    "/validate",
    response_model=AssessmentValidationResponse,
)
def validate_complete_assessment(
    request: AssessmentValidationRequest,
):
    try:
        return validate_assessment(request)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Assessment validation failed: {str(exc)}",
        ) from exc
