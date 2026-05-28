# Deployment v1.0.5

## Local Product Run

```bash
cp .env.example .env
# edit ATMAN_QWEN_BASE_URL and ATMAN_QWEN_API_KEY
docker compose up --build
```

## Apps

```text
Atman App:  http://localhost:3002
Studio:     http://localhost:3000
Public App: http://localhost:3001
API:        http://localhost:8000/docs
```

## Production Requirements

- Remote Qwen API key vault/secrets manager.
- Managed Postgres.
- Managed object storage.
- HTTPS domain.
- Real auth provider.
- Daily backup and restore test.
- Rate limits and model usage alarms.
