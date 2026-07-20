from datetime import UTC, datetime

from app.schemas.investigation import InvestigationResult
from app.schemas.knowledge import KnowledgePattern


class KnowledgeCaptureService:
    """Converts a completed investigation into a reusable operational pattern."""

    def capture(self, result: InvestigationResult) -> KnowledgePattern:
        leader = max(result.hypotheses, key=lambda item: item.confidence)
        resolution = result.resolution_plan
        actions = [item.action for item in resolution.actions] if resolution else []
        verification = (
            [item.expected_value for item in resolution.verification_criteria]
            if resolution
            else []
        )
        entities = sorted({entity for item in result.evidence for entity in item.entities})
        categories = sorted({item.category.value for item in result.evidence})
        tags = sorted({result.scenario_id, *[entity.lower() for entity in entities]})
        return KnowledgePattern(
            id=f"KP-{result.investigation_id.removeprefix('INV-')}",
            created_at=datetime.now(UTC),
            source_investigation_id=result.investigation_id,
            title=f"{leader.title} operational pattern",
            symptoms=[result.problem],
            root_cause=result.verdict or leader.title,
            resolution_summary=actions,
            verification_summary=verification,
            evidence_categories=categories,
            entities=entities,
            tags=tags,
            confidence=leader.confidence,
            reusable=result.stop_reason.sufficient,
        )
