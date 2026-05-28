# API examples — v0.7 Eval + Source Explorer

## Hardened eval

```bash
curl -X POST http://localhost:8000/eval/run/hardened \
  -H 'content-type: application/json' \
  -d '{"benchmark_name":"nyayabench_hardened","model_version":"Atman-Lab-Qwen-14B-v0.7"}'
```

## Citation check

```bash
curl -X POST http://localhost:8000/eval/citation/check \
  -H 'content-type: application/json' \
  -d '{"answer_text":"स्रोत: BG.2.47", "citations":[{"locator":"BG.2.47"}], "strict":true}'
```

## Fake-shloka check

```bash
curl -X POST http://localhost:8000/eval/fake-shloka/check \
  -H 'content-type: application/json' \
  -d '{"text":"धर्मो रक्षति रक्षितः ॥", "citations":[], "strict":true}'
```

## Public source search

```bash
curl 'http://localhost:8000/public/source-explorer/search?q=कर्म&limit=10'
```
