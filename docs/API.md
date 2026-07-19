# OpsMind API

## Base URL

```text
http://127.0.0.1:8000/api/v1
```

Interactive OpenAPI documentation is available at `/docs`.

## Health and runtime

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Application health check |
| GET | `/runtime` | Current runtime mode and configuration summary |

## Investigation Packs

| Method | Path | Purpose |
|---|---|---|
| GET | `/packs` | List available Investigation Packs |
| GET | `/packs/{pack_id}` | Read one Investigation Pack |

## Investigations

| Method | Path | Purpose |
|---|---|---|
| POST | `/investigations` | Create and start an investigation |
| GET | `/investigations/{id}` | Read current investigation state |
| GET | `/investigations/{id}/events` | Stream structured investigation events over SSE |
| GET | `/investigations/{id}/timeline` | Read ordered investigation timeline |
| GET | `/investigations/{id}/notebook` | Read investigation notebook entries |
| GET | `/investigations/{id}/decision-trace` | Read selected and rejected hypothesis reasoning |
| GET | `/investigations/{id}/report` | Read structured JSON report |
| GET | `/investigations/{id}/report.md` | Download Markdown report |

`POST /investigations` returns HTTP `202 Accepted` because execution continues as a background task. Clients can subscribe to the SSE endpoint or poll the investigation state.

## Investigation History

| Method | Path | Purpose |
|---|---|---|
| GET | `/investigations/history` | List and filter persisted investigations |
| GET | `/investigations/history/{id}` | Reopen a persisted investigation |
| GET | `/investigations/history/{id}/report.md` | Download a persisted Markdown report |
| DELETE | `/investigations/history/{id}` | Delete a persisted investigation |

History filters supported by the list endpoint:

- `query`
- `status`
- `environment`
- `priority`
- `root_cause`

## SSE event stream

The event endpoint uses `text/event-stream`. Events include a sequence number, event type, timestamp, investigation phase, status, evidence references, and hypothesis updates where applicable.

Example client:

```javascript
const source = new EventSource(
  "/api/v1/investigations/INV-EXAMPLE/events"
);

source.onmessage = (event) => {
  console.log(JSON.parse(event.data));
};
```

## Error behavior

Unknown investigations return `404 Not Found`. Validation errors use FastAPI's standard `422 Unprocessable Entity` response.
