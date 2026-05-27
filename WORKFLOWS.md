# Workflows

Hermes-X workflows are declarative investigation routes selected by evidence type.

Current workflows:

- `url_intelligence`: runs intake first, then behavior and OSINT analysis in parallel.
- `screenshot_intelligence`: runs intake first, then OCR-first vision and behavior analysis in parallel.
- `document_intelligence`: runs intake first, then OCR-first vision and behavior analysis in parallel.
- `message_intelligence`: runs intake first, then behavior, OSINT, and vision analysis in parallel.

Rules:

- Workflows select agents; agents do not select each other.
- Workflows must stay provider-agnostic.
- Future workflow plugins should register declarative `WorkflowDefinition` objects.
- Flutter must render workflow state only; it must not own workflow routing.
- Workflow selection appears through `investigation_started`.
- UI clients replay workflow state from stored events after reconnect.

