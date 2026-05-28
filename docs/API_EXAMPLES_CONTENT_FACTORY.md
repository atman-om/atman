# Atman v0.4 Content Factory API Examples

## Create batch

```bash
curl -X POST http://localhost:8000/content/batches \
  -H 'Content-Type: application/json' \
  -d '{"name":"Gita notes","content_type":"notes","topic":"कर्मयोग","quantity":5,"source_required":true}'
```

## Run batch

```bash
curl -X POST http://localhost:8000/content/batches/<batch_id>/run
```

## List review queue

```bash
curl 'http://localhost:8000/content/items?review_status=REVIEW_PENDING'
```

## Approve item

```bash
curl -X POST http://localhost:8000/content/items/<item_id>/review \
  -H 'Content-Type: application/json' \
  -d '{"decision":"APPROVED","reason":"source checked"}'
```

## Export approved content

```bash
curl -X POST http://localhost:8000/content/exports \
  -H 'Content-Type: application/json' \
  -d '{"export_format":"jsonl","review_status":"APPROVED"}'
```
