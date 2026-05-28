---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 27 — Versioning and Artifact Registry

## 1. Objective

Every corpus, dataset, ontology, RAG index, prompt pack, model, and release must be versioned and traceable.

## 2. Artifact types

```text
CORPUS
DATASET
RAG_INDEX
ONTOLOGY
PROMPT_PACK
MODEL_CHECKPOINT
MODEL_ALIAS
BENCHMARK
RELEASE
```

## 3. Version format

```text
atman-corpus-0.2.0
atman-dataset-sft-0.2.1
atman-rag-0.2.3
atman-ontology-0.1.8
atman-prompt-acharya-0.2.0
atman-model-hindi-0.2.1
atman-release-0.2.0
```

## 4. Artifact manifest

```json
{
  "artifact_id": "uuid",
  "artifact_type": "RAG_INDEX",
  "name": "atman-rag",
  "version": "0.2.3",
  "hash": "sha256:...",
  "storage_uri": "s3://...",
  "source_artifacts": ["uuid"],
  "created_by": "uuid",
  "created_at": "...",
  "status": "candidate|approved|deprecated|revoked"
}
```

## 5. Model alias rule

`Atman-Prod` is an alias, not a checkpoint name. It points to exactly one approved model checkpoint.

## 6. Immutability

Published artifact versions are immutable. Fixes require a new version.

## 7. Lineage graph

Artifact registry must answer:

```text
Which sources built this dataset?
Which dataset trained this checkpoint?
Which checkpoint served this answer?
Which RAG index supplied this citation?
Which eval run approved this release?
```

## 8. Revocation

Artifacts can be revoked when rights, safety, or quality problems are found. Revocation must cascade to dependent release gates.
