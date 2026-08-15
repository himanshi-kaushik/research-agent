import logging
import asyncio

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.app.agent.research_agent import research_topic
from backend.app.models import ResearchRequest, ResearchResponse


logger = logging.getLogger(__name__)


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

        return ResearchResponse(
            topic=request.topic,
            report=report,
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


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy"
    }
