# Corpus Upload Fixture

Use with:

```bash
curl -X POST http://localhost:8000/corpus/upload \
  -F "title=Bhagavad Gita Demo" \
  -F "language=sa" \
  -F "rights_status=PUBLIC_DOMAIN_VERIFIED" \
  -F "locator=BG.2.47" \
  -F "file=@fixtures/corpus_sample_gita.txt"
```
