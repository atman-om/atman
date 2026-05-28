# Corpus Review Workflow

## Source status ladder

```text
INGESTED → PARSED → CHUNKED → EMBEDDED/INDEXED → APPROVED_Z1 → APPROVED_Z2
```

## Rights gate

Z2 is blocked unless rights status is one of:

- `PUBLIC_DOMAIN_VERIFIED`
- `LICENSED_VERIFIED`
- `OPEN_LICENSE_VERIFIED`
- `USER_OWNED`
- `NO_TRAINING_ALLOWED` for RAG-only use

## Chunk review decisions

- `approve` → `APPROVED`
- `reject` → `REJECTED`
- `needs_revision` → `NEEDS_REVISION`
- `revise` → `REVIEW_PENDING`
- `deprecate` → `DEPRECATED`
