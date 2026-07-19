from app.investigation.base import InvestigationEngineProtocol
from app.schemas.investigation import InvestigationRequest, InvestigationResult


class InvestigationOrchestrator:
    """Stable entry point that delegates work to the selected engine."""

    def __init__(self, engine: InvestigationEngineProtocol) -> None:
        self._engine = engine

    async def create(self, request: InvestigationRequest) -> InvestigationResult:
        return await self._engine.create(request)

    async def run(self, investigation_id: str) -> None:
        await self._engine.run(investigation_id)
