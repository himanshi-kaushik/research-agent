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
    session_id: str


class FollowUpRequest(BaseModel):
    """Input for asking a question about an existing research session."""

    session_id: str = Field(min_length=1, max_length=100)
    question: str = Field(min_length=3, max_length=1000)

    @field_validator("session_id", "question")
    @classmethod
    def values_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("The value cannot be empty.")
        return value


class FollowUpResponse(BaseModel):
    """Answer produced with the context of an existing research session."""

    session_id: str
    question: str
    answer: str
