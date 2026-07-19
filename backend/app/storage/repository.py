from abc import ABC, abstractmethod

from app.schemas.investigation import InvestigationResult
from app.storage.models import InvestigationHistoryItem


class InvestigationRepository(ABC):
    @abstractmethod
    def save(self, result: InvestigationResult, report_markdown: str) -> None: ...

    @abstractmethod
    def get(self, investigation_id: str) -> InvestigationResult: ...

    @abstractmethod
    def list(
        self,
        query: str | None = None,
        status: str | None = None,
        environment: str | None = None,
        priority: str | None = None,
        root_cause: str | None = None,
    ) -> list[InvestigationHistoryItem]: ...

    @abstractmethod
    def get_report(self, investigation_id: str) -> str: ...

    @abstractmethod
    def delete(self, investigation_id: str) -> None: ...

    @abstractmethod
    def exists(self, investigation_id: str) -> bool: ...
