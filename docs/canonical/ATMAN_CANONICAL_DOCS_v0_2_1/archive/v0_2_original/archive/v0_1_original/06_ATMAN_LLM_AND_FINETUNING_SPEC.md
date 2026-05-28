# 06 — Atman LLM and Fine-Tuning Specification

## 1. Model family

```text
Atman-Lab-8B
Atman-Hindi-8B
Atman-Sanskrit-8B
Atman-Acharya-14B
Atman-Scholar-32B
Atman-Guard-8B
Atman-Prod
```

## 2. Base model strategy

Initial base models should be open-weight Qwen/Llama/Mistral-class models with strong multilingual performance.

Canonical first target:

```text
Atman-Lab-8B = Qwen-class 8B + LoRA/QLoRA SFT
```

## 3. Fine-tuning purpose

Fine-tuning is for behavior, not primary knowledge.

Fine-tune for:

- Hindi explanation style;
- source-grounded answer format;
- refusal/uncertainty discipline;
- Sanskrit breakdown output format;
- sampradāya-aware framing;
- misconception correction;
- citation discipline.

Do not fine-tune for:

- storing all scripture;
- reproducing copyrighted translations;
- unsupported shloka generation;
- replacing RAG.

## 4. Dataset types

| Type | Use |
|---|---|
| SFT | correct answer examples |
| DPO | chosen/rejected preference pairs |
| Eval | benchmark and adversarial traps |
| RAG chunks | retrieval, not model training by default |

## 5. Training tiers

| Tier | Data | Threshold |
|---|---|---|
| FT_LAB | Z1/Z2 | low threshold, internal only |
| FT_STAGING | reviewed Z1 + Z2 | medium threshold, beta |
| FT_PROD | Z2 only | strict threshold, public |

## 6. Minimum sample targets

| Stage | SFT | DPO | Eval |
|---|---:|---:|---:|
| Lab | 1k–3k | 300–1k | 500 |
| Staging | 10k–25k | 2k–5k | 2k |
| Production | 50k+ | 10k+ | 5k+ |

## 7. Training output registry

Every checkpoint must record:

```json
{
  "model_name": "Atman-Lab-8B",
  "base_model": "...",
  "method": "sft_lora",
  "dataset_version": "...",
  "artifact_uri": "...",
  "metrics": {
    "faithfulness": 0.91,
    "citation_validity": 0.94
  },
  "status": "lab"
}
```
