import logging
import uuid
from datetime import date, datetime

import httpx
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy import select

from app.agents.retrospective.state import RetrospectiveState, WorkLogItem
from app.core.config import settings
from app.core.database import AsyncSessionLocal, get_mongo_db
from app.models.work_log import WorkLog
from app.services.model_service import get_model_service
from app.services.rag_service import build_rag_context

logger = logging.getLogger(__name__)

_llm: ChatAnthropic | None = None


def _get_llm() -> ChatAnthropic:
    global _llm
    if _llm is None:
        _llm = ChatAnthropic(
            model="claude-sonnet-4-6",
            api_key=settings.ANTHROPIC_API_KEY,
            max_tokens=4096,
        )
    return _llm


# ── Node 1: 지난주 WorkLog 수집 ────────────────────────────────────────────────

async def collect_logs(state: RetrospectiveState) -> RetrospectiveState:
    user_id = uuid.UUID(state["user_id"])
    period_from = date.fromisoformat(state["period_from"])
    period_to = date.fromisoformat(state["period_to"])

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(WorkLog)
            .where(
                WorkLog.user_id == user_id,
                WorkLog.log_date >= period_from,
                WorkLog.log_date <= period_to,
            )
            .order_by(WorkLog.log_date)
        )
        logs = result.scalars().all()

    work_logs: list[WorkLogItem] = [
        WorkLogItem(
            id=str(log.id),
            title=log.title,
            content=log.content,
            log_date=str(log.log_date),
            mood=log.mood,
        )
        for log in logs
    ]

    logger.info(
        "WorkLog 수집 완료 userId=%s count=%d period=%s~%s",
        state["user_id"],
        len(work_logs),
        state["period_from"],
        state["period_to"],
    )
    return {**state, "work_logs": work_logs}


# ── Node 2: RAG 패턴 분석 ─────────────────────────────────────────────────────

async def analyze_patterns(state: RetrospectiveState) -> RetrospectiveState:
    if not state["work_logs"]:
        return {**state, "rag_context": "", "analysis_summary": "이번 주 작업 로그가 없습니다."}

    query = " ".join(log["title"] for log in state["work_logs"])
    user_id = uuid.UUID(state["user_id"])

    async with AsyncSessionLocal() as db:
        rag_context = await build_rag_context(query, user_id, db, top_k=5)

    return {**state, "rag_context": rag_context}


# ── Node 3: 회고 초안 생성 ────────────────────────────────────────────────────

async def generate_draft(state: RetrospectiveState) -> RetrospectiveState:
    logs_text = "\n\n".join(
        f"[{log['log_date']}] {log['title']}\n{log['content']}"
        for log in state["work_logs"]
    )

    model_service = get_model_service()
    logger.info("회고 초안 생성 backend=%s", model_service.backend_name)

    full_text = await model_service.generate_retrospective_draft(
        logs_text=logs_text,
        period_from=state["period_from"],
        period_to=state["period_to"],
        rag_context=state.get("rag_context", ""),
    )

    # 첫 번째 줄을 제목으로 추출
    lines = full_text.strip().split("\n")
    title_line = next((l for l in lines if l.startswith("## ")), None)
    draft_title = title_line.replace("## ", "").strip() if title_line else f"{state['period_from']} 주간 회고"

    return {**state, "draft_title": draft_title, "draft_content": full_text}


# ── Node 4: 다음 주 목표 제안 ────────────────────────────────────────────────

async def suggest_goals(state: RetrospectiveState) -> RetrospectiveState:
    if not state.get("draft_content"):
        return {**state, "goals": []}

    prompt = f"""다음 회고를 읽고 다음 주 실천 가능한 목표 3가지를 제안해주세요.
목표는 구체적이고 측정 가능하게, 각각 한 문장으로 작성해주세요.
응답은 JSON 배열 형식으로만 반환하세요: ["목표1", "목표2", "목표3"]

회고:
{state['draft_content']}"""

    response = await _get_llm().ainvoke([HumanMessage(content=prompt)])
    raw = response.content.strip()

    try:
        import json
        # JSON 코드블록 제거
        if "```" in raw:
            raw = raw.split("```")[1].replace("json", "").strip()
        goals = json.loads(raw)
        if not isinstance(goals, list):
            goals = [str(goals)]
    except Exception:
        goals = [raw]

    return {**state, "goals": goals}


# ── Node 5: MongoDB 저장 ──────────────────────────────────────────────────────

async def save_to_mongo(state: RetrospectiveState) -> RetrospectiveState:
    db = get_mongo_db()
    doc = {
        "user_id": state["user_id"],
        "period_from": state["period_from"],
        "period_to": state["period_to"],
        "work_log_count": len(state.get("work_logs", [])),
        "draft_title": state.get("draft_title", ""),
        "draft_content": state.get("draft_content", ""),
        "goals": state.get("goals", []),
        "created_at": datetime.utcnow(),
    }
    result = await db["retrospective_results"].insert_one(doc)
    logger.info("MongoDB 저장 완료 docId=%s", result.inserted_id)
    return {**state, "mongo_doc_id": str(result.inserted_id)}


# ── Node 6: Spring Boot API 전달 ─────────────────────────────────────────────

async def notify_spring_api(state: RetrospectiveState) -> RetrospectiveState:
    """회고 초안을 Spring Boot retrospectives API에 저장"""
    if not state.get("draft_content"):
        return state

    api_url = f"http://api:8080/api/v1/retrospectives"
    payload = {
        "userId": state["user_id"],
        "title": state.get("draft_title", "주간 회고"),
        "content": state.get("draft_content", ""),
        "periodFrom": state["period_from"],
        "periodTo": state["period_to"],
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(api_url, json=payload)
            response.raise_for_status()
            logger.info("Spring Boot API 전달 완료 userId=%s", state["user_id"])
    except Exception as e:
        logger.error("Spring Boot API 전달 실패: %s", e)

    return state
