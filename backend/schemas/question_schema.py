from typing import Literal

from pydantic import BaseModel, Field


QuestionType = Literal[
    "mcq",
    "coding",
    "short_answer",
    "scenario_based",
]

Difficulty = Literal["easy", "medium", "hard"]


class Question(BaseModel):
    id: str
    question: str
    skill: str
    difficulty: Difficulty
    question_type: QuestionType
    marks: int = Field(ge=1)

    options: list[str] = Field(default_factory=list)
    correct_answer: str | None = None
    explanation: str | None = None


class QuestionRetrievalRequest(BaseModel):
    blueprint: dict


class QuestionGap(BaseModel):
    skill: str
    required: int
    retrieved: int
    missing: int


class QuestionRetrievalResponse(BaseModel):
    selected_questions: list[Question]
    gaps: list[QuestionGap]
    total_retrieved: int


class QuestionGenerationRequest(BaseModel):
    blueprint: dict
    retrieval_result: QuestionRetrievalResponse


class GeneratedQuestionList(BaseModel):
    questions: list[Question]


class QuestionGenerationResponse(BaseModel):
    generated_questions: list[Question]
    total_generated: int
    remaining_gaps: list[QuestionGap]