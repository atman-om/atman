# Atman v0.7 — Source Explorer

## Purpose

Expose Atman corpus sources and chunks in a source-governed way.

## Public endpoints

```text
GET /public/source-explorer/search?q=karma
GET /public/source-explorer/sources/{source_id}
```

Public routes show only sources with rights status:

```text
PUBLIC_DOMAIN_VERIFIED
OPEN_LICENSE_VERIFIED
LICENSED_VERIFIED
USER_OWNED
```

and ingestion status:

```text
APPROVED_Z2
INDEXED
```

## Admin endpoints

```text
GET /source-explorer/search
GET /source-explorer/sources/{source_id}
```

Admin route can inspect non-public, reference-only, or review-pending sources for governance work.

## Design invariant

The public source explorer must never reveal rejected, unknown-rights, no-storage, or blocked source text.
