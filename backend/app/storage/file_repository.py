import json
import os
import shutil
from datetime import UTC, datetime
from pathlib import Path

from app.schemas.investigation import InvestigationResult
from app.storage.models import InvestigationHistoryItem
from app.storage.repository import InvestigationRepository


class FileInvestigationRepository(InvestigationRepository):
    """Atomic, file-backed repository for completed investigation snapshots."""

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _directory(self, investigation_id: str) -> Path:
        safe_id = Path(investigation_id).name
        if safe_id != investigation_id:
            raise ValueError("Invalid investigation ID")
        return self.root / safe_id

    def save(self, result: InvestigationResult, report_markdown: str) -> None:
        directory = self._directory(result.investigation_id)
        directory.mkdir(parents=True, exist_ok=True)
        self._atomic_write(
            directory / "investigation.json",
            result.model_dump_json(indent=2),
        )
        self._atomic_write(directory / "report.md", report_markdown)

    def get(self, investigation_id: str) -> InvestigationResult:
        path = self._directory(investigation_id) / "investigation.json"
        if not path.is_file():
            raise KeyError(investigation_id)
        return InvestigationResult.model_validate_json(path.read_text(encoding="utf-8"))

    def list(
        self,
        query: str | None = None,
        status: str | None = None,
        environment: str | None = None,
        priority: str | None = None,
        root_cause: str | None = None,
    ) -> list[InvestigationHistoryItem]:
        items: list[InvestigationHistoryItem] = []
        for path in self.root.glob("*/investigation.json"):
            try:
                result = InvestigationResult.model_validate_json(path.read_text(encoding="utf-8"))
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            leader = max(result.hypotheses, key=lambda item: item.confidence, default=None)
            root = leader.title if leader else None
            stat = path.stat()
            created = datetime.fromtimestamp(stat.st_ctime, UTC)
            updated = datetime.fromtimestamp(stat.st_mtime, UTC)
            item = InvestigationHistoryItem(
                investigation_id=result.investigation_id,
                problem=result.problem,
                status=result.status,
                environment=result.environment,
                priority=result.priority,
                root_cause=root,
                confidence=leader.confidence if leader else 0.0,
                evidence_count=len(result.evidence),
                created_at=created,
                updated_at=updated,
            )
            haystack = " ".join(
                filter(
                    None,
                    [
                        item.investigation_id,
                        item.problem,
                        item.environment,
                        item.priority,
                        item.root_cause,
                        result.verdict,
                        result.stop_reason.summary,
                    ],
                )
            ).lower()
            if query and query.lower() not in haystack:
                continue
            if status and item.status.value.lower() != status.lower():
                continue
            if environment and item.environment.lower() != environment.lower():
                continue
            if priority and item.priority.lower() != priority.lower():
                continue
            if root_cause and root_cause.lower() not in (item.root_cause or "").lower():
                continue
            items.append(item)
        return sorted(items, key=lambda item: item.updated_at, reverse=True)

    def get_report(self, investigation_id: str) -> str:
        path = self._directory(investigation_id) / "report.md"
        if not path.is_file():
            raise KeyError(investigation_id)
        return path.read_text(encoding="utf-8")

    def delete(self, investigation_id: str) -> None:
        directory = self._directory(investigation_id)
        if not directory.is_dir():
            raise KeyError(investigation_id)
        shutil.rmtree(directory)

    def exists(self, investigation_id: str) -> bool:
        return (self._directory(investigation_id) / "investigation.json").is_file()

    @staticmethod
    def _atomic_write(path: Path, content: str) -> None:
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(content, encoding="utf-8")
        os.replace(temporary, path)
