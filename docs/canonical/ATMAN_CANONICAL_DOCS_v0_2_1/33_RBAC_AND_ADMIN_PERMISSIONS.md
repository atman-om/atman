# 33 — RBAC and Admin Permissions

**Project:** Atman  **Version:** v0.2.1  **Status:** Canonical / Repo-generation-ready  **Date:** 2026-05-28  **Owner:** Atman Platform Architecture
## Purpose

This document upgrades Atman from execution-grade documentation to repo-generation-ready specification. It is binding for `ATMAN_REPO_v0_3` unless superseded by a later canonical version.

## Non-negotiable invariant

```text
Atman source authority comes from reviewed corpus + provenance + citations, not from external LLM memory or unverified scraped text.
```


## Roles

```text
viewer
student_user
content_reviewer
corpus_editor
rights_reviewer
ontology_editor
dataset_editor
ml_engineer
release_manager
security_admin
system_admin
```

## Permission matrix

| Capability | viewer | corpus_editor | rights_reviewer | ml_engineer | release_manager | admin |
|---|---:|---:|---:|---:|---:|---:|
| View sources | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Upload source |  | ✓ |  |  |  | ✓ |
| Approve rights |  |  | ✓ |  |  | ✓ |
| Edit ontology |  |  |  |  |  | ✓ |
| Build dataset |  |  |  | ✓ |  | ✓ |
| Start training |  |  |  | ✓ |  | ✓ |
| Approve release |  |  |  |  | ✓ | ✓ |
| Manage users |  |  |  |  |  | ✓ |

## Privileged actions

These actions require explicit audit reason:

```text
source promotion to Z2
rights status override
dataset sample approval for training
model release approval
release rollback
deleting user-generated content
exporting corpus data
```

## Session policy

```text
JWT access token ≤ 30 minutes
refresh token ≤ 14 days
admin sessions re-authenticate for privileged actions
all admin actions require request_id + actor_id
```

## Object-level access

Atman Studio resources are governed by role + state:

```text
rights_reviewer can approve only RIGHTS_REVIEW_PENDING sources
ml_engineer can create training runs only from APPROVED_FOR_TRAINING datasets
release_manager can approve only gates with zero hard failures
```

## Acceptance criteria

```text
✓ no unauthenticated write endpoint
✓ RBAC checked before service execution
✓ all privileged actions audit logged
✓ security_admin can revoke active sessions
✓ object state is checked with role
```
