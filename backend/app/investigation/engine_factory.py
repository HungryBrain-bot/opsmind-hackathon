from app.core.settings import Settings
from app.investigation.base import InvestigationEngineProtocol
from app.investigation.demo_engine import DemoInvestigationEngine
from app.investigation.openai_engine import OpenAIInvestigationEngine
from app.investigation.store import InvestigationStore


class InvestigationEngineFactory:
    """Build the investigation engine selected by the configured planner provider."""

    def __init__(self, settings: Settings, store: InvestigationStore) -> None:
        self._settings = settings
        self._store = store

    def build(self) -> InvestigationEngineProtocol:
        provider = self._settings.planner_provider.strip().lower()

        if provider == "fixture":
            return DemoInvestigationEngine(self._settings, self._store)

        if provider == "openai":
            self._validate_openai_configuration()
            return OpenAIInvestigationEngine(self._settings, self._store)

        raise ValueError(
            "Unsupported OPSMIND_PLANNER_PROVIDER "
            f"{self._settings.planner_provider!r}. Expected 'fixture' or 'openai'."
        )

    def _validate_openai_configuration(self) -> None:
        if self._settings.openai_api_key:
            return
        if self._settings.planner_fallback_to_fixture:
            return
        raise ValueError(
            "OPSMIND_OPENAI_API_KEY is required when OPSMIND_PLANNER_PROVIDER='openai' "
            "and OPSMIND_PLANNER_FALLBACK_TO_FIXTURE=false."
        )
