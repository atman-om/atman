# Atman Repo v0.3 Architecture

```text
Client / Atman Studio
  → FastAPI API
    → PostgreSQL metadata
    → Qdrant vector index
    → Redis worker queue
    → MinIO object storage
    → Qwen runtime service, later
```

## Invariants

- Qwen is the working base family.
- RAG and source verification precede fine-tuning.
- Web ingestion is rights, robots, and provenance gated.
- External LLMs may assist extraction but cannot become Atman authority.
- Production release is blocked by NyayaBench.
