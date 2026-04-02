from langgraph.graph import END, START, StateGraph

from app.agents.retrospective.nodes import (
    analyze_patterns,
    collect_logs,
    generate_draft,
    notify_spring_api,
    save_to_mongo,
    suggest_goals,
)
from app.agents.retrospective.state import RetrospectiveState


def build_retrospective_graph() -> StateGraph:
    graph = StateGraph(RetrospectiveState)

    graph.add_node("collect_logs", collect_logs)
    graph.add_node("analyze_patterns", analyze_patterns)
    graph.add_node("generate_draft", generate_draft)
    graph.add_node("suggest_goals", suggest_goals)
    graph.add_node("save_to_mongo", save_to_mongo)
    graph.add_node("notify_spring_api", notify_spring_api)

    graph.add_edge(START, "collect_logs")
    graph.add_edge("collect_logs", "analyze_patterns")
    graph.add_edge("analyze_patterns", "generate_draft")
    graph.add_edge("generate_draft", "suggest_goals")
    graph.add_edge("suggest_goals", "save_to_mongo")
    graph.add_edge("save_to_mongo", "notify_spring_api")
    graph.add_edge("notify_spring_api", END)

    return graph.compile()


# 싱글턴 컴파일 그래프
retrospective_graph = build_retrospective_graph()


async def run_retrospective_agent(
    user_id: str,
    period_from: str,
    period_to: str,
) -> RetrospectiveState:
    initial_state = RetrospectiveState(
        user_id=user_id,
        period_from=period_from,
        period_to=period_to,
        work_logs=[],
        rag_context="",
        analysis_summary="",
        draft_title="",
        draft_content="",
        goals=[],
        mongo_doc_id=None,
        error=None,
    )
    return await retrospective_graph.ainvoke(initial_state)
