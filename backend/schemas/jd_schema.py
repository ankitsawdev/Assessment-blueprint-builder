from pydantic import BaseModel, Field


class JobDescriptionResponse(BaseModel):
    job_title: str | None = None
    experience_required: str | None = None
    employment_type: str | None = None

    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)

    responsibilities: list[str] = Field(default_factory=list)
    qualifications: list[str] = Field(default_factory=list)

    job_location: str | None = None
    other_details: list[str] = Field(default_factory=list)