# Diagnostics

Diagnostics inspect replay and graph health without correcting history.

Components:

- `ProjectionInspector`: node and edge counts.
- `ReplayAnalyzer`: event count and ordering.
- `GraphIntegrityInspector`: edge endpoint validation.

Diagnostics report divergence. They do not suppress or mutate replay state.

