# AI Discovery Output Contract and Mock Adapter

**Status:** Local prototype only. No model provider or execution worker is connected.

## Scope

This phase defines a strict JSON contract and a deterministic mock adapter for testing the future natural-language-processing boundary. It does not call a model, browse, access a repository, write product data, verify factual claims, or authorize human decisions.

## Finding contract

Every response has exactly:
- `schema_version`: currently `1.0`.
- `findings`: 1–100 extracted findings.

Each finding has exactly:
- `item_id`: stable-format identifier unique within the response.
- `category`: `owner_fact`, `sourced_fact_candidate`, `assumption`, `hypothesis`, `recommendation`, or `unknown`.
- `statement`: concise normalized statement.
- `source_document_id`, `source_location`, `supporting_excerpt`: provenance fields. A source excerpt must be an exact substring of the supplied source document.
- `model_confidence`: optional numeric hint from 0 to 1; it is not calibrated evidence.
- `reviewer_status`: must remain `unreviewed` in model output.
- `reviewer_note`, `reviewed_at`: must remain null; only a separate human review process may populate them.

Owner facts and sourced-fact candidates require source document provenance. A structurally valid sourced candidate is not a verified fact and cannot automatically enter the evidence register.

## Deterministic validation

The standard-library validator rejects duplicate JSON keys, non-finite numbers, unknown fields and categories, malformed IDs, duplicate finding IDs, missing or unknown source references, excerpts that do not exactly occur in the supplied source, self-approved review metadata, invalid confidence values, and oversized payloads/fields/lists.

Validation confirms structure and traceability only. It does not confirm that the statement correctly interprets the excerpt, that the source is reliable, or that a claim is true. Human review remains mandatory.

## Mock adapter

`MockLanguageModelAdapter` mirrors the proposed adapter method but returns a fixed fixture. It performs no network access, model inference, filesystem access, subprocess execution, or external action. Its input text is treated as data and is not interpreted as instructions.

## Run tests locally

```sh
python -m unittest tests.test_ai_output_contract -v
```

The repository CI also runs the full standard-library test suite on Python 3.12.

## Explicit exclusions

No hosted or local model is selected; no API key, account, paid API, external prompt submission, confidential data, product repository, approval service, executor, deployment or production environment is involved.
