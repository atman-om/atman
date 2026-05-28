# Railway Backend Deploy

Railway should deploy the Atman API from the repo root using `railway.json`.

## Service

- GitHub repo: `atman-om/atman`
- Branch: `main`
- Config file path: `/railway.json`
- Builder: Dockerfile
- Dockerfile path: `services/api/Dockerfile`
- Healthcheck: `/health`

## Required variables

Set these in the Railway API service:

```text
ATMAN_ENV=production
ATMAN_PRODUCTION_REQUIRE_AUTH=true
ATMAN_DATABASE_URL=<Neon or Railway Postgres URL>
ATMAN_QWEN_BASE_URL=<Qwen OpenAI-compatible base URL>
ATMAN_QWEN_API_KEY=<Qwen API key>
```

Use the exact variable names already present in `.env.example`. A standard Neon pooled URL like `postgresql://...-pooler.../neondb?sslmode=require&channel_binding=require` is accepted for `ATMAN_DATABASE_URL`; the API converts it to the async SQLAlchemy driver format at runtime.

`ATMAN_SYNC_DATABASE_URL` is optional for Railway. If it is not set, migrations derive the sync driver URL from `ATMAN_DATABASE_URL`.

## If Railway does not auto-deploy

Check these in the Railway service settings:

1. Source repo is `atman-om/atman`, not the old `mail2piyushbatra/atman`.
2. Branch is `main`.
3. Config as Code path is `/railway.json`.
4. Root directory is empty or `/`, because the Dockerfile uses the repo root as build context.
5. GitHub auto-deploys are enabled.

The API container binds to Railway's injected `PORT`, with local fallback to `8000`.

Railway runs `alembic upgrade head` before starting the API, so the Neon schema is migrated during deployment.
