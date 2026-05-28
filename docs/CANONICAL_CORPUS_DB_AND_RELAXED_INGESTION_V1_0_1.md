# Canonical Corpus DB + Relaxed Ingestion — Atman v1.0.1

## Product decision

Atman now separates wide intake from trusted knowledge.

```text
Scrape/discover broadly → quarantine → verify → canonical corpus → RAG/training
```

Public citations may be hidden. Internal provenance is mandatory.

## Corpus zones

```text
Z0_DISCOVERY              = metadata/snippet discovery
Z1_QUARANTINE             = raw text snapshot, not authority
Z2_CANDIDATE_CANONICAL    = structurally aligned but not final
Z3_VERIFIED_CANONICAL     = trusted answer/RAG source
Z4_TRAINING_APPROVED      = rights + quality approved for training
```

## New DB objects

```text
canonical_works
canonical_editions
canonical_passages
source_snapshots
claim_evidence
corpus_promotion_events
```

## New APIs

```text
POST /canonical/works
GET  /canonical/works
POST /canonical/passages
GET  /canonical/passages/search
POST /canonical/source-snapshots
POST /canonical/import/manifest
POST /canonical/claims/check
POST /canonical/answers/generate
POST /canonical/promotions
```

## Citation modes

```text
hidden  = public user sees no citation block; backend stores evidence
source  = source name + locator
scholar = full internal evidence details
```

## Use case

```bash
python scripts/import_canonical_manifest.py fixtures/canonical/gita_seed_manifest.json
```

Then call:

```text
POST /canonical/answers/generate
{
  "question": "कर्म योग क्या है?",
  "citation_mode": "hidden"
}
```

## Hard invariant

Atman may ingest broadly, but it must not answer/train from unverified quarantine snapshots.
