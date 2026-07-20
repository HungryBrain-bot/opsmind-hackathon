from app.schemas.hypothesis import Hypothesis
from app.schemas.investigation import InvestigationResult
from app.schemas.resolution import (
    ActionRisk,
    ResolutionAction,
    ResolutionPlan,
    ResolutionStage,
    VerificationCriterion,
)


class ResolutionIntelligenceService:
    """Builds an evidence-backed, approval-gated resolution plan."""

    def build(self, result: InvestigationResult, leading: Hypothesis) -> ResolutionPlan:
        evidence_ids = sorted(set(leading.supporting_evidence_ids))
        actions = self._actions(result.scenario_id, evidence_ids, leading.confidence)
        return ResolutionPlan(
            root_cause=result.verdict or leading.title,
            root_cause_hypothesis_id=leading.id,
            confidence=leading.confidence,
            evidence_ids=evidence_ids,
            actions=actions,
            verification_criteria=self._verification(result.scenario_id),
            risks=self._risks(result.scenario_id),
            human_approval_required=True,
        )

    def _actions(
        self, scenario_id: str, evidence_ids: list[str], confidence: float
    ) -> list[ResolutionAction]:
        catalog = {
            "certificate_expiry": [
                (
                    ResolutionStage.CONTAINMENT,
                    "Pause dependent changes and preserve current logs.",
                    "Prevent configuration drift while the certificate fault is remediated.",
                    "The affected forwarding path remains stable for controlled recovery.",
                    ActionRisk.LOW,
                    None,
                ),
                (
                    ResolutionStage.RECOVERY,
                    "Renew and deploy the Heavy Forwarder client certificate through the approved change process.",
                    "The expired certificate is the evidence-backed root cause of failed TLS handshakes.",
                    "TLS authentication succeeds and forwarding resumes.",
                    ActionRisk.MEDIUM,
                    "Restore the prior certificate bundle and configuration if validation fails.",
                ),
                (
                    ResolutionStage.VERIFICATION,
                    "Validate TLS connectivity and event freshness after deployment.",
                    "Recovery is not complete until both transport and data flow are healthy.",
                    "TLS errors stop and new events arrive within the accepted freshness window.",
                    ActionRisk.LOW,
                    None,
                ),
                (
                    ResolutionStage.PREVENTION,
                    "Add certificate-expiry monitoring and ownership alerts.",
                    "The incident was preventable with proactive certificate lifecycle monitoring.",
                    "Future expiry risk is detected before service impact.",
                    ActionRisk.LOW,
                    None,
                ),
            ],
            "firewall_block": [
                (
                    ResolutionStage.CONTAINMENT,
                    "Freeze unrelated firewall changes affecting the forwarding route.",
                    "Avoid additional network drift during remediation.",
                    "The impacted path can be restored without concurrent policy changes.",
                    ActionRisk.LOW,
                    None,
                ),
                (
                    ResolutionStage.RECOVERY,
                    "Restore the approved TCP 9997 firewall rule.",
                    "Current evidence shows the forwarding path is blocked by policy.",
                    "The Heavy Forwarder can reconnect to the indexer cluster.",
                    ActionRisk.MEDIUM,
                    "Reapply the previous firewall policy if the restored rule creates unexpected exposure.",
                ),
                (
                    ResolutionStage.VERIFICATION,
                    "Test TCP 9997 and confirm queued events drain.",
                    "Connectivity alone is insufficient; ingestion recovery must be observed.",
                    "Reachability succeeds and backlog trends toward zero.",
                    ActionRisk.LOW,
                    None,
                ),
                (
                    ResolutionStage.PREVENTION,
                    "Add policy-drift detection for approved forwarding routes.",
                    "Automated drift detection reduces recurrence risk.",
                    "Unauthorized rule removal is detected quickly.",
                    ActionRisk.LOW,
                    None,
                ),
            ],
            "outputs_misconfiguration": [
                (
                    ResolutionStage.CONTAINMENT,
                    "Stop further deployment of the affected outputs configuration.",
                    "Prevent the invalid destination from propagating.",
                    "Only the known affected scope remains impacted.",
                    ActionRisk.LOW,
                    None,
                ),
                (
                    ResolutionStage.RECOVERY,
                    "Correct the indexer destination in the approved deployment app.",
                    "The effective forwarding destination is invalid.",
                    "The Heavy Forwarder targets the active indexer cluster.",
                    ActionRisk.MEDIUM,
                    "Redeploy the last known-good outputs configuration.",
                ),
                (
                    ResolutionStage.VERIFICATION,
                    "Validate effective configuration with btool and confirm forwarding freshness.",
                    "Both intended and effective configuration must be verified.",
                    "Configuration matches the approved endpoint and events resume.",
                    ActionRisk.LOW,
                    None,
                ),
                (
                    ResolutionStage.PREVENTION,
                    "Add configuration validation before deployment.",
                    "Pre-deployment validation would catch retired endpoints.",
                    "Invalid targets are blocked before production rollout.",
                    ActionRisk.LOW,
                    None,
                ),
            ],
            "disk_full": [
                (
                    ResolutionStage.CONTAINMENT,
                    "Stop nonessential local data growth and preserve diagnostic logs.",
                    "Further growth can worsen queue blockage and remove evidence.",
                    "Free space stops declining while recovery is prepared.",
                    ActionRisk.MEDIUM,
                    None,
                ),
                (
                    ResolutionStage.RECOVERY,
                    "Recover disk space using the approved cleanup runbook.",
                    "Disk exhaustion is blocking Splunk queues.",
                    "Filesystem capacity returns above the operational threshold.",
                    ActionRisk.HIGH,
                    "Restore removed data from backup if an approved cleanup removes required files.",
                ),
                (
                    ResolutionStage.VERIFICATION,
                    "Confirm queues unblock and event freshness recovers.",
                    "Disk recovery must translate into pipeline recovery.",
                    "Blocked queues clear and ingestion lag falls within target.",
                    ActionRisk.LOW,
                    None,
                ),
                (
                    ResolutionStage.PREVENTION,
                    "Add disk and queue saturation alerts with capacity forecasting.",
                    "Earlier warning prevents service interruption.",
                    "Capacity risk is detected before queues block.",
                    ActionRisk.LOW,
                    None,
                ),
            ],
        }
        selected = catalog.get(scenario_id, catalog["certificate_expiry"])
        return [
            ResolutionAction(
                id=f"A-{index:03d}",
                stage=stage,
                action=action,
                rationale=rationale,
                expected_outcome=outcome,
                evidence_ids=evidence_ids,
                confidence=confidence,
                risk=risk,
                rollback_action=rollback,
            )
            for index, (stage, action, rationale, outcome, risk, rollback) in enumerate(
                selected, start=1
            )
        ]

    @staticmethod
    def _verification(scenario_id: str) -> list[VerificationCriterion]:
        scenario_specific = {
            "certificate_expiry": ("TLS handshake errors", "No new errors", "splunkd.log"),
            "firewall_block": ("TCP 9997 reachability", "Successful", "network health check"),
            "outputs_misconfiguration": (
                "Effective indexer destination",
                "Approved endpoint",
                "btool output",
            ),
            "disk_full": ("Filesystem utilization", "Below operational threshold", "host metrics"),
        }
        metric, expected, source = scenario_specific.get(
            scenario_id, scenario_specific["certificate_expiry"]
        )
        return [
            VerificationCriterion(
                id="V-001",
                metric=metric,
                condition="matches recovery target",
                expected_value=expected,
                evidence_source=source,
            ),
            VerificationCriterion(
                id="V-002",
                metric="Event freshness",
                condition="new events arrive continuously",
                expected_value="Within the accepted ingestion SLA",
                evidence_source="Splunk internal metrics",
            ),
            VerificationCriterion(
                id="V-003",
                metric="Forwarding queue health",
                condition="queues are not blocked and backlog declines",
                expected_value="Healthy / draining",
                evidence_source="Heavy Forwarder telemetry",
            ),
        ]

    @staticmethod
    def _risks(scenario_id: str) -> list[str]:
        common = [
            "All write actions require human approval and an approved runbook.",
            "Recovery may briefly interrupt forwarding while configuration is reloaded.",
        ]
        if scenario_id == "disk_full":
            common.append(
                "Cleanup actions can remove required data if paths are not reviewed first."
            )
        return common
