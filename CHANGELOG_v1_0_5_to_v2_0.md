# Changelog — v1.0.5 to v2.0

## Added

- Dharma Knowledge OS status/capability layer
- Parallel Model Lab with dataset planning, experiment registry, checkpoint comparison, and readiness scoring
- Source-correctness claim grading service
- Learning paths, saved answers, and lesson progress schema
- Unified Atman app navigation for Library, Learn, Model Lab, Correctness
- v2.0 docs, schemas, fixtures, and tests

## Decision changes

- Fine-tuning is now explicitly parallel, not deferred.
- Live app remains remote-Qwen-first.
- Raw scraped/quarantine data is blocked from training datasets.
- Fine-tuned Atman-Qwen cannot replace remote Qwen until release gates pass.
