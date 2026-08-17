import logging
import asyncio
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.app.agent.research_agent import answer_followup, research_topic
from backend.app.models import (
    FollowUpRequest,
    FollowUpResponse,
    ResearchRequest,
    ResearchResponse,
)


logger = logging.getLogger(__name__)

# Local in-memory context is sufficient for this free single-process demo.
# A production deployment should replace this with SQLite or another database.
research_sessions: dict[str, dict] = {}


app = FastAPI(
    title="Research Agent API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Research Agent API is running."
    }

@app.post(
    "/api/research",
    response_model=ResearchResponse,
)
async def create_research(
    request: ResearchRequest,
) -> ResearchResponse:
    """Generate a multi-source research report."""

    try:
        report = await asyncio.wait_for(
            research_topic(request.topic),
            timeout=240,
        )
        session_id = uuid4().hex
        research_sessions[session_id] = {
            "topic": request.topic,
            "report": report,
            "history": [],
        }

        return ResearchResponse(
            topic=request.topic,
            report=report,
            session_id=session_id,
        )

    except Exception as error:
        logger.exception(
            "Research request failed for topic: %s",
            request.topic,
        )
        raise HTTPException(
            status_code=502,
            detail=(
                "The Research Agent could not complete the request. "
                "Please try again."
            ),
        ) from error


@app.post(
    "/api/followup",
    response_model=FollowUpResponse,
)
async def create_followup(request: FollowUpRequest) -> FollowUpResponse:
    """Answer a follow-up using the saved report and conversation context."""
    session = research_sessions.get(request.session_id)
    if session is None:
        raise HTTPException(
            status_code=404,
            detail="The research session was not found. Start new research first.",
        )

    try:
        answer = await asyncio.wait_for(
            answer_followup(
                topic=session["topic"],
                report=session["report"],
                history=session["history"],
                question=request.question,
            ),
            timeout=180,
        )
        session["history"].extend(
            [
                {"role": "user", "content": request.question},
                {"role": "assistant", "content": answer},
            ]
        )
        return FollowUpResponse(
            session_id=request.session_id,
            question=request.question,
            answer=answer,
        )
    except Exception as error:
        logger.exception(
            "Follow-up request failed for session: %s",
            request.session_id,
        )
        raise HTTPException(
            status_code=502,
            detail="The Research Agent could not answer the follow-up question.",
        ) from error


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy"
    }
