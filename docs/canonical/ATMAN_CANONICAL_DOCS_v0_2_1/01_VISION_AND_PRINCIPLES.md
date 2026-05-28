---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 01 — Vision, Scope, and Product Principles

## 1. Product statement

Atman is a Hindi-first Sanātan Dharma AI platform for source-grounded learning, scripture explanation, concept clarification, and scholar-grade exploration.

The first public experience is **Ask Atman**: a cited Dharma assistant that answers in simple Hindi by default.

## 2. Primary users

| User | Need |
|---|---|
| General learner | simple Hindi explanation of Dharma concepts |
| Student/devotee | shloka meaning, word breakdown, source context |
| Teacher/content creator | structured explanations, misconception correction |
| Scholar/advanced user | source comparison, sampradāya-aware interpretation |
| Internal reviewer | corpus review, evaluation, release approval |
| Content manager | source triage, rights workflow, quality management |

## 3. Initial domain scope

MVP sequence:

1. Bhagavad Gita;
2. Principal Upanishads;
3. Ramayana;
4. Mahabharata dharma episodes;
5. Puranas;
6. Darshanas;
7. commentarial traditions.

## 4. Default language policy

Atman is **Hindi-first**.

Default answer mode:

```text
सरल हिंदी + स्रोत संकेत + आवश्यकता पड़ने पर परम्परा-भेद
```

English and Sanskrit are secondary but structurally supported.

## 5. Product modes

| Mode | Description |
|---|---|
| Ask Atman | direct Q&A |
| Shloka Explainer | shloka meaning, word breakdown, source context |
| Source Explorer | browse texts, chapters, chunks, citations |
| Scholar Mode | deeper comparative answers |
| Review Studio | corpus and answer review |
| RAG Debugger | internal retrieval debugging |
| NyayaBench Viewer | eval runs, regressions, hard failures |

## 6. Out-of-scope for MVP

- claiming priest/guru authority;
- unsupported ritual/tantra procedure generation;
- political mobilization content;
- full copyrighted book reproduction;
- final doctrinal claims without tradition/source context;
- replacing human scholarship or legal/medical advice.

## 7. Product success metrics

| Metric | Target |
|---|---:|
| Hindi answer usefulness | ≥ 90% positive internal rating |
| Citation validity | ≥ 98% for production |
| Fake shloka rate | ≤ 1% |
| No-source safe refusal | ≥ 95% correct behavior |
| Retrieval source hit rate | ≥ 85% for covered corpus |
| User feedback resolution loop | ≤ 7 days for critical clusters |

## 8. Execution principles

```text
No invented scripture.
No source-free certainty.
No copyrighted reproduction without rights.
No public release without NyayaBench.
No hidden artifact drift.
No model-only knowledge authority.
```
