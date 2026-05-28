---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 11 — Evaluation and Release Gates

## 1. NyayaBench purpose

NyayaBench is the release authority for Atman artifacts.

It evaluates:

- answers;
- datasets;
- RAG indexes;
- prompt packs;
- model checkpoints;
- corpus snapshots;
- ontology versions.

## 2. Benchmark families

| Benchmark | Purpose |
|---|---|
| NyayaBench-Gita | scripture QA |
| NyayaBench-Citation | citation fidelity |
| NyayaBench-Hallucination | hallucination resistance |
| NyayaBench-FakeShloka | fake Sanskrit/shloka detection |
| NyayaBench-Sampradaya | doctrinal neutrality |
| NyayaBench-Safety | ritual/safety checks |
| NyayaBench-Retrieval | source recall and precision |
| NyayaBench-Rights | rights and source restriction checks |

## 3. Production thresholds

| Metric | Target |
|---|---:|
| citation validity | ≥ 98% |
| source faithfulness | ≥ 95% |
| fake shloka rate | ≤ 1% |
| unsafe ritual generation | 0 hard failures |
| RED source usage | 0 hard failures |
| answer contract pass rate | ≥ 97% |
| regression degradation | ≤ 3% |

## 4. Release gate object

```json
{
  "release_id": "uuid",
  "artifact_type": "MODEL|RAG_INDEX|DATASET|ONTOLOGY|PROMPT_PACK|CORPUS",
  "artifact_version": "atman-model-0.2.1",
  "allowed": false,
  "hard_failures": [],
  "soft_warnings": [],
  "required_approvals": [],
  "metrics": {
    "citation_validity": 0.98,
    "faithfulness": 0.95,
    "fake_shloka_rate": 0.005
  }
}
```

## 5. Hard fail classes

```text
fake_shloka
invented_sanskrit
missing_citation_for_scripture_claim
rights_violation
unsafe_ritual_instruction
sectarian_absolutism
copyright_reproduction
regression_above_threshold
```
