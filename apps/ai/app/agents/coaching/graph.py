from langgraph.graph import END, START, StateGraph

from app.agents.coaching.nodes import (
    analyze_weak_stacks,
    collect_recent_logs,
    generate_roadmap,
    save_to_mongo,
    search_resources,
)
from app.agents.coaching.state import CoachingState


def build_coaching_graph() -> StateGraph:
    graph = StateGraph(CoachingState)

    graph.add_node("collect_recent_logs", collect_recent_logs)
    graph.add_node("analyze_weak_stacks", analyze_weak_stacks)
    graph.add_node("search_resources", search_resources)
    graph.add_node("generate_roadmap", generate_roadmap)
    graph.add_node("save_to_mongo", save_to_mongo)

    graph.add_edge(START, "collect_recent_logs")
    graph.add_edge("collect_recent_logs", "analyze_weak_stacks")
    graph.add_edge("analyze_weak_stacks", "search_resources")
    graph.add_edge("search_resources", "generate_roadmap")
    graph.add_edge("generate_roadmap", "save_to_mongo")
    graph.add_edge("save_to_mongo", END)

    return graph.compile()


# 싱글턴 컴파일 그래프
coaching_graph = build_coaching_graph()


async def run_coaching_agent(user_id: str) -> CoachingState:
    initial_state = CoachingState(
        user_id=user_id,
        recent_logs=[],
        rag_context="",
        weak_stacks=[],
        search_results={},
        roadmap="",
        mongo_doc_id=None,
        error=None,
    )
    return await coaching_graph.ainvoke(initial_state)
