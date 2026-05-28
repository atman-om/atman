# Wide Corpus Acquisition v1.0.5

## Rule

Scrape/discover broadly. Quarantine first. Verify before canonical use.

## Zones

```text
Z0_DISCOVERY
Z1_QUARANTINE
Z2_CANDIDATE_CANONICAL
Z3_VERIFIED_CANONICAL
Z4_TRAINING_APPROVED
```

## API

```text
POST /acquisition/jobs
GET  /acquisition/jobs
```

## Promotion Logic

The acquisition scorer considers:

- content length,
- Dharma/source relevance terms,
- rights signal,
- canonical candidate metadata.

Only high-quality rights-clean items are auto-marked as `Z2_CANDIDATE_CANONICAL`. Everything else stays in quarantine.
