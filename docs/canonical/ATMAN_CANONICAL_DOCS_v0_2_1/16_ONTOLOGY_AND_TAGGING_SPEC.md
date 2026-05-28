---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 16 — Ontology and Tagging Specification

## 1. Objective

TattvaNet is the canonical ontology/knowledge graph layer for Atman. It connects texts, verses, concepts, traditions, commentaries, people, practices, questions, and misconceptions.

## 2. Entity types

```text
TEXT
BOOK
CHAPTER
VERSE
COMMENTARY
DARSHANA
SAMPRADAYA
ACHARYA
DEITY
CONCEPT
PRACTICE
FESTIVAL
RITUAL
PLACE
PERSON
QUESTION
MISCONCEPTION
TERM
TRANSLATION
```

## 3. Edge types

```text
PART_OF
COMMENTS_ON
EXPLAINS
CONTRADICTS
SUPPORTS
ASSOCIATED_WITH
MENTIONS
PRACTICED_IN
DERIVED_FROM
TRANSLATES
INTERPRETS_AS
HAS_MISCONCEPTION
RESOLVES_MISCONCEPTION
```

## 4. Canonical entity schema

```json
{
  "entity_id": "uuid",
  "entity_type": "CONCEPT",
  "canonical_label": "karma",
  "display_label_hi": "कर्म",
  "display_label_sa": "कर्म",
  "display_label_en": "karma",
  "aliases": ["कर्मफल", "action"],
  "transliteration": "karma",
  "script": "devanagari|iast|latin",
  "description": "...",
  "source_basis": ["chunk_id"],
  "confidence": 0.98,
  "review_status": "approved"
}
```

## 5. Canonical edge schema

```json
{
  "edge_id": "uuid",
  "source_entity_id": "uuid",
  "target_entity_id": "uuid",
  "relation_type": "EXPLAINS",
  "evidence_chunk_ids": ["uuid"],
  "confidence": 0.92,
  "tradition_scope": ["Advaita Vedanta"],
  "validity_notes": "...",
  "review_status": "approved"
}
```

## 6. Tagging pipeline

```text
chunk
→ language/script detection
→ term extraction
→ candidate entity match
→ new entity proposal when needed
→ relation proposal
→ evidence binding
→ reviewer approval
→ graph publish
```

## 7. Review rules

- Auto-tags remain candidates until approved.
- Every production edge requires evidence chunks.
- Doctrinally sensitive edges must include tradition scope.
- No ontology fact may be treated as true without evidence.

## 8. Source-of-truth precedence

```text
verified source text
→ verified commentary
→ approved ontology edge
→ model synthesis
```

Model synthesis never overrides source evidence.
