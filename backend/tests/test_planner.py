from app.core.settings import Settings
from app.investigation.planner import OpenAIInvestigationPlanner
from app.schemas.investigation import InvestigationRequest


async def test_openai_planner_safely_falls_back_without_key() -> None:
    planner = OpenAIInvestigationPlanner(
        Settings(
            planner_provider="openai",
            openai_api_key=None,
            planner_fallback_to_fixture=True,
        ),
        available_tools=[
            "query_splunk_internal_logs",
            "get_certificate_status",
            "search_historical_incidents",
            "get_component_relationships",
            "get_heavy_forwarder_health",
        ],
    )
    plan = await planner.create_plan(
        InvestigationRequest(
            problem="Why is HF-PROD-02 not forwarding logs to the indexer cluster?"
        )
    )

    assert plan.hypotheses
    assert planner.last_usage.provider == "openai"
    assert planner.last_usage.fallback_used is True
