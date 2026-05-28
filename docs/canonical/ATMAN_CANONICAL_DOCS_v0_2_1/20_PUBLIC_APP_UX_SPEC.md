---
project: Atman
pack: ATMAN_CANONICAL_DOCS_v0_2
version: 0.2
status: execution-grade canonical baseline
created_at: 2026-05-28T13:00:36+05:30
timezone: Asia/Kolkata
canonical_rule: Any implementation, repo, model, dataset, or release gate must conform to this document pack or record an ADR.
---

# 20 — Public App UX Specification

## 1. Objective

The public Atman app must make source-backed Dharma learning simple, Hindi-first, and trustworthy.

## 2. Public screens

```text
Home
Ask Atman
Shloka Explainer
Source Explorer
Scholar Mode
Citation View
Feedback Report
About Sources
Safety/Limitations
```

## 3. Ask Atman flow

```text
question input
→ answer mode selection
→ retrieval + answer generation
→ answer display
→ citation expansion
→ related concepts
→ feedback
```

## 4. Answer display structure

```text
सीधा उत्तर
स्रोत आधार
सरल व्याख्या
परम्परा-भेद, यदि लागू हो
संबंधित अवधारणाएँ
सीमा/अनिश्चितता
```

## 5. Shloka Explainer flow

```text
input shloka/reference
→ source match
→ exact text display
→ word meaning
→ simple Hindi explanation
→ commentary comparison when available
→ citation
```

## 6. Source Explorer

Must support:

```text
browse by text
browse by chapter/verse
search by concept
filter by tradition/commentary
view source locator
copy citation
```

## 7. Scholar Mode

Scholar Mode may include:

- deeper citations;
- cross-commentary comparison;
- Sanskrit transliteration;
- ontology graph links;
- uncertainty/range of interpretations.

## 8. Public limitations copy

Atman should state:

```text
Atman स्रोत-आधारित अध्ययन सहायता है। यह गुरु, आचार्य, पुरोहित, डॉक्टर, वकील या अंतिम धार्मिक प्राधिकारी का विकल्प नहीं है।
```

## 9. Feedback categories

```text
wrong citation
unclear answer
missing tradition
unsafe/problematic
hallucinated shloka
translation issue
other
```

## 10. Trust cues

- visible citations;
- “source not found” transparency;
- no fake shlokas;
- versioned source notes;
- report button on every answer.
