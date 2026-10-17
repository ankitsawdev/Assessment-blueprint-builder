
from typing import Literal
from pydantic import BaseModel, Field, model_validator

from backend.schemas.jd_schema import JobDescriptionResponse


QuestionType = Literal[
    "mcq",
    "coding",
    "short_answer",
    "scenario_based"
]

Difficulty = Literal["easy", "medium", "hard"]


class AssessmentConfig(BaseModel):
    total_questions: int = Field(default=20, ge=1, le=100)
    duration_minutes: int = Field(default=60, ge=5, le=300)
    total_marks: int = Field(default=100, ge=1)

    difficulty: Literal[
        "easy", "medium", "hard", "mixed"
    ] = "mixed"

    question_types: list[QuestionType] = Field(
        default_factory=lambda: ["mcq", "coding"]
    )

    @model_validator(mode="after")
    def validate_question_types(self):
        if not self.question_types:
            raise ValueError(
                "At least one question type is required."
            )

        self.question_types = list(
            dict.fromkeys(self.question_types)
        )

        return self


class AssessmentRequest(BaseModel):
    job_description: JobDescriptionResponse
    config: AssessmentConfig = Field(
        default_factory=AssessmentConfig
    )


class SkillDistribution(BaseModel):
    skill: str
    importance: Literal["high", "medium", "low"]
    question_count: int = Field(ge=0)
    reason: str


class BlueprintPlan(BaseModel):
    role: str
    experience_level: str
    skill_distribution: list[SkillDistribution]


class QuestionAllocation(BaseModel):
    question_type: QuestionType
    difficulty: Difficulty
    count: int = Field(ge=1)
    marks_per_question: int = Field(ge=1)
    estimated_minutes_per_question: float = Field(gt=0)


class SkillBlueprint(BaseModel):
    skill: str
    importance: Literal["high", "medium", "low"]
    question_count: int
    reason: str
    allocations: list[QuestionAllocation]


class AssessmentBlueprint(BaseModel):
    role: str
    experience_level: str
    total_questions: int
    total_marks: int
    duration_minutes: int
    difficulty: str
    question_types: list[QuestionType]
    skills: list[SkillBlueprint]
