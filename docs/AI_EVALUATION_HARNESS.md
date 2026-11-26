# NLP Evaluation Dataset and Scoring Harness

**Status:** Local, read-only evaluation tooling. No model is selected or connected.

## Purpose

Before comparing free, local or hosted NLP models, evaluate them against the same small, human-authored examples. The starter dataset covers:
- extracting explicit owner-provided facts;
- keeping an unvalidated pricing idea as a hypothesis;
- preserving uncertainty when evidence is absent;
- treating prompt-injection text inside a product brief as untrusted source data.

The examples are synthetic and contain no customer or confidential data.

## Scoring

The harness reports:
- schema validity (via the strict output contract);
- expected findings matched, missing findings and extra findings;
- category accuracy;
- exact source-document and excerpt provenance accuracy;
- required-phrase coverage as a simple lexical proxy.

Invalid outputs receive zero scores for the case and include a validation error.

## Run locally

```sh
python -m unittest discover -s tests -v
python -m control_plane.ai_evaluation --dataset examples/evaluation/nlp-evaluation-v1.json --outputs path/to/candidate-outputs.json
```

The candidate output file is a JSON object mapping each `case_id` to a response object that follows the AI output contract. The harness reads the files and prints a report; it does not write files, call the network, invoke a provider or change a repository.

## Interpretation limits

This is a starter smoke-test set, not a statistically representative benchmark. Phrase coverage is not semantic understanding. Exact excerpt matching does not prove faithful interpretation. Scores do not verify factual truth, source quality, safety, multilingual performance, latency, privacy, licensing or confidence calibration.

Before any model comparison, expand the dataset with reviewed examples in the intended languages and domains, include difficult negatives and paraphrases, freeze a versioned test split, and define acceptable error thresholds with a human reviewer. Never use this score alone to approve a model or product release.
