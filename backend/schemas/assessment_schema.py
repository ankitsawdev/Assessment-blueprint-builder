
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from backend.schemas.jd_schema import JobDescriptionResponse


QuestionType = Literal[
    "mcq",
    "coding",
    "short_answer",
    "scenario_based",
]

Difficulty = Literal["easy", "medium", "hard"]


DEFAULT_QUESTION_DURATIONS = {
    "mcq": 0.5,
    "coding": 1.0,
    "short_answer": 2.0,
    "scenario_based": 2.0,
}


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

    # Exact number of questions requested for each type.
    # None preserves compatibility with older API requests.
    question_type_counts: dict[QuestionType, int] | None = None

    question_duration_minutes: dict[QuestionType, float] = Field(
        default_factory=lambda: DEFAULT_QUESTION_DURATIONS.copy()
    )

    mixed_difficulty_distribution: dict[Difficulty, int] = Field(
        default_factory=lambda: {
            "easy": 30,
            "medium": 50,
            "hard": 20,
        }
    )

    @model_validator(mode="after")
    def validate_configuration(self):
        if not self.question_types:
            raise ValueError("At least one question type is required.")

        self.question_types = list(dict.fromkeys(self.question_types))

        for question_type in self.question_types:
            duration = self.question_duration_minutes.get(question_type)

            if duration is None or duration <= 0:
                raise ValueError(
                    f"Duration for {question_type} must be greater than zero."
                )

        if self.question_type_counts is not None:
            counts = self.question_type_counts

            if any(count < 0 for count in counts.values()):
                raise ValueError("Question counts cannot be negative.")

            if set(counts.keys()) != set(self.question_types):
                raise ValueError(
                    "Question types must match the types with configured counts."
                )

            if any(count == 0 for count in counts.values()):
                raise ValueError(
                    "Every selected question type must have at least one question."
                )

            if sum(counts.values()) != self.total_questions:
                raise ValueError(
                    "Question type counts must equal total_questions."
                )

        distribution = self.mixed_difficulty_distribution

        if set(distribution.keys()) != {"easy", "medium", "hard"}:
            raise ValueError(
                "Difficulty distribution must contain easy, medium and hard."
            )

        if any(value < 0 or value > 100 for value in distribution.values()):
            raise ValueError(
                "Difficulty percentages must be between 0 and 100."
            )

        if sum(distribution.values()) != 100:
            raise ValueError(
                "Mixed difficulty percentages must total 100."
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
