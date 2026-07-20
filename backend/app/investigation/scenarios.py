from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.schemas.evidence import Evidence, EvidenceCategory, EvidenceReliability

NOW = datetime.now(timezone.utc)


@dataclass(frozen=True)
class Scenario:
    id: str
    label: str
    root_cause: str
    verdict: str
    recommended_actions: list[str]


SCENARIOS = {
    "certificate_expiry": Scenario(
        id="certificate_expiry",
        label="INC-2026-0719-001 — Heavy Forwarder stopped forwarding",
        root_cause="Expired Heavy Forwarder client certificate",
        verdict=(
            "HF-PROD-02 stopped forwarding because its client certificate expired, "
            "causing TLS handshakes to IDX-CLUSTER-01:9997 to fail."
        ),
        recommended_actions=[
            "Renew and deploy CERT-HF-PROD-02 through the approved change process.",
            "Validate TLS connectivity and forwarding freshness after deployment.",
            "Add certificate-expiry monitoring to prevent recurrence.",
        ],
    ),
    "firewall_block": Scenario(
        id="firewall_block",
        label="INC-2026-0718-014 — No events reaching indexer cluster",
        root_cause="Network or indexer connectivity failure",
        verdict=(
            "HF-PROD-02 stopped forwarding because a firewall policy blocked TCP 9997 "
            "between the Heavy Forwarder and IDX-CLUSTER-01."
        ),
        recommended_actions=[
            "Restore the approved TCP 9997 firewall rule between HF-PROD-02 and the indexers.",
            "Retest connectivity from the Heavy Forwarder host.",
            "Confirm queued events drain and ingestion freshness recovers.",
        ],
    ),
    "outputs_misconfiguration": Scenario(
        id="outputs_misconfiguration",
        label="INC-2026-0716-003 — Forwarding failure after maintenance",
        root_cause="Incorrect outputs.conf destination",
        verdict=(
            "HF-PROD-02 stopped forwarding because outputs.conf referenced an invalid "
            "indexer destination."
        ),
        recommended_actions=[
            "Correct the indexer destination in the approved outputs.conf deployment app.",
            "Validate the effective configuration with btool.",
            "Restart or reload Splunk and confirm forwarding resumes.",
        ],
    ),
    "disk_full": Scenario(
        id="disk_full",
        label="INC-2026-0714-027 — Ingestion delay and growing queues",
        root_cause="Disk pressure or blocked queues",
        verdict=(
            "HF-PROD-02 stopped forwarding because local storage was exhausted, "
            "blocking Splunk output queues."
        ),
        recommended_actions=[
            "Recover disk space using the approved cleanup runbook.",
            "Restart or unblock Splunk queues after capacity is restored.",
            "Add disk and queue saturation alerting to prevent recurrence.",
        ],
    ),
}


def scenario_evidence(scenario_id: str) -> list[Evidence]:
    scenario_id = scenario_id if scenario_id in SCENARIOS else "certificate_expiry"
    if scenario_id == "firewall_block":
        return _firewall()
    if scenario_id == "outputs_misconfiguration":
        return _outputs()
    if scenario_id == "disk_full":
        return _disk()
    return _certificate()


def _e(id, title, content, category, source, *, supports=None, contradicts=None, current=True):
    return Evidence(
        id=id,
        title=title,
        content=content,
        category=category,
        source=source,
        observed_at=NOW - timedelta(minutes=int(id.split("-")[1])),
        reliability=EvidenceReliability.HIGH,
        supports=supports or [],
        contradicts=contradicts or [],
        entities=["HF-PROD-02", "IDX-CLUSTER-01"],
        current=current,
    )


def _certificate():
    return [
        _e(
            "E-001",
            "Current TLS handshake failure",
            "splunkd.log reports TLS handshake failures to IDX-CLUSTER-01:9997.",
            EvidenceCategory.OPERATIONAL,
            "query_splunk_internal_logs",
            supports=["H-001"],
        ),
        _e(
            "E-002",
            "Client certificate expired",
            "CERT-HF-PROD-02 expired before forwarding stopped.",
            EvidenceCategory.CONFIGURATION,
            "get_certificate_status",
            supports=["H-001"],
        ),
        _e(
            "E-003",
            "Matching Jira incident",
            "Jira incident OPS-1842 records the same TLS error after certificate expiry.",
            EvidenceCategory.HISTORICAL,
            "search_historical_incidents",
            supports=["H-001"],
            current=False,
        ),
        _e(
            "E-004",
            "Destination configuration validated",
            "outputs.conf points to IDX-CLUSTER-01:9997.",
            EvidenceCategory.CONFIGURATION,
            "get_component_relationships",
            contradicts=["H-002"],
        ),
        _e(
            "E-005",
            "TCP 9997 reachable",
            "TCP connectivity succeeds from HF-PROD-02.",
            EvidenceCategory.OPERATIONAL,
            "get_heavy_forwarder_health",
            contradicts=["H-003"],
        ),
        _e(
            "E-006",
            "Local resources healthy",
            "Disk and queues are healthy.",
            EvidenceCategory.OPERATIONAL,
            "get_heavy_forwarder_health",
            contradicts=["H-004"],
        ),
    ]


def _firewall():
    return [
        _e(
            "E-101",
            "TCP 9997 connection timeout",
            "Repeated connection attempts to IDX-CLUSTER-01:9997 time out.",
            EvidenceCategory.OPERATIONAL,
            "get_heavy_forwarder_health",
            supports=["H-003"],
        ),
        _e(
            "E-102",
            "Firewall policy changed",
            "Azure Firewall change record removed the approved TCP 9997 rule.",
            EvidenceCategory.CONFIGURATION,
            "get_component_relationships",
            supports=["H-003"],
        ),
        _e(
            "E-103",
            "Matching Jira incident",
            "Jira OPS-1764 documents identical symptoms after a firewall rule rollback.",
            EvidenceCategory.HISTORICAL,
            "search_historical_incidents",
            supports=["H-003"],
            current=False,
        ),
        _e(
            "E-104",
            "Certificate valid",
            "HF client certificate is valid for 74 more days.",
            EvidenceCategory.CONFIGURATION,
            "get_certificate_status",
            contradicts=["H-001"],
        ),
        _e(
            "E-105",
            "Destination configuration valid",
            "outputs.conf contains the approved indexer group.",
            EvidenceCategory.CONFIGURATION,
            "get_component_relationships",
            contradicts=["H-002"],
        ),
        _e(
            "E-106",
            "Disk and queues healthy",
            "Disk usage is 31%; no local blocked queue condition exists.",
            EvidenceCategory.OPERATIONAL,
            "get_heavy_forwarder_health",
            contradicts=["H-004"],
        ),
    ]


def _outputs():
    return [
        _e(
            "E-201",
            "Invalid indexer destination",
            "Effective outputs.conf targets retired host idx-old-01:9997.",
            EvidenceCategory.CONFIGURATION,
            "get_component_relationships",
            supports=["H-002"],
        ),
        _e(
            "E-202",
            "DNS resolution failure",
            "The configured retired indexer hostname no longer resolves.",
            EvidenceCategory.OPERATIONAL,
            "query_splunk_internal_logs",
            supports=["H-002"],
        ),
        _e(
            "E-203",
            "Matching Jira incident",
            "Jira OPS-1901 links the failure to an outdated deployment app.",
            EvidenceCategory.HISTORICAL,
            "search_historical_incidents",
            supports=["H-002"],
            current=False,
        ),
        _e(
            "E-204",
            "Certificate valid",
            "The deployed client certificate is valid.",
            EvidenceCategory.CONFIGURATION,
            "get_certificate_status",
            contradicts=["H-001"],
        ),
        _e(
            "E-205",
            "Approved indexer endpoint reachable",
            "The correct production indexer endpoint is reachable.",
            EvidenceCategory.OPERATIONAL,
            "get_heavy_forwarder_health",
            contradicts=["H-003"],
        ),
        _e(
            "E-206",
            "Local resources healthy",
            "Disk and queue health do not indicate local resource pressure.",
            EvidenceCategory.OPERATIONAL,
            "get_heavy_forwarder_health",
            contradicts=["H-004"],
        ),
    ]


def _disk():
    return [
        _e(
            "E-301",
            "Filesystem critically full",
            "/opt is 99% utilized with less than 200 MB free.",
            EvidenceCategory.OPERATIONAL,
            "get_heavy_forwarder_health",
            supports=["H-004"],
        ),
        _e(
            "E-302",
            "Output queues blocked",
            "Splunk metrics report blocked=true and persistent queue growth.",
            EvidenceCategory.OPERATIONAL,
            "query_splunk_internal_logs",
            supports=["H-004"],
        ),
        _e(
            "E-303",
            "Capacity policy breached",
            "Configured minimum free-space threshold has been crossed.",
            EvidenceCategory.CONFIGURATION,
            "get_component_relationships",
            supports=["H-004"],
        ),
        _e(
            "E-304",
            "Certificate valid",
            "The client certificate remains valid.",
            EvidenceCategory.CONFIGURATION,
            "get_certificate_status",
            contradicts=["H-001"],
        ),
        _e(
            "E-305",
            "Destination configuration valid",
            "outputs.conf points to the approved indexer cluster.",
            EvidenceCategory.CONFIGURATION,
            "get_component_relationships",
            contradicts=["H-002"],
        ),
        _e(
            "E-306",
            "Indexer endpoint reachable",
            "TCP 9997 connectivity succeeds.",
            EvidenceCategory.OPERATIONAL,
            "get_heavy_forwarder_health",
            contradicts=["H-003"],
        ),
    ]
