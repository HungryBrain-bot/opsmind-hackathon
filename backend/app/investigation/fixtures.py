from datetime import datetime, timedelta, timezone

from app.schemas.evidence import Evidence, EvidenceCategory, EvidenceReliability
from app.schemas.hypothesis import Hypothesis, HypothesisStatus


NOW = datetime.now(timezone.utc)


def heavy_forwarder_hypotheses() -> list[Hypothesis]:
    return [
        Hypothesis(
            id="H-001",
            title="Expired Heavy Forwarder client certificate",
            rationale="TLS handshake errors and a matching historical incident make certificate failure plausible.",
            status=HypothesisStatus.SUPPORTED,
            confidence=0.94,
        ),
        Hypothesis(
            id="H-002",
            title="Incorrect outputs.conf destination",
            rationale="A wrong indexer destination is a common forwarding failure.",
            status=HypothesisStatus.REJECTED,
            confidence=0.12,
        ),
        Hypothesis(
            id="H-003",
            title="Network or indexer connectivity failure",
            rationale="The destination connection failed and required direct validation.",
            status=HypothesisStatus.REJECTED,
            confidence=0.18,
        ),
        Hypothesis(
            id="H-004",
            title="Disk pressure or blocked queues",
            rationale="Queue growth can result from local resource pressure.",
            status=HypothesisStatus.REJECTED,
            confidence=0.08,
        ),
    ]


def heavy_forwarder_evidence() -> list[Evidence]:
    return [
        Evidence(
            id="E-001",
            title="Current TLS handshake failure",
            content="splunkd.log reports SSL handshake failure while connecting to IDX-CLUSTER-01:9997.",
            category=EvidenceCategory.OPERATIONAL,
            source="query_splunk_internal_logs",
            observed_at=NOW - timedelta(minutes=3),
            reliability=EvidenceReliability.HIGH,
            supports=["H-001"],
            entities=["HF-PROD-02", "IDX-CLUSTER-01"],
        ),
        Evidence(
            id="E-002",
            title="Client certificate expired",
            content="CERT-HF-PROD-02 expired before the forwarding interruption began.",
            category=EvidenceCategory.CONFIGURATION,
            source="get_certificate_status",
            observed_at=NOW - timedelta(minutes=2),
            reliability=EvidenceReliability.HIGH,
            supports=["H-001"],
            entities=["HF-PROD-02", "CERT-HF-PROD-02"],
        ),
        Evidence(
            id="E-003",
            title="Matching historical incident",
            content="A prior Heavy Forwarder incident produced the same TLS error after certificate expiry.",
            category=EvidenceCategory.HISTORICAL,
            source="search_historical_incidents",
            observed_at=NOW - timedelta(minutes=6),
            reliability=EvidenceReliability.MEDIUM,
            supports=["H-001"],
            entities=["HF-PROD-02"],
            current=False,
        ),
        Evidence(
            id="E-004",
            title="Destination configuration validated",
            content="outputs.conf points to the expected IDX-CLUSTER-01:9997 destination.",
            category=EvidenceCategory.CONFIGURATION,
            source="get_component_relationships",
            observed_at=NOW - timedelta(minutes=4),
            reliability=EvidenceReliability.HIGH,
            contradicts=["H-002"],
            entities=["HF-PROD-02", "IDX-CLUSTER-01"],
        ),
        Evidence(
            id="E-005",
            title="Indexer endpoint reachable",
            content="TCP connectivity to IDX-CLUSTER-01:9997 succeeds from the Heavy Forwarder host.",
            category=EvidenceCategory.OPERATIONAL,
            source="get_heavy_forwarder_health",
            observed_at=NOW - timedelta(minutes=4),
            reliability=EvidenceReliability.HIGH,
            contradicts=["H-003"],
            entities=["HF-PROD-02", "IDX-CLUSTER-01"],
        ),
        Evidence(
            id="E-006",
            title="Local resources healthy",
            content="Disk, memory, and splunkd service state are healthy; output queues are growing due to failed TLS sessions.",
            category=EvidenceCategory.OPERATIONAL,
            source="get_heavy_forwarder_health",
            observed_at=NOW - timedelta(minutes=5),
            reliability=EvidenceReliability.HIGH,
            contradicts=["H-004"],
            entities=["HF-PROD-02"],
        ),
    ]
