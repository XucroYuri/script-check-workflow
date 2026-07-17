# Changelog

## 3.2.0 - 2026-07-17

### Added

- Machine-readable Stage I/O and scoring contract.
- Fail-closed hard gates and deterministic scoring.
- Untrusted-script prompt isolation and reviewer tool restrictions.
- Candidate-script post-synthesis review.
- Collision-safe run IDs and no-clobber file delivery.
- Adversarial eval fixtures and CI validation.

### Changed

- Scoring applies only to the post-synthesis candidate.
- High-severity findings and high-risk writer confirmations block delivery regardless of score.
- Blocked runs produce `candidate-script`, not `standardized-script`.
- Stage 5 production readiness requires an explicit target profile.

### Removed

- Unsupported claims of “免检” and “废片率极低”.
- Mutable default-branch sponsor image references.
