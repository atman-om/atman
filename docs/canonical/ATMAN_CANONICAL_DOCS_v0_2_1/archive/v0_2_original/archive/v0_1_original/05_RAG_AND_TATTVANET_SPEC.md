# 05 — RAG and TattvaNet Specification

## 1. RAG purpose

RAG is the source-grounding layer. It retrieves relevant corpus chunks and prevents Atman from relying only on model memory.

## 2. Retrieval pipeline

```text
question
→ normalize
→ detect language/intent
→ extract concepts
→ expand with TattvaNet
→ vector search
→ metadata filtering
→ reranking
→ source pack
```

## 3. Required metadata filters

| Filter | Examples |
|---|---|
| zone | Z2_PRODUCTION |
| rights_status | GREEN |
| language_code | hi, sa, en |
| work | Bhagavad Gita |
| chapter/verse | 2/47 |
| concept | karma |
| tradition/school | advaita, vaishnava, shaiva |
| source_type | scripture, commentary |

## 4. TattvaNet entities

```text
Text
Chapter
Verse
Concept
Deity
Sampradaya
Darshana
Commentary
Author
Ritual
Festival
Practice
Question
Misconception
```

## 5. TattvaNet relationships

```text
VERSE_EXPLAINS_CONCEPT
CONCEPT_RELATED_TO_CONCEPT
COMMENTARY_INTERPRETS_VERSE
SCHOOL_INTERPRETS_AS
TEXT_BELONGS_TO_CATEGORY
QUESTION_REQUIRES_SOURCE
MISCONCEPTION_CORRECTED_BY
```

## 6. Source pack contract

Runtime must pass source pack to generation:

```json
{
  "question": "...",
  "retrieved_chunks": [
    {
      "chunk_id": "...",
      "source_id": "...",
      "text": "...",
      "work": "Bhagavad Gita",
      "chapter": "2",
      "verse": "47",
      "score": 0.91
    }
  ]
}
```

## 7. Fallback rule

If no acceptable source pack is retrieved:

```text
Do not fabricate.
Return safe uncertainty.
Offer related source-backed explanation if available.
```
