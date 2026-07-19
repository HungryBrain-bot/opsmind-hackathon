from typing import Protocol

from app.schemas.investigation import InvestigationRequest, InvestigationResult


class InvestigationEngineProtocol(Protocol):
    """Common contract implemented by every OpsMind investigation engine."""

    async def create(self, request: InvestigationRequest) -> InvestigationResult:
        """Create and persist a new investigation."""

    async def run(self, investigation_id: str) -> None:
        """Run an existing investigation until it reaches a terminal state."""
