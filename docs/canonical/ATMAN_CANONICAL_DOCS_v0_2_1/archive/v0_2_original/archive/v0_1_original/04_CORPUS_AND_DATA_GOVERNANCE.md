# 04 — Corpus and Data Governance

## 1. Data zone policy

| Zone | Meaning | Allowed actions |
|---|---|---|
| Z0_DISCOVERY | rough discovery/reference | metadata, summaries, topic maps |
| Z1_SANDBOX | internal experiment corpus | lab training, draft RAG, synthetic data |
| Z2_PRODUCTION | verified corpus | public RAG, production fine-tune |

## 2. Rights statuses

| Status | Meaning | Production allowed |
|---|---|---|
| GREEN | owned, licensed, public-domain, or explicitly allowed | yes |
| AMBER | uncertain | no |
| RED | blocked/high-risk | no |
| REFERENCE_ONLY | can be cited/researched but not stored for training | no |
| SYNTHETIC | teacher/user generated | only if verified and permitted |

## 3. Source record schema

Required metadata:

```json
{
  "source_id": "...",
  "title": "...",
  "source_type": "PUBLIC_DOMAIN_TEXT",
  "language_codes": ["sa", "hi"],
  "rights_status": "GREEN",
  "zone": "Z2_PRODUCTION",
  "author": null,
  "publisher": null,
  "year": null,
  "source_url": null,
  "checksum": "...",
  "declared_rights": "...",
  "created_at": "..."
}
```

## 4. Corpus chunk schema

```json
{
  "chunk_id": "...",
  "source_id": "...",
  "text": "...",
  "normalized_text": "...",
  "language_code": "hi",
  "work": "Bhagavad Gita",
  "chapter": "2",
  "verse": "47",
  "concepts": ["karma", "nishkama_karma"],
  "rights_status": "GREEN",
  "zone": "Z2_PRODUCTION"
}
```

## 5. Deduplication policy

Deduplication must run at source checksum level, exact chunk hash level, near-duplicate similarity level, and cross-source duplicate level.

Near duplicates should be reviewed, not automatically deleted, if they represent legitimate translation/commentary variants.

## 6. Quality scoring

Every chunk should receive:

- OCR confidence;
- language consistency;
- chunk completeness;
- source reference clarity;
- semantic density;
- rights readiness.

## 7. Synthetic data policy

Teacher LLM data is allowed in Z1, but must be tagged:

```json
{
  "origin": "teacher_llm_generated",
  "source_basis": ["..."],
  "requires_verification_for_production": true
}
```

Synthetic output must not be treated as scripture.
