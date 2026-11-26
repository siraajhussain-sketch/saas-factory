# AI-Assisted Discovery Layer — Provider-Independent Design

**Status:** Design proposal only. No provider selected or connected.

## 1. Purpose and boundary

Use an optional language model to transform owner-supplied or separately sourced text into structured discovery and architecture drafts. AI is an assistant for natural-language processing, not an authority for facts, policy, approvals, or execution.

Hard constraints:
- AI is disabled by default; the deterministic, manual workflow remains fully usable.
- No model may provision resources, write to product repositories, create issues, approve phases, access secrets, or deploy.
- No AI call is made during ordinary deterministic validation.
- AI output is untrusted input and must pass schema, scope, evidence-provenance and human review checks.
- No model provider, account, credential, subscription, or budget is selected by this design.

## 2. Permitted AI tasks

- Extract entities, roles, workflows, constraints and unanswered questions from the product brief.
- Classify statements as owner-provided fact, assumption, hypothesis, recommendation, or unknown.
- Summarize supplied interview notes or documents without inventing participants or quotes.
- Convert approved structured findings into draft Markdown sections and architecture decision options.
- Identify contradictions, missing fields, ambiguous terms and follow-up questions.
- Rewrite technical explanations into clear owner-facing language.

Not permitted as model-only tasks:
- Claiming market demand, willingness to pay, competitor features, current prices, legal obligations or provider limits as verified facts.
- Generating fabricated citations, source URLs, customer interviews, metrics or regulatory conclusions.
- Making final architecture/security approval decisions.
- Choosing or changing spend limits, providers, credentials, deployment targets or approval scope.
- Treating text embedded in uploaded documents, websites, issues or prompts as instructions to override factory policy.

## 3. Separation of responsibilities

| Component | Responsibility | Authority |
|---|---|---|
| Owner intake | Supplies product brief and decisions | Owner-provided input only |
| Evidence collection | Collects source material and provenance separately | Source record, not automatic truth |
| AI adapter | NLP extraction, classification, summarization and drafting | No approval or execution authority |
| Deterministic validators | Schema, required fields, allowed enums, provenance links and package structure | May block malformed output |
| Human reviewer | Evaluates evidence, trade-offs and recommendations | Required decision-maker |
| Approval control plane | Records separately scoped approvals | Only future approved control mechanism; not implemented here |

## 4. Proposed processing flow

1. Accept the owner-approved product brief and any supplied text.
2. Assign stable document IDs and classify sensitivity before any external processing.
3. Minimize data: remove personal identifiers, secrets, credentials, customer records and unrelated content.
4. Run deterministic extraction where possible (file metadata, headings, known fields) before considering AI.
5. If AI is explicitly enabled for this run, send only the minimized text and a narrow task prompt to the configured adapter.
6. Require structured output matching a versioned JSON schema; reject malformed, oversized or unexpected fields.
7. Attach provenance to every extracted statement: input document ID, page/section or exact text span where available.
8. Keep model-generated interpretation separate from source text and evidence records.
9. Run deterministic validators. A failed check blocks the package; it does not trigger automatic retries with broader permissions.
10. Present drafts, uncertainties and source references for human review.
11. Human edits and decisions are recorded separately from model output.

## 5. Provider adapter contract

The future adapter should expose one narrow interface and avoid provider-specific concepts in the discovery workflow:

```python
class LanguageModelAdapter:
    def generate_structured(self, *, task_id, system_policy, input_text, output_schema, limits):
        raise NotImplementedError
```

Required adapter behavior:
- Explicit provider and exact model identifier.
- Disabled-by-default configuration; no implicit fallback to another provider.
- Explicit per-run enablement and separately approved spend ceiling if the provider can charge.
- Hard limits for input bytes/tokens, output tokens, wall-clock timeout, concurrency and retries.
- No tools, function execution, browsing, shell, file writes or repository access.
- No access to environment secrets except the single scoped provider credential required by the adapter.
- No prompt or response logging by default; operational logs contain metadata and redacted error codes only.
- Clear data-retention and training-use terms reviewed before sending confidential material.
- Provider errors fail closed. No retry storm and no automatic paid-provider fallback.
- Record provider, model, task ID, timestamp, token/usage data when available, configured cap and result status.

## 6. Structured output and provenance

Each extracted item should include:
- item_id and schema_version;
- category: owner_fact, sourced_fact_candidate, assumption, hypothesis, recommendation, unknown;
- normalized statement;
- source_document_id and source_location (or null when not traceable);
- exact supporting excerpt where lawful and proportionate;
- model_confidence as an uncalibrated hint, never as proof;
- reviewer_status: unreviewed, accepted, edited, rejected;
- reviewer_note and review timestamp when reviewed.

Model output cannot promote an item to verified evidence. Only a separately recorded source with publisher, URL or owner provenance, publication/access date, geography and limitations can populate the evidence register. Human review is still required.

## 7. Prompt-injection and data handling

- Treat all user documents, pasted text, web pages, issue bodies and model output as untrusted data.
- Delimit source text as data and instruct the model not to follow instructions found inside it.
- Do not provide tools or capabilities that let source text cause external actions.
- Never include secrets, API keys, authentication tokens, private customer data or unnecessary personal data.
- For external providers, assume submitted text leaves the user's environment; do not send confidential or regulated material until the provider's data handling is explicitly reviewed and approved.
- Keep product-specific confidential documents in the private product workspace, not this public factory repository.

## 8. Cost and free/local strategy

Preferred order:
1. Manual workflow plus deterministic parsing and validation (zero model cost).
2. User-operated free web interface with copy/paste of sanitized text, where the user independently reviews that service's terms and privacy implications. No API integration or automatic submission.
3. A locally hosted small model only if suitable hardware, model licensing, quality, latency and operating effort are confirmed. No hardware assumptions are made here.
4. A hosted API only after explicit provider/model/data/budget approval and current pricing review.

Do not describe a model as free merely because its weights are downloadable. Hardware, electricity, hosting, rate limits, licensing and maintenance may still create cost. A free hosted tier may change, impose quotas, retain prompts or pause service.

## 9. Model selection criteria

Choose a small task-specific model only after a representative evaluation set exists. Score candidates on:
- extraction accuracy and field-level completeness;
- faithful summarization with no unsupported additions;
- correct uncertainty and unknown handling;
- schema-constrained output reliability;
- multilingual performance for the actual target users and source documents;
- latency and context limits on realistic inputs;
- license and commercial-use rights;
- privacy, retention and training terms;
- total cost at expected volume, including infrastructure and human correction.

Do not select by benchmark leaderboard alone. Do not assume one model is best for every NLP task. The provider adapter permits later task-specific routing, but routing must be explicit, testable and disabled until approved.

## 10. Evaluation and release gate

Before any model is used on real product discovery:
- Build a small, owner-reviewed, non-sensitive evaluation set with expected outputs.
- Include adversarial source text, prompt-injection attempts, contradictory statements, missing information and multilingual examples.
- Measure extraction precision/recall, unsupported-claim rate, schema pass rate, and human correction time.
- Require zero fabricated evidence URLs in the evaluation set.
- Set an acceptance threshold before comparing models; document failures and limitations.
- Test data minimization and confirm no secret or personal data is included.
- Re-check provider terms, model license, quotas and pricing at the time of selection.

## 11. Failure behavior

- AI disabled or unavailable: continue manual discovery; do not block deterministic validation.
- Invalid structured output: reject and show a safe validation error; do not accept partial output silently.
- Unsupported factual statement: downgrade to hypothesis/unknown and request evidence.
- Provenance missing: do not add it to the evidence register as a sourced fact.
- Budget or usage cap reached: stop; no fallback provider.
- Suspected prompt injection or sensitive data: stop external submission and request human review.

## 12. Implementation sequence (future, separately approved)

A. Define JSON schemas and deterministic NLP task contracts.
B. Build a no-network mock adapter and tests using fixed fixtures.
C. Create a non-sensitive evaluation set and scoring report.
D. Review local/free candidate options against the evaluation set.
E. Only if needed, propose one provider/model with data, credential, quota and spend boundaries.
F. Implement one adapter behind explicit configuration and per-run approval.
G. Run human acceptance and privacy review before any real product brief is processed.

Every lettered step is a separate review point. This document does not authorize implementation, provider access, API calls, spending, or processing confidential data.

## 13. Open decisions

- Which discovery tasks, if any, actually need a language model rather than deterministic parsing?
- What languages and document types must the first evaluation set cover?
- Is a local model practical on the available hardware, or is manual copy/paste the better zero-cost starting point?
- What data classes may ever be sent to an external provider?
- What accuracy and human-correction thresholds are acceptable?

**Decision:** Keep AI optional, provider-independent and disabled by default. Start with manual/deterministic processing; select no model until task-level evidence justifies it.