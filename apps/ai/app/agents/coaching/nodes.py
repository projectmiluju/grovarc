import json
import logging
import uuid
from datetime import date, datetime, timedelta

from langchain_anthropic import ChatAnthropic
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy import select

from app.agents.coaching.state import CoachingState
from app.agents.retrospective.state import WorkLogItem
from app.core.config import settings
from app.core.database import AsyncSessionLocal, get_mongo_db
from app.models.work_log import WorkLog
from app.services.rag_service import build_rag_context

logger = logging.getLogger(__name__)

_llm: ChatAnthropic | None = None
_search: DuckDuckGoSearchRun | None = None


def _get_llm() -> ChatAnthropic:
    global _llm
    if _llm is None:
        _llm = ChatAnthropic(
            model="claude-sonnet-4-6",
            api_key=settings.ANTHROPIC_API_KEY,
            max_tokens=4096,
        )
    return _llm


def _get_search() -> DuckDuckGoSearchRun:
    global _search
    if _search is None:
        _search = DuckDuckGoSearchRun()
    return _search


# ── Node 1: 최근 3개월 WorkLog 수집 ──────────────────────────────────────────

async def collect_recent_logs(state: CoachingState) -> CoachingState:
    user_id = uuid.UUID(state["user_id"])
    period_to = date.today()
    period_from = period_to - timedelta(days=90)

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(WorkLog)
            .where(
                WorkLog.user_id == user_id,
                WorkLog.log_date >= period_from,
                WorkLog.log_date <= period_to,
            )
            .order_by(WorkLog.log_date.desc())
        )
        logs = result.scalars().all()

    recent_logs: list[WorkLogItem] = [
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
        "최근 3개월 WorkLog 수집 완료 userId=%s count=%d",
        state["user_id"],
        len(recent_logs),
    )
    return {**state, "recent_logs": recent_logs}


# ── Node 2: 부족한 기술 스택 파악 (RAG + LLM) ────────────────────────────────

async def analyze_weak_stacks(state: CoachingState) -> CoachingState:
    if not state["recent_logs"]:
        return {**state, "rag_context": "", "weak_stacks": []}

    query = " ".join(log["title"] for log in state["recent_logs"][:20])
    user_id = uuid.UUID(state["user_id"])

    async with AsyncSessionLocal() as db:
        rag_context = await build_rag_context(query, user_id, db, top_k=10)

    logs_text = "\n".join(
        f"[{log['log_date']}] {log['title']}: {log['content'][:200]}"
        for log in state["recent_logs"][:30]
    )

    system_prompt = """당신은 개발자 성장을 분석하는 AI 코치입니다.
작업 로그를 분석하여 개발자가 자주 다루는 기술과 부족하거나 더 발전이 필요한 기술 스택을 파악해주세요."""

    human_prompt = f"""## 최근 3개월 작업 로그
{logs_text}

{f"## 과거 패턴 (RAG){chr(10)}{rag_context}" if rag_context else ""}

위 로그를 분석하여 이 개발자가 학습을 강화해야 할 기술 스택 3~5가지를 파악해주세요.
응답은 JSON 배열 형식으로만 반환하세요: ["기술1", "기술2", "기술3"]
각 항목은 구체적인 기술명으로 작성하세요 (예: "Kubernetes", "Redis 캐싱 전략", "JUnit 테스트")."""

    response = await _get_llm().ainvoke(
        [SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)]
    )
    raw = response.content.strip()

    try:
        if "```" in raw:
            raw = raw.split("```")[1].replace("json", "").strip()
        weak_stacks = json.loads(raw)
        if not isinstance(weak_stacks, list):
            weak_stacks = [str(weak_stacks)]
    except Exception:
        weak_stacks = [raw]

    logger.info("부족 스택 파악 완료 userId=%s stacks=%s", state["user_id"], weak_stacks)
    return {**state, "rag_context": rag_context, "weak_stacks": weak_stacks}


# ── Node 3: 학습 리소스 웹 검색 ──────────────────────────────────────────────

async def search_resources(state: CoachingState) -> CoachingState:
    if not state["weak_stacks"]:
        return {**state, "search_results": {}}

    search = _get_search()
    search_results: dict[str, str] = {}

    for stack in state["weak_stacks"]:
        try:
            query = f"{stack} 학습 로드맵 튜토리얼 추천 2024 2025"
            result = search.run(query)
            search_results[stack] = result[:800]  # 토큰 절약
            logger.info("웹 검색 완료 stack=%s", stack)
        except Exception as e:
            logger.warning("웹 검색 실패 stack=%s error=%s", stack, e)
            search_results[stack] = ""

    return {**state, "search_results": search_results}


# ── Node 4: 개인화 학습 로드맵 생성 ──────────────────────────────────────────

async def generate_roadmap(state: CoachingState) -> CoachingState:
    if not state["weak_stacks"]:
        return {**state, "roadmap": "분석할 작업 로그가 없습니다."}

    stacks_section = "\n".join(f"- {s}" for s in state["weak_stacks"])

    resources_section = ""
    for stack, result in state.get("search_results", {}).items():
        if result:
            resources_section += f"\n### {stack}\n{result}\n"

    logs_summary = "\n".join(
        f"[{log['log_date']}] {log['title']}"
        for log in state["recent_logs"][:15]
    )

    system_prompt = """당신은 개발자의 성장을 돕는 AI 코치입니다.
분석 결과를 바탕으로 구체적이고 실천 가능한 개인화 학습 로드맵을 마크다운으로 작성해주세요."""

    human_prompt = f"""## 개발자 최근 활동 요약
{logs_summary}

## 학습이 필요한 기술 스택
{stacks_section}

## 웹 검색 학습 리소스
{resources_section if resources_section else "검색 결과 없음"}

위 정보를 바탕으로 개인화된 8주 학습 로드맵을 작성해주세요.
형식:
- 전체 목표 (2~3줄)
- 주차별 학습 계획 (1~8주, 각 주차별 목표 + 구체적 학습 항목)
- 추천 리소스 (책, 강의, 공식 문서 링크 등)
- 실천 팁 (3가지)

한국어로 작성하고 마크다운 형식을 사용하세요."""

    response = await _get_llm().ainvoke(
        [SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)]
    )

    roadmap = response.content.strip()
    logger.info("로드맵 생성 완료 userId=%s", state["user_id"])
    return {**state, "roadmap": roadmap}


# ── Node 5: MongoDB 저장 ──────────────────────────────────────────────────────

async def save_to_mongo(state: CoachingState) -> CoachingState:
    db = get_mongo_db()
    doc = {
        "user_id": state["user_id"],
        "log_count": len(state.get("recent_logs", [])),
        "weak_stacks": state.get("weak_stacks", []),
        "roadmap": state.get("roadmap", ""),
        "created_at": datetime.utcnow(),
    }
    result = await db["coaching_results"].insert_one(doc)
    logger.info("MongoDB 저장 완료 docId=%s", result.inserted_id)
    return {**state, "mongo_doc_id": str(result.inserted_id)}
