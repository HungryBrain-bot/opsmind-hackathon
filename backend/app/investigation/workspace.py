from app.schemas.investigation import InvestigationResult
from app.schemas.workspace import (
    ConfidencePoint,
    GraphEdgeType,
    GraphNodeType,
    InvestigationWorkspace,
    WorkspaceGraph,
    WorkspaceGraphEdge,
    WorkspaceGraphNode,
    WorkspaceHypothesis,
    WorkspaceResolutionStage,
    WorkspaceTimelineItem,
    WorkspaceVerificationItem,
)


class InvestigationWorkspaceBuilder:
    """Transforms engine state into presentation-ready workspace data."""

    def build(self, result: InvestigationResult) -> InvestigationWorkspace:
        leading = max(result.hypotheses, key=lambda item: item.confidence, default=None)
        return InvestigationWorkspace(
            investigation_id=result.investigation_id,
            problem=result.problem,
            environment=result.environment,
            priority=result.priority,
            status=result.status.value,
            phase=result.lifecycle_phase.value,
            progress_percent=result.progress_percent,
            round_number=result.round_number,
            verdict=result.verdict,
            leading_hypothesis_id=leading.id if leading else None,
            leading_hypothesis=leading.title if leading else None,
            overall_confidence=leading.confidence if leading else 0.0,
            evidence_strength=result.evidence_strength,
            completeness=result.investigation_completeness,
            next_action=result.next_action,
            missing_evidence=result.missing_evidence,
            graph=self._graph(result),
            timeline=[
                WorkspaceTimelineItem(
                    sequence=index,
                    timestamp=item.timestamp,
                    phase=item.phase,
                    title=item.title,
                    detail=item.detail,
                    kind=self._timeline_kind(item.phase, item.title),
                )
                for index, item in enumerate(result.timeline, start=1)
            ],
            confidence_evolution=self._confidence(result),
            hypotheses=[
                WorkspaceHypothesis(
                    id=item.id,
                    title=item.title,
                    rationale=item.rationale,
                    status=item.status.value,
                    confidence=item.confidence,
                    supporting_evidence_ids=item.supporting_evidence_ids,
                    contradicting_evidence_ids=item.contradicting_evidence_ids,
                    rejection_reason=item.rejection_reason,
                )
                for item in sorted(
                    result.hypotheses, key=lambda item: item.confidence, reverse=True
                )
            ],
            resolution=self._resolution(result),
            verification=self._verification(result),
            knowledge_capture=(
                result.knowledge_pattern.model_dump(mode="json")
                if result.knowledge_pattern
                else None
            ),
            playback_events=self._playback(result),
        )

    def _graph(self, result: InvestigationResult) -> WorkspaceGraph:
        nodes = [
            WorkspaceGraphNode(
                id="incident",
                label=result.problem,
                node_type=GraphNodeType.INCIDENT,
                status=result.status.value,
                subtitle=f"{result.environment} · {result.priority}",
                detail=result.stop_reason.summary,
            )
        ]
        edges: list[WorkspaceGraphEdge] = []
        for hypothesis in result.hypotheses:
            nodes.append(
                WorkspaceGraphNode(
                    id=hypothesis.id,
                    label=hypothesis.title,
                    node_type=GraphNodeType.HYPOTHESIS,
                    status=hypothesis.status.value,
                    confidence=hypothesis.confidence,
                    subtitle=f"{hypothesis.confidence:.0%} confidence",
                    detail=hypothesis.rationale,
                )
            )
            edges.append(
                WorkspaceGraphEdge(
                    source="incident",
                    target=hypothesis.id,
                    edge_type=GraphEdgeType.RELATES_TO,
                )
            )
        entity_ids: set[str] = set()
        for evidence in result.evidence:
            nodes.append(
                WorkspaceGraphNode(
                    id=evidence.id,
                    label=evidence.title,
                    node_type=GraphNodeType.EVIDENCE,
                    status="current" if evidence.current else "historical",
                    subtitle=f"{evidence.category.value} · {evidence.reliability.value}",
                    detail=evidence.content,
                    metadata={
                        "source": evidence.source,
                        "observed_at": evidence.observed_at.isoformat(),
                    },
                )
            )
            for hypothesis_id in evidence.supports:
                edges.append(
                    WorkspaceGraphEdge(
                        source=evidence.id,
                        target=hypothesis_id,
                        edge_type=GraphEdgeType.SUPPORTS,
                        label="supports",
                    )
                )
            for hypothesis_id in evidence.contradicts:
                edges.append(
                    WorkspaceGraphEdge(
                        source=evidence.id,
                        target=hypothesis_id,
                        edge_type=GraphEdgeType.CONTRADICTS,
                        label="contradicts",
                    )
                )
            for entity in evidence.entities:
                entity_id = f"entity:{entity}"
                if entity_id not in entity_ids:
                    entity_ids.add(entity_id)
                    nodes.append(
                        WorkspaceGraphNode(
                            id=entity_id,
                            label=entity,
                            node_type=GraphNodeType.ENTITY,
                            status="known",
                            subtitle="Enterprise entity",
                        )
                    )
                edges.append(
                    WorkspaceGraphEdge(
                        source=evidence.id,
                        target=entity_id,
                        edge_type=GraphEdgeType.RELATES_TO,
                    )
                )
        if result.resolution_plan:
            nodes.append(
                WorkspaceGraphNode(
                    id="resolution",
                    label="Resolution plan",
                    node_type=GraphNodeType.RESOLUTION,
                    status=result.resolution_plan.status,
                    confidence=result.resolution_plan.confidence,
                    subtitle=result.resolution_plan.root_cause,
                )
            )
            edges.append(
                WorkspaceGraphEdge(
                    source=result.resolution_plan.root_cause_hypothesis_id,
                    target="resolution",
                    edge_type=GraphEdgeType.RESOLVES,
                    label="resolves",
                )
            )
        return WorkspaceGraph(nodes=nodes, edges=edges)

    def _confidence(self, result: InvestigationResult) -> list[ConfidencePoint]:
        points = []
        for index, confidence in enumerate(result.confidence_history, start=1):
            round_item = next((item for item in result.rounds if item.number == index), None)
            points.append(
                ConfidencePoint(
                    round_number=index,
                    confidence=confidence,
                    label=f"Round {index}",
                    reason=round_item.decision_reason if round_item else "Evidence evaluated",
                )
            )
        return points

    def _resolution(self, result: InvestigationResult) -> list[WorkspaceResolutionStage]:
        if not result.resolution_plan:
            return []
        return [
            WorkspaceResolutionStage(
                id=item.id,
                stage=item.stage.value,
                title=item.stage.value.replace("_", " ").title(),
                action=item.action,
                rationale=item.rationale,
                expected_outcome=item.expected_outcome,
                risk=item.risk.value,
                confidence=item.confidence,
                approval_required=item.approval_required,
                evidence_ids=item.evidence_ids,
                rollback_action=item.rollback_action,
            )
            for item in result.resolution_plan.actions
        ]

    def _verification(self, result: InvestigationResult) -> list[WorkspaceVerificationItem]:
        if not result.resolution_plan:
            return []
        return [
            WorkspaceVerificationItem(
                id=item.id,
                metric=item.metric,
                condition=item.condition,
                expected_value=item.expected_value,
                source=item.evidence_source,
                status=item.status,
            )
            for item in result.resolution_plan.verification_criteria
        ]

    def _playback(self, result: InvestigationResult) -> list[dict[str, object]]:
        events: list[dict[str, object]] = []
        for index, item in enumerate(result.timeline, start=1):
            events.append(
                {
                    "sequence": index,
                    "at_ms": (index - 1) * 900,
                    "type": self._timeline_kind(item.phase, item.title),
                    "title": item.title,
                    "detail": item.detail,
                    "phase": item.phase,
                }
            )
        return events

    @staticmethod
    def _timeline_kind(phase: str, title: str) -> str:
        value = f"{phase} {title}".lower()
        if "evidence" in value or "tool" in value:
            return "evidence"
        if "hypoth" in value or "reason" in value:
            return "hypothesis"
        if "resolution" in value or "verdict" in value:
            return "resolution"
        if "verification" in value:
            return "verification"
        if "knowledge" in value:
            return "knowledge"
        return "activity"
