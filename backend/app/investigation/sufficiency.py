from collections import Counter

from app.schemas.evidence import Evidence, EvidenceCategory
from app.schemas.hypothesis import Hypothesis
from app.schemas.investigation import StopReason


class EvidenceSufficiencyEngine:
    """Deterministic and explainable stopping rules for the hackathon MVP."""

    def __init__(self, confidence_threshold: float = 0.80) -> None:
        self.confidence_threshold = confidence_threshold

    def evaluate(
        self,
        leading_hypothesis: Hypothesis,
        evidence: list[Evidence],
    ) -> tuple[StopReason, float, float]:
        supporting = [item for item in evidence if leading_hypothesis.id in item.supports]
        categories = Counter(item.category for item in supporting)
        independent_categories = len(categories)
        has_current_operational = any(
            item.category == EvidenceCategory.OPERATIONAL and item.current for item in supporting
        )
        unresolved_high_contradictions = any(
            leading_hypothesis.id in item.contradicts and item.reliability == "high"
            for item in evidence
        )

        rules_passed: list[str] = []
        rules_failed: list[str] = []

        checks = {
            "At least three corroborating evidence items": len(supporting) >= 3,
            "At least two independent evidence categories": independent_categories >= 2,
            "At least one current operational observation": has_current_operational,
            "No unresolved high-reliability contradiction": not unresolved_high_contradictions,
            "Leading hypothesis exceeds confidence threshold": (
                leading_hypothesis.confidence >= self.confidence_threshold
            ),
        }
        for name, passed in checks.items():
            (rules_passed if passed else rules_failed).append(name)

        reliability_weights = {"high": 1.0, "medium": 0.65, "low": 0.35}
        weighted_support = sum(reliability_weights[item.reliability] for item in supporting)
        evidence_strength = min(1.0, weighted_support / 3.0)
        completeness = sum(checks.values()) / len(checks)
        sufficient = all(checks.values())

        summary = (
            "Leading hypothesis is corroborated by independent current evidence."
            if sufficient
            else "More evidence is required before a defensible verdict can be issued."
        )
        return (
            StopReason(
                sufficient=sufficient,
                summary=summary,
                rules_passed=rules_passed,
                rules_failed=rules_failed,
            ),
            round(evidence_strength, 2),
            round(completeness, 2),
        )
