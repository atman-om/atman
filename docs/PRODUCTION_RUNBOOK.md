# Production Runbook

## P0 unsafe output

```text
detect → disable release → preserve logs → create incident → rerun NyayaBench → patch prompt/model/corpus → release gate → redeploy
```

## P1 citation corruption

```text
freeze public answers → reindex corpus → rerun citation checks → compare source explorer → release only after pass
```

## Backup

Use `/ops/backups/simulate` for manifest shape. Replace simulation with pg_dump, qdrant snapshot, and MinIO object backup in deployment.
