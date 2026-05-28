# Atman Repo v0.6 — Corpus Ingestion and Review

v0.6 turns Atman from a public/Qwen runtime scaffold into a corpus-governed platform.

## Added

- `/corpus/upload` multipart source upload.
- Text/Markdown/HTML/PDF text-layer extraction.
- Source-file ledger with checksum and storage URI.
- Ingestion runs with extraction/chunk/index reports.
- Rights decision events.
- Source promotion gates for Z1/Z2.
- Chunk review events with revision hashes.
- Corpus dashboard metrics.
- Studio pages: Corpus, Source Review, Chunk Review.

## Non-goals

- No bundled Qwen weights.
- No automatic OCR engine dependency. Empty PDF text layers are marked `OCR_REQUIRED_TEXT_LAYER_EMPTY`.
- No bypassing copyright, robots, login walls, or paywalls.

## Recommended sequence

```text
upload source
→ extract text
→ chunk + embed
→ rights review
→ chunk review
→ approve Z1 sandbox
→ approve Z2 production only after rights + quality checks
```
