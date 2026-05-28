# Atman v1.0 Status

## Included

- Public app and Atman Studio
- FastAPI backend with Docker Compose
- Corpus upload/review/promote lifecycle
- Web-to-corpus crawler governance
- OCR analysis and OCR-required detection
- Qwen runtime facade with deterministic fallback and OpenAI-compatible server mode
- Content factory with review and export
- NyayaBench hardened evals and source explorer
- Qwen training dataset builder and simulated LoRA/QLoRA ModelOps flow
- Model checkpoint/release gates
- Production readiness, backup simulation, incident ledger
- Migrations 0001–0007

## Not bundled

- Qwen model weights
- Production-reviewed Dharma corpus
- Real OCR engine binaries
- Real GPU training execution by default

## Release posture

`v1.0` is a production release candidate scaffold. Real production deployment requires reviewed corpus, secrets rotation, auth enablement, real Qwen endpoint, and operational monitoring.
