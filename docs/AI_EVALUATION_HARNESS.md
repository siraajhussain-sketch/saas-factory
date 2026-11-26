# NLP Evaluation Dataset and Scoring Harness

**Status:** Local, read-only evaluation tooling. No model is selected or connected.

## Language coverage

The version 1.1 starter dataset evaluates:
- English (`en`);
- Arabic (`ar`), including Modern Standard Arabic and one synthetic Gulf/Emirati-style colloquial example;
- Urdu (`ur`);
- mixed-language input (`mixed`), including Arabic–English and Urdu–English code-switching.

For UAE-focused products, Arabic and English are priority launch languages. Urdu remains included for Pakistan-facing workflows and mixed-language customer input. This is a test priority, not a commitment that every product must launch with every language.

## Purpose and scenarios

Before comparing free, local or hosted NLP models, evaluate them against the same small, human-authored examples. Cases cover explicit owner facts, uncertain pricing, missing customer research, prompt-injection text, UAE-related Arabic input, Urdu input and code-switched input. All examples are synthetic and contain no customer or confidential data.

## Scoring

The harness reports:
- schema validity;
- expected findings matched, missing findings and extra findings;
- category accuracy;
- exact source-document and excerpt provenance accuracy;
- required-phrase coverage as a simple lexical proxy;
- a separate summary by language.

Invalid outputs receive zero scores for the case and include a validation error.

## Run locally

```sh
python -m unittest discover -s tests -v
python -m control_plane.ai_evaluation --dataset examples/evaluation/nlp-evaluation-v1.1.json --outputs path/to/candidate-outputs.json
```

The candidate output file is a JSON object mapping each `case_id` to a response object that follows the AI output contract. The harness reads the files and prints a report; it does not write files, call the network, invoke a provider or change a repository.

## Limitations and next evaluation work

This is a starter smoke-test set, not a statistically representative benchmark. One colloquial Arabic example is not enough to represent UAE dialects; expand with reviewed Emirati/Gulf, MSA, and relevant regional variants. Add Arabic diacritic, spelling and morphology variants, longer documents, formal business/legal phrasing, right-to-left layout edge cases, and realistic code-switching. Expand Urdu regional phrasing as well.

Phrase coverage is not semantic understanding. Exact excerpt matching does not prove faithful interpretation. Scores do not verify factual truth, source quality, safety, latency, privacy, licensing or confidence calibration. Human review by fluent Arabic and Urdu speakers remains mandatory. Before model selection, create a larger reviewed dataset, define separate language-specific acceptance thresholds, and compare error rates per language rather than relying on one blended score.
