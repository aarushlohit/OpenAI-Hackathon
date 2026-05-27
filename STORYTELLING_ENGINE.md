# Storytelling Engine

The storytelling layer converts investigation evidence into readable narratives.

Components:

- `StoryBuilder`: creates investigation narratives from context and threat score.
- `NarrativeProjection`: stable report-friendly narrative contract.
- `ExecutiveReportBuilder`: produces non-technical summaries for campus and safety teams.

Rules:

- Stories are evidence-oriented.
- Stories do not alter severity.
- Executive reports do not recompute threat scores.

