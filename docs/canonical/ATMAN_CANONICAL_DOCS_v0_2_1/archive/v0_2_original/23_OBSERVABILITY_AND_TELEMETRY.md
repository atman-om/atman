---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 23 — Observability and Telemetry

## 1. Objective

Atman must expose enough telemetry to detect quality regressions, latency problems, cost spikes, safety failures, and citation corruption.

## 2. Metrics

```text
query_latency_ms
retrieval_latency_ms
rerank_latency_ms
inference_latency_ms
total_answer_latency_ms
citation_failure_rate
hallucination_flag_rate
fake_shloka_flag_rate
no_source_refusal_rate
feedback_negative_rate
token_input_count
token_output_count
token_cost_estimate
gpu_utilization
cache_hit_rate
qdrant_query_latency_ms
worker_queue_depth
```

## 3. Logs

Structured JSON logs required for:

```text
API requests
source uploads
review decisions
RAG retrievals
answer contract failures
NyayaBench runs
release gate decisions
incidents
rollbacks
```

## 4. Trace spans

`/ask` trace must include:

```text
request_received
intent_classification
risk_classification
query_expansion
bm25_retrieval
dense_retrieval
reranking
source_pack_build
llm_generation
citation_validation
contract_validation
response_returned
```

## 5. Dashboards

| Dashboard | Purpose |
|---|---|
| Runtime Quality | hallucination, citation, feedback |
| RAG Performance | recall proxy, latency, empty retrievals |
| Corpus Operations | ingestion/review queues |
| Training/Eval | checkpoint/eval trends |
| Infra | CPU/GPU/memory/queues |
| Cost | token, GPU, storage, egress |

## 6. Alerts

| Alert | Severity |
|---|---|
| unsafe output detected | P0 |
| citation failure spike | P1 |
| fake shloka detected in prod | P1 |
| retrieval empty-rate spike | P2 |
| latency SLO breach | P2 |
| queue backlog high | P3 |

## 7. Privacy

Telemetry must avoid storing sensitive personal data unless required for debugging and permitted by policy. Redaction must run before long-term storage.
