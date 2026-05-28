---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 15 — Agent Tool Contracts

## 1. Contract principle

Agents are orchestrators. Tools perform bounded actions with typed inputs, typed outputs, audit logs, and failure modes.

## 2. Common envelope

### Request envelope

```json
{
  "request_id": "uuid",
  "actor_id": "uuid",
  "workspace_id": "default",
  "tool_name": "corpus.parse_pdf",
  "payload": {},
  "dry_run": false
}
```

### Response envelope

```json
{
  "request_id": "uuid",
  "status": "success|partial|failed",
  "result": {},
  "warnings": [],
  "errors": []
}
```

## 3. ShrutiKosh Corpus Agent tools

| Tool | Input | Output |
|---|---|---|
| `source.register` | file metadata | `source_id` |
| `file.scan` | object URI | scan report |
| `pdf.extract_text` | PDF URI | page text blocks |
| `ocr.extract` | image/page URI | OCR text + confidence |
| `text.normalize` | raw text | normalized text |
| `citation.parse` | text + source type | locator map |
| `chunk.create` | normalized text | chunk list |
| `rights.classify_draft` | source metadata | draft rights signal |
| `quality.score` | chunks | quality report |
| `ontology.tag` | chunks | entity/edge candidates |
| `dataset.export` | approved chunk set | JSONL artifact |

### Example: `chunk.create`

```json
{
  "source_id": "uuid",
  "strategy": "verse|heading|semantic",
  "max_tokens": 700,
  "overlap_tokens": 80
}
```

Output:

```json
{
  "chunk_ids": ["uuid"],
  "warnings": ["locator_missing_on_3_chunks"]
}
```

## 4. Atman Tune Agent tools

| Tool | Purpose |
|---|---|
| `dataset.validate` | validates source lineage and intended use |
| `dataset.mix` | creates mixture from approved inputs |
| `train.launch_lora` | launches LoRA/QLoRA run |
| `checkpoint.register` | records checkpoint metadata/hash |
| `checkpoint.compare` | compares candidate with baseline |
| `model.promote_candidate` | submits release-gate request |

## 5. NyayaBench tools

| Tool | Purpose |
|---|---|
| `eval.run` | execute benchmark |
| `citation.verify` | source/citation matching |
| `fake_shloka.detect` | Sanskrit/shloka trap detection |
| `faithfulness.score` | source-pack vs answer |
| `safety.check` | runtime safety checks |
| `regression.compare` | compare candidate vs previous release |

## 6. Atman Acharya Runtime tools

| Tool | Purpose |
|---|---|
| `intent.classify` | question type |
| `risk.classify` | safety/source risk |
| `retrieve.source_pack` | retrieve evidence |
| `answer.generate` | LLM response |
| `answer.validate_contract` | policy gate |
| `citation.render` | final citation formatting |
| `feedback.log` | user feedback |

## 7. Garuda Watch tools

| Tool | Purpose |
|---|---|
| `metrics.aggregate` | runtime metrics |
| `cluster.feedback` | group user reports |
| `drift.detect` | retrieval/model drift |
| `incident.open` | create incident |
| `rollback.prepare` | generate rollback plan |

## 8. Failure policy

Tools must fail closed when they cannot verify rights, source locator, citation integrity, or safety state.
