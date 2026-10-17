
from pydantic import BaseModel, Field

from backend.schemas.question_schema import (
    Question,
    QuestionRetrievalResponse,
    QuestionGenerationResponse,
    QuestionGap,
)


class AssessmentAssemblyRequest(BaseModel):
    blueprint: dict
    retrieval_result: QuestionRetrievalResponse
    generation_result: QuestionGenerationResponse


class AssessmentAssemblyResponse(BaseModel):
    assessment_title: str
    duration_minutes: int | None = None
    total_questions: int
    total_marks: int
    questions: list[Question]
    question_type_distribution: dict[str, int]
    difficulty_distribution: dict[str, int]
    skill_distribution: dict[str, int]
    remaining_gaps: list[QuestionGap] = Field(default_factory=list)
