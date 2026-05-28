# API Examples — v0.6 Corpus

## Upload a plaintext source

```bash
curl -X POST http://localhost:8000/corpus/upload \
  -F "title=Bhagavad Gita Demo" \
  -F "language=hi" \
  -F "rights_status=PUBLIC_DOMAIN_VERIFIED" \
  -F "locator=BG.2.47" \
  -F "file=@fixtures/corpus_sample_gita.txt"
```

## Review rights

```bash
curl -X POST http://localhost:8000/corpus/sources/{source_id}/rights \
  -H 'Content-Type: application/json' \
  -d '{"rights_status":"PUBLIC_DOMAIN_VERIFIED","evidence":{"basis":"public-domain manual review"}}'
```

## Promote source to Z2

```bash
curl -X POST http://localhost:8000/corpus/sources/{source_id}/promote \
  -H 'Content-Type: application/json' \
  -d '{"target_status":"APPROVED_Z2","evidence":{"quality":"reviewed"}}'
```

## Approve a chunk

```bash
curl -X PATCH http://localhost:8000/corpus/chunks/{chunk_id}/review \
  -H 'Content-Type: application/json' \
  -d '{"decision":"approve","quality_score":0.95,"checklist":{"citation_locator":true}}'
```
