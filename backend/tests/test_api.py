"""Tests for the Research Agent FastAPI endpoints."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from backend.app.main import app, research_sessions


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
    }


def test_research_rejects_short_topic():
    response = client.post(
        "/api/research",
        json={"topic": "AI"},
    )

    assert response.status_code == 422


def test_research_rejects_blank_topic():
    response = client.post(
        "/api/research",
        json={"topic": "     "},
    )

    assert response.status_code == 422


def test_research_returns_report():
    fake_report = """
# Research Report: Renewable Energy

## Executive Summary
Renewable energy can reduce operational emissions.

## Sources
1. https://example.com
""".strip()

    with patch(
        "backend.app.main.research_topic",
        new=AsyncMock(return_value=fake_report),
    ), patch("backend.app.main.uuid4") as fake_uuid:
        fake_uuid.return_value.hex = "session-123"
        response = client.post(
            "/api/research",
            json={
                "topic": "Renewable energy benefits",
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "topic": "Renewable energy benefits",
        "report": fake_report,
        "session_id": "session-123",
    }


def test_followup_uses_saved_context():
    research_sessions["session-123"] = {
        "topic": "Renewable energy benefits",
        "report": "Saved report",
        "history": [],
    }
    with patch(
        "backend.app.main.answer_followup",
        new=AsyncMock(return_value="A contextual answer [1]."),
    ) as mocked_answer:
        response = client.post(
            "/api/followup",
            json={
                "session_id": "session-123",
                "question": "What is the main limitation?",
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "session_id": "session-123",
        "question": "What is the main limitation?",
        "answer": "A contextual answer [1].",
    }
    mocked_answer.assert_awaited_once()
    assert len(research_sessions["session-123"]["history"]) == 2


def test_followup_rejects_unknown_session():
    response = client.post(
        "/api/followup",
        json={
            "session_id": "missing-session",
            "question": "What is the main limitation?",
        },
    )

    assert response.status_code == 404


def test_research_handles_agent_failure():
    with patch(
        "backend.app.main.research_topic",
        new=AsyncMock(
            side_effect=RuntimeError("Model unavailable"),
        ),
    ):
        response = client.post(
            "/api/research",
            json={
                "topic": "Renewable energy benefits",
            },
        )

    assert response.status_code == 502
    assert response.json() == {
        "detail": (
            "The Research Agent could not complete the request. "
            "Please try again."
        ),
    }
