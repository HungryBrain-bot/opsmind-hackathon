# Visual Investigation Workspace

OpsMind v2.0 turns the investigation engine into a visual enterprise workspace. The user interface does not reconstruct reasoning. A dedicated presentation layer transforms the canonical `InvestigationResult` into stable workspace models.

## Design principles

1. **Evidence before answers** — every conclusion links to supporting and contradicting evidence.
2. **Confidence is earned** — confidence evolution is visualized by investigation round.
3. **Competing explanations stay visible** — supported and rejected hypotheses remain on the whiteboard.
4. **Resolution is a lifecycle** — containment, recovery, verification, rollback and prevention are presented as connected stages.
5. **Reasoning is replayable** — the investigation timeline can be played back as a deterministic visual narrative.
6. **One state, multiple views** — engineer and executive modes render the same backend investigation state.

## Presentation architecture

```text
Investigation Engine
        │
        ▼
InvestigationResult
        │
        ▼
InvestigationWorkspaceBuilder
        │
        ├── Evidence graph
        ├── Confidence evolution
        ├── Hypothesis board
        ├── Timeline and playback
        ├── Resolution flow
        ├── Verification checklist
        └── Knowledge capture
        │
        ▼
Visual Investigation Workspace
```

## API

```http
GET /api/v1/investigations/{investigation_id}/workspace
```

The endpoint returns presentation-ready graph nodes and edges, timeline entries, confidence points, resolution stages, verification criteria and playback events.

## Judge experience

The built-in scenarios are deterministic and run locally. A judge can start an investigation, watch confidence evolve, inspect evidence graph nodes, compare hypotheses, replay the reasoning sequence and switch to an executive summary without an external API key.
