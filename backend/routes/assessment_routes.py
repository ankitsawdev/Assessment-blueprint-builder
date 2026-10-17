
from fastapi import APIRouter, HTTPException

from backend.schemas.assessment_schema import (
    AssessmentRequest,
    AssessmentBlueprint,
)

from backend.services.assessment_service import (
    generate_assessment_blueprint,
)

router = APIRouter(
    prefix="/assessments",
    tags=["Assessments"],
)


@router.post(
    "/blueprint",
    response_model=AssessmentBlueprint
)
def create_assessment_blueprint(
    request: AssessmentRequest
):
    try:
        return generate_assessment_blueprint(request)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Assessment blueprint generation failed.",
        ) from exc
