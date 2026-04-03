from fastapi import APIRouter
from pydantic import BaseModel

from app.agents.coaching.graph import run_coaching_agent
from app.agents.retrospective.graph import run_retrospective_agent

router = APIRouter(prefix="/agents", tags=["agents"])


class RetrospectiveRequest(BaseModel):
    user_id: str
    period_from: str  # "2026-03-28"
    period_to: str    # "2026-04-03"


class RetrospectiveResponse(BaseModel):
    draft_title: str
    draft_content: str
    goals: list[str]
    mongo_doc_id: str | None


@router.post("/retrospective", response_model=RetrospectiveResponse)
async def trigger_retrospective_agent(body: RetrospectiveRequest):
    result = await run_retrospective_agent(
        user_id=body.user_id,
        period_from=body.period_from,
        period_to=body.period_to,
    )
    return RetrospectiveResponse(
        draft_title=result["draft_title"],
        draft_content=result["draft_content"],
        goals=result["goals"],
        mongo_doc_id=result.get("mongo_doc_id"),
    )


class CoachingRequest(BaseModel):
    user_id: str


class CoachingResponse(BaseModel):
    weak_stacks: list[str]
    roadmap: str
    mongo_doc_id: str | None


@router.post("/coaching", response_model=CoachingResponse)
async def trigger_coaching_agent(body: CoachingRequest):
    result = await run_coaching_agent(user_id=body.user_id)
    return CoachingResponse(
        weak_stacks=result["weak_stacks"],
        roadmap=result["roadmap"],
        mongo_doc_id=result.get("mongo_doc_id"),
    )
