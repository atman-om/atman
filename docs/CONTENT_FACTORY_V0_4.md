# Content Factory v0.4

## Goal

v0.4 turns Atman from a single-output generator into a governed content production system.

## Pipeline

```text
source corpus
→ RAG retrieval
→ template rendering / Qwen runtime later
→ quality score
→ review queue
→ export artifact
```

## Release invariant

Generated material is not public by default. It moves through review states before export or publication.

## Review states

```text
REVIEW_PENDING
NEEDS_REVISION
APPROVED
REJECTED
AUTO_BLOCKED
```

## Quality flags

```text
NO_CITATION
LOW_SOURCE_COVERAGE
SOURCE_REQUIRED_BUT_MISSING
UNVERIFIED_SANSKRIT
RITUAL_SAFETY_REVIEW
TOO_SHORT
```
