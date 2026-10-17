
from pydantic import BaseModel, Field

from backend.schemas.assembly_schema import AssessmentAssemblyResponse


class AssessmentValidationRequest(BaseModel):
    blueprint: dict
    assessment: AssessmentAssemblyResponse


class ValidationCheck(BaseModel):
    name: str
    passed: bool
    message: str


class AssessmentValidationResponse(BaseModel):
    is_valid: bool
    checks: list[ValidationCheck] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
