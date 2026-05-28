# v0.8 — Web-to-Corpus and OCR Pipeline

## Objective

Acquire allowed web/PDF/image sources without contaminating Atman with unreviewed or rights-unsafe data.

## Pipeline

```text
URL/register → robots check → rights gate → fetch/extract → quality score → provenance event → review queue → corpus promotion
```

## OCR modes

```text
deterministic = classify and extract plain text only
tesseract     = future local OCR worker
paddle        = future multilingual OCR worker
external      = future managed OCR API
```

## Hard gate

No crawled or OCR-derived text becomes Z2 until rights + quality + source review pass.
