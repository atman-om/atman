---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 30 — Operations Runbook

## 1. Objective

Define operational handling for incidents, deployments, rollback, source revocation, eval failures, and runtime quality issues.

## 2. Incident severity

| Severity | Meaning | Examples |
|---|---|---|
| P0 | immediate user/system harm | unsafe output, severe data leak |
| P1 | trust/citation/release integrity issue | fake shloka in production, citation corruption |
| P2 | degraded capability | retrieval failure spike, latency breach |
| P3 | non-critical instability | UI bug, delayed queue |

## 3. Unsafe output procedure

```text
detect
→ preserve logs/source pack/answer
→ flag session
→ open incident
→ disable affected artifact if severe
→ rollback if needed
→ rerun NyayaBench
→ patch root cause
→ release through gate
→ postmortem
```

## 4. Citation corruption procedure

```text
freeze current RAG index alias
compare answer citations against chunk snapshot
rollback to previous approved index if corruption confirmed
open RAG_INDEX release block
rebuild candidate index
rerun retrieval/citation evals
```

## 5. Rights revocation procedure

```text
mark source revoked
remove source chunks from retrieval
identify dependent datasets/checkpoints
block future training use
notify release manager
run dependency impact report
```

## 6. Bad model release rollback

```text
identify production alias
switch alias to previous approved checkpoint
clear inference cache
run smoke tests
monitor error/feedback metrics
open regression investigation
```

## 7. Deployment checklist

```text
migrations applied
health checks green
eval smoke passed
release gate approved
artifact manifest stored
rollback target confirmed
dashboards checked
```

## 8. Postmortem template

```text
incident id
severity
start time
end time
impact
trigger
root cause
what detected it
what failed
fix
prevention
owner
due date
```

## 9. Weekly operations review

Review:

```text
negative feedback clusters
citation failures
retrieval misses
rights queue
open incidents
cost trend
latency trend
pending release gates
```

## 10. Production freeze rule

If P0 or unresolved P1 is active, production release gates remain frozen except for rollback or emergency fix releases.
