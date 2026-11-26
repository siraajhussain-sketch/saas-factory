# Implementation Roadmap

This roadmap is a proposal. Completing a phase requires review and explicit approval before the next phase begins.

## Phase 0 — Governance baseline
- Product-agnostic engineering and security rules.
- Approval gates and cost policy.
- Architecture and orchestrator design.
- Public-repository hygiene.

## Phase 1 — Deterministic control plane
- Strict product and approval schemas.
- Repository, branch, phase and path allowlists.
- Zero-provider and zero-spend enforcement.
- ADR integrity verification.
- Approval expiry and revocation validation.
- Unit tests and CI.
- No executor or external side effects.

## Phase 2D — Product brief intake validation
- Deterministic local validation of the Product Brief template.
- Required section and unfinished-template checks.
- Blank labeled fields blocked; explicit `UNKNOWN` remains acceptable.
- Read-only CLI with mandatory dry-run and standard-library tests.
- Passing status means ready for human discovery review only; no implementation authority.
- No network, model, provider, credentials, product repository writes or spending.

## Phase 2 — Read-only discovery and architecture package
- Structured intake and evidence register.
- Evidence-backed discovery report with facts separated from assumptions.
- Product-specific architecture and threat-model draft.
- Data/privacy, localization, operations and test strategy.
- Dependency and cost analysis, including free-tier limitations.
- Bounded implementation-phase proposal and explicit owner decision.
- No product repository writes, provider calls, provisioning or deployment.

## Phase 2A — Optional AI-assisted discovery design
- Provider-independent NLP adapter contract.
- Strict separation of model drafts, evidence and human decisions.
- Data minimization, prompt-injection and failure controls.
- Evaluation criteria and zero-cost-first options.
- No provider selected, credentials, calls or spending.

## Phase 2B — Structured output contract and mock adapter
- Strict, versioned JSON output contract with bounded fields and categories.
- Exact source-document and excerpt provenance checks.
- Model output cannot self-approve or create verified evidence.
- Deterministic fixed-fixture adapter; no network or model inference.
- Adversarial, malformed, oversized and provenance-failure tests.
- No provider selected, credentials, external prompt submission, spending or product repository writes.

## Phase 2C — NLP evaluation baseline
- Small, synthetic, versioned evaluation dataset.
- Read-only scoring for schema validity, missing/extra findings, category accuracy, provenance and lexical coverage.
- Document benchmark limitations and human-review requirements.
- No model invocation, provider credentials, network access or product repository writes.

## Phase 2F — Human review checklist
- Structured human review for discovery, evidence quality, architecture, cost/dependencies and security/privacy.
- Explicit PASS / FAIL / N/A outcomes, reviewer notes and bounded next-phase decision.
- Clear separation between review completion and authorization to implement, spend or deploy.
- Review checklist is guidance, not certification or machine-enforceable approval.

## Phase 2E — Read-only lifecycle manifest
- Versioned JSON case record linking artifacts, validator-run records, human review notes and lifecycle history.
- Root-confined artifact paths and SHA-256 integrity checks.
- Strict identifiers, references, timestamps and permitted state sequence.
- Human decisions remain unauthenticated records; lifecycle state never grants authority.
- Standard-library tests and mandatory dry-run CLI.
- No database, network, provider, executor, product repository writes or spending.

## Deferred — Expanded multilingual benchmark (before model selection)

This is intentionally backlog work, not a current implementation phase. The version 1.1 synthetic dataset is only a smoke-test baseline and must not be used to claim production-grade Arabic or Urdu quality.

- Expand UAE-focused Arabic coverage with reviewed Modern Standard Arabic, Gulf/Emirati-style phrasing and formal business-document language.
- Add realistic but synthetic UAE business scenarios, longer passages, spelling/morphology variants, diacritics, right-to-left layout cases and Arabic–English code-switching.
- Expand Urdu phrasing and Urdu–English code-switching for Pakistan-facing workflows.
- Have fluent Arabic and Urdu reviewers validate expected findings, terminology and acceptable interpretations; record disagreements and uncertainty.
- Define separate minimum acceptance thresholds for Arabic, English and Urdu, plus mixed-language cases; do not hide weak per-language performance behind an aggregate score.
- Only after this dataset and review process are ready, benchmark candidate small/free/local models for quality, privacy, licensing, hardware requirements, latency and total operating cost. Do not connect a model or send product/customer documents without a separate approval.

**Exit condition:** a versioned, human-reviewed dataset and documented per-language acceptance criteria exist. Until then, model selection and integration remain deferred.

## Phase 3 — Isolated product repository setup
- Explicit repository and visibility approval.
- Approved starter and baseline security controls.
- Product-specific configuration and CI.
- No production credentials or data.

## Phase 4 — Controlled implementation worker
- One approved phase at a time.
- Strict branch/path scope.
- Provider disabled unless separately approved.
- Bounded retries and execution time.
- Pull request and human review.

## Phase 5 — Validation and operational maturity
- Security and tenant-isolation tests.
- Migration, backup and restore checks.
- Privacy and retention verification.
- Observability, incident response and support readiness.
- Independent human acceptance.

## Phase 6 — Optional release automation
- Only after production readiness review.
- Separate approval for credentials, billing, deployment, DNS and public launch.
- Rollback plan and accountable owner.
- No default automatic release.

## Non-goals

The roadmap does not promise autonomous software delivery, production readiness, guaranteed security or zero-cost operation. Any such capability must be demonstrated and independently reviewed before use.
