"""Tests for the Research Agent FastAPI endpoints."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from backend.app.main import app


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
    ):
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
    }


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
    