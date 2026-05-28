---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 25 — Runtime Safety and Guardrails

## 1. Objective

Ensure Atman's public runtime remains source-grounded, safe, non-hallucinatory, and culturally precise.

## 2. Blocked behaviors

```text
inventing Sanskrit
claiming unverifiable revelation
fake citations
harmful ritual instructions
medical/legal certainty
sectarian absolutism
copyright reproduction
personalized coercive spiritual claims
```

## 3. Runtime safety pipeline

```text
query
→ intent classification
→ risk classification
→ retrieval
→ source coverage assessment
→ policy validation
→ synthesis
→ citation verification
→ hallucination scoring
→ answer contract validation
→ response release
```

## 4. Risk classes

| Risk | Handling |
|---|---|
| normal learning | answer with citations |
| scripture quote | exact source required |
| no-source claim | safe uncertainty |
| ritual/tantra | non-procedural + caution |
| medical/legal | general info + professional referral |
| sectarian comparison | scoped, comparative wording |
| self-harm/violence | platform safety policy handling |

## 5. Contract checks

```json
{
  "has_source_for_scripture_claim": true,
  "no_fake_shloka": true,
  "no_unsafe_instruction": true,
  "sampradaya_scope_clear": true,
  "copyright_safe": true,
  "uncertainty_when_needed": true
}
```

## 6. Sanskrit validation

Generated Sanskrit is prohibited unless it is directly copied from verified retrieved source chunks or a validated transliteration/conversion of retrieved text.

## 7. Escalation

If a production answer violates hard safety rules:

```text
log event
flag answer
notify Garuda Watch
open incident if severe
include answer/session/source pack for audit
```
