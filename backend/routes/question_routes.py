
from fastapi import APIRouter, HTTPException

from backend.schemas.question_schema import (
    QuestionRetrievalRequest,
    QuestionRetrievalResponse,
    QuestionGenerationRequest,
    QuestionGenerationResponse,
)

from backend.services.question_service import retrieve_questions
from backend.services.question_generation_service import (
    generate_missing_questions,
)

router = APIRouter(
    prefix="/questions",
    tags=["Question Bank"],
)


@router.post(
    "/retrieve",
    response_model=QuestionRetrievalResponse,
)
def retrieve_assessment_questions(
    request: QuestionRetrievalRequest,
):
    try:
        return retrieve_questions(request.blueprint)

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=500,
            detail="Question bank file is missing.",
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Question retrieval failed.",
        ) from exc


@router.post(
    "/generate",
    response_model=QuestionGenerationResponse,
)
def generate_assessment_questions(
    request: QuestionGenerationRequest,
):
    try:
        return generate_missing_questions(request)

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Question generation failed.",
        ) from exc
