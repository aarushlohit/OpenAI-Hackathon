# Correlation Engine

The Phase 6 correlation layer detects repeated scam infrastructure across investigations.

Components:

- `ThreatCorrelationEngine`: compares graph projections and summarizes related investigations.
- `CampaignDetector`: detects campaign hints such as reused payment methods and domain clusters.
- `EntitySimilarity`: deterministic and fuzzy matching helper for future alias correlation.

Current deterministic signals:

- Reused UPI or payment wallet.
- Reused domain.
- Shared entities across investigations.

Future-ready signals:

- Embedding-backed semantic similarity.
- Multimodal template matching.
- Recruiter alias clustering.
- Cloned portal family detection.

