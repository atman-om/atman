# API Examples

## Create source

```bash
curl -X POST http://localhost:8000/sources \
  -H 'content-type: application/json' \
  -d '{"source_type":"text","title":"Demo","language":"hi","rights_status":"USER_OWNED","source_metadata":{"locator":"BG.2.47"},"text":"कर्मयोग..."}'
```

## Ask RAG

```bash
curl -X POST http://localhost:8000/rag/query \
  -H 'content-type: application/json' \
  -d '{"question":"गीता 2.47 का अर्थ क्या है?","top_k":5}'
```

## Generate content

```bash
curl -X POST http://localhost:8000/content/generate \
  -H 'content-type: application/json' \
  -d '{"content_type":"mcq","topic":"कर्मयोग","quantity":5}'
```
