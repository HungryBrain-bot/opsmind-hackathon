import pytest

from app.core.settings import Settings
from app.investigation.demo_engine import DemoInvestigationEngine
from app.investigation.engine_factory import InvestigationEngineFactory
from app.investigation.openai_engine import OpenAIInvestigationEngine
from app.investigation.store import InvestigationStore


def test_factory_builds_demo_engine_for_fixture_provider() -> None:
    engine = InvestigationEngineFactory(
        Settings(planner_provider="fixture"),
        InvestigationStore(),
    ).build()

    assert isinstance(engine, DemoInvestigationEngine)


def test_factory_builds_openai_engine_when_key_is_configured() -> None:
    engine = InvestigationEngineFactory(
        Settings(planner_provider="openai", openai_api_key="test-key"),
        InvestigationStore(),
    ).build()

    assert isinstance(engine, OpenAIInvestigationEngine)


def test_factory_allows_openai_engine_with_safe_fixture_fallback() -> None:
    engine = InvestigationEngineFactory(
        Settings(
            planner_provider="openai",
            openai_api_key=None,
            planner_fallback_to_fixture=True,
        ),
        InvestigationStore(),
    ).build()

    assert isinstance(engine, OpenAIInvestigationEngine)


def test_factory_rejects_openai_without_key_when_fallback_is_disabled() -> None:
    factory = InvestigationEngineFactory(
        Settings(
            planner_provider="openai",
            openai_api_key=None,
            planner_fallback_to_fixture=False,
        ),
        InvestigationStore(),
    )

    with pytest.raises(ValueError, match="OPSMIND_OPENAI_API_KEY is required"):
        factory.build()


def test_factory_rejects_unknown_provider() -> None:
    factory = InvestigationEngineFactory(
        Settings(planner_provider="unknown"),
        InvestigationStore(),
    )

    with pytest.raises(ValueError, match="Unsupported OPSMIND_PLANNER_PROVIDER"):
        factory.build()
