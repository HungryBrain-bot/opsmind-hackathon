import asyncio

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse, StreamingResponse

from app.core.settings import Settings, get_settings
from app.investigation.engine import InvestigationEngine
from app.investigation.explainability import DecisionTraceBuilder
from app.investigation.reporting import InvestigationReportBuilder
from app.investigation.store import InvestigationNotFoundError, InvestigationStore
from app.storage.file_repository import FileInvestigationRepository
from app.storage.models import InvestigationHistoryItem
from app.schemas.explainability import InvestigationDecisionTrace
from app.schemas.investigation import InvestigationRequest, InvestigationResult, InvestigationStatus
from app.schemas.report import InvestigationReport

router = APIRouter(prefix="/investigations", tags=["investigations"])
_settings = get_settings()
_repository = FileInvestigationRepository(_settings.investigation_storage_path)
_store = InvestigationStore(_repository)


def get_store() -> InvestigationStore:
    return _store


def get_engine(
    settings: Settings = Depends(get_settings),
    store: InvestigationStore = Depends(get_store),
) -> InvestigationEngine:
    return InvestigationEngine(settings, store)




@router.get("/history", response_model=list[InvestigationHistoryItem])
async def list_investigation_history(
    query: str | None = None,
    status: str | None = None,
    environment: str | None = None,
    priority: str | None = None,
    root_cause: str | None = None,
) -> list[InvestigationHistoryItem]:
    return _repository.list(query, status, environment, priority, root_cause)


@router.get("/history/{investigation_id}", response_model=InvestigationResult)
async def get_historical_investigation(investigation_id: str) -> InvestigationResult:
    try:
        return _repository.get(investigation_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Investigation not found") from exc


@router.get("/history/{investigation_id}/report.md")
async def download_historical_report(investigation_id: str) -> PlainTextResponse:
    try:
        content = _repository.get_report(investigation_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Investigation report not found") from exc
    filename = f"opsmind-investigation-{investigation_id}.md"
    return PlainTextResponse(
        content,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/history/{investigation_id}", status_code=204)
async def delete_historical_investigation(investigation_id: str) -> None:
    try:
        _repository.delete(investigation_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Investigation not found") from exc


@router.post("", response_model=InvestigationResult, status_code=202)
async def create_investigation(
    request: InvestigationRequest,
    background_tasks: BackgroundTasks,
    engine: InvestigationEngine = Depends(get_engine),
) -> InvestigationResult:
    result = await engine.create(request)
    background_tasks.add_task(engine.run, result.investigation_id)
    return result


@router.get("/{investigation_id}", response_model=InvestigationResult)
async def get_investigation(
    investigation_id: str,
    store: InvestigationStore = Depends(get_store),
) -> InvestigationResult:
    try:
        return await store.get(investigation_id)
    except InvestigationNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Investigation not found") from exc


@router.get("/{investigation_id}/events")
async def stream_events(
    investigation_id: str,
    request: Request,
    store: InvestigationStore = Depends(get_store),
) -> StreamingResponse:
    try:
        await store.get(investigation_id)
    except InvestigationNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Investigation not found") from exc

    async def event_stream():
        offset = 0
        terminal = {
            InvestigationStatus.COMPLETED,
            InvestigationStatus.INCONCLUSIVE,
            InvestigationStatus.FAILED,
        }
        while True:
            if await request.is_disconnected():
                break
            events = await store.events_from(investigation_id, offset)
            for event in events:
                offset += 1
                payload = event.model_dump_json()
                yield f"id: {event.sequence}\nevent: {event.type.value}\ndata: {payload}\n\n"
            current = await store.get(investigation_id)
            if current.status in terminal and not events:
                break
            if not events:
                yield ": keep-alive\n\n"
                await store.wait_for_events(investigation_id, timeout=10.0)
            await asyncio.sleep(0)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/{investigation_id}/timeline")
async def get_timeline(
    investigation_id: str,
    store: InvestigationStore = Depends(get_store),
) -> list[dict]:
    try:
        result = await store.get(investigation_id)
    except InvestigationNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Investigation not found") from exc
    return [
        {
            "sequence": index,
            "timestamp": item.timestamp,
            "phase": item.phase,
            "title": item.title,
            "detail": item.detail,
        }
        for index, item in enumerate(result.timeline, start=1)
    ]


@router.get("/{investigation_id}/notebook")
async def get_notebook(
    investigation_id: str,
    store: InvestigationStore = Depends(get_store),
) -> dict:
    try:
        result = await store.get(investigation_id)
    except InvestigationNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Investigation not found") from exc
    entries = [
        {
            "type": "problem",
            "title": "Problem statement",
            "content": result.problem,
            "evidence_ids": [],
        }
    ]
    entries.extend(
        {
            "type": "hypothesis",
            "title": item.title,
            "content": item.rationale,
            "evidence_ids": item.supporting_evidence_ids + item.contradicting_evidence_ids,
        }
        for item in result.hypotheses
    )
    entries.extend(
        {
            "type": "observation",
            "title": item.title,
            "content": item.content,
            "evidence_ids": [item.id],
        }
        for item in result.evidence
    )
    if result.verdict:
        entries.append(
            {
                "type": "verdict",
                "title": "Final verdict",
                "content": result.verdict,
                "evidence_ids": result.verdict_evidence_ids,
            }
        )
    return {
        "investigation_id": result.investigation_id,
        "summary": result.stop_reason.summary,
        "entries": entries,
    }


@router.get(
    "/{investigation_id}/decision-trace",
    response_model=InvestigationDecisionTrace,
)
async def get_decision_trace(
    investigation_id: str,
    store: InvestigationStore = Depends(get_store),
) -> InvestigationDecisionTrace:
    try:
        result = await store.get(investigation_id)
    except InvestigationNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Investigation not found") from exc
    return DecisionTraceBuilder().build(result)


@router.get("/{investigation_id}/report", response_model=InvestigationReport)
async def get_investigation_report(
    investigation_id: str,
    store: InvestigationStore = Depends(get_store),
) -> InvestigationReport:
    try:
        result = await store.get(investigation_id)
    except InvestigationNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Investigation not found") from exc
    return InvestigationReportBuilder().build(result)


@router.get("/{investigation_id}/report.md")
async def download_investigation_report(
    investigation_id: str,
    store: InvestigationStore = Depends(get_store),
) -> PlainTextResponse:
    try:
        result = await store.get(investigation_id)
    except InvestigationNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Investigation not found") from exc
    content = InvestigationReportBuilder().to_markdown(result)
    filename = f"opsmind-investigation-{investigation_id}.md"
    return PlainTextResponse(
        content,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
