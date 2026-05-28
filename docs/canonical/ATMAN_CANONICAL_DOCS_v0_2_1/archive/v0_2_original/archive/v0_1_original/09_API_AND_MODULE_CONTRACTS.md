# 09 — API and Module Contracts

## 1. Core API groups

| Group | Endpoints |
|---|---|
| Health | `GET /health` |
| Sources | `POST /sources`, `GET /sources`, `GET /sources/{id}` |
| Uploads | `POST /uploads/pdf`, `GET /uploads/pdf-preview/{id}` |
| Review | `GET /review/sources`, `POST /review/sources/{id}/decision` |
| Ask | `POST /ask` |
| RAG | `POST /rag/debug`, `POST /index/rebuild` |
| Datasets | `POST /datasets/sft/build`, `POST /datasets/dpo/build`, `POST /datasets/export` |
| Training | `POST /training/checkpoints`, `GET /training/checkpoints` |
| Eval | `POST /eval/run` |
| Licensing | `GET /licensing/dashboard`, `POST /licensing/sources/{id}` |
| Corpus | `POST /corpus/deduplicate`, `GET /corpus/quality/chunks` |
| Sanskrit | `POST /sanskrit/padaccheda`, `POST /sanskrit/morphology` |
| Provenance | `GET /provenance/sources/{id}` |
| Release | `GET /release/gate` |

## 2. Ask request

```json
{
  "question": "गीता 2.47 का अर्थ बताओ",
  "language": "hi",
  "mode": "simple"
}
```

## 3. Ask response

```json
{
  "answer": "...",
  "citations": [
    {
      "source_id": "...",
      "chunk_id": "...",
      "title": "Bhagavad Gita 2.47",
      "work": "Bhagavad Gita",
      "chapter": "2",
      "verse": "47",
      "score": 0.91
    }
  ],
  "confidence": "high",
  "limitations": null
}
```

## 4. Review decision

```json
{
  "decision": "promote_to_production",
  "reason": "Public-domain source verified"
}
```

## 5. Dataset build request

```json
{
  "output_format": "messages",
  "intended_use": "lab"
}
```

## 6. Release gate response

```json
{
  "release_allowed": false,
  "blocking_issues": [
    "insufficient production samples",
    "citation threshold not met"
  ],
  "metrics": {}
}
```
