import asyncio
from copy import deepcopy

from app.investigation.reporting import InvestigationReportBuilder
from app.schemas.investigation import InvestigationEvent, InvestigationResult, InvestigationStatus
from app.storage.repository import InvestigationRepository


class InvestigationNotFoundError(KeyError):
    pass


class InvestigationStore:
    """Live in-memory state with optional durable history for terminal investigations."""

    def __init__(self, repository: InvestigationRepository | None = None) -> None:
        self.repository = repository
        self._results: dict[str, InvestigationResult] = {}
        self._events: dict[str, list[InvestigationEvent]] = {}
        self._conditions: dict[str, asyncio.Condition] = {}
        self._lock = asyncio.Lock()

    async def create(self, result: InvestigationResult) -> None:
        async with self._lock:
            self._results[result.investigation_id] = deepcopy(result)
            self._events[result.investigation_id] = []
            self._conditions[result.investigation_id] = asyncio.Condition()

    async def get(self, investigation_id: str) -> InvestigationResult:
        async with self._lock:
            result = self._results.get(investigation_id)
            if result is not None:
                return deepcopy(result)
        if self.repository and self.repository.exists(investigation_id):
            try:
                return self.repository.get(investigation_id)
            except KeyError as exc:
                raise InvestigationNotFoundError(investigation_id) from exc
        raise InvestigationNotFoundError(investigation_id)

    async def update(self, result: InvestigationResult) -> None:
        async with self._lock:
            if result.investigation_id not in self._results:
                raise InvestigationNotFoundError(result.investigation_id)
            self._results[result.investigation_id] = deepcopy(result)
        if self.repository and result.status in {
            InvestigationStatus.COMPLETED,
            InvestigationStatus.INCONCLUSIVE,
            InvestigationStatus.FAILED,
        }:
            report = InvestigationReportBuilder().to_markdown(result)
            self.repository.save(result, report)

    async def append_event(self, event: InvestigationEvent) -> None:
        condition = self._conditions.get(event.investigation_id)
        if condition is None:
            raise InvestigationNotFoundError(event.investigation_id)
        async with self._lock:
            self._events[event.investigation_id].append(deepcopy(event))
        async with condition:
            condition.notify_all()

    async def events_from(self, investigation_id: str, offset: int) -> list[InvestigationEvent]:
        async with self._lock:
            if investigation_id not in self._events:
                raise InvestigationNotFoundError(investigation_id)
            return deepcopy(self._events[investigation_id][offset:])

    async def wait_for_events(self, investigation_id: str, timeout: float = 15.0) -> None:
        condition = self._conditions.get(investigation_id)
        if condition is None:
            raise InvestigationNotFoundError(investigation_id)
        async with condition:
            try:
                await asyncio.wait_for(condition.wait(), timeout=timeout)
            except TimeoutError:
                return
