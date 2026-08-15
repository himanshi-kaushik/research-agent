"""Pydantic models for the Research Agent API."""

from pydantic import BaseModel, Field, field_validator


class ResearchRequest(BaseModel):
    """Input for starting a research task."""

    topic: str = Field(
        min_length=3,
        max_length=500,
        examples=["Benefits and limitations of renewable energy"],
    )

    @field_validator("topic")
    @classmethod
    def topic_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("The research topic cannot be empty.")

        return value


class ResearchResponse(BaseModel):
    """Structured response returned to the frontend."""

    topic: str
    report: str

    