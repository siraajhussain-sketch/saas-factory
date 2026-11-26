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

## Phase 2E — Read-only lifecycle manifest
- Versioned JSON case record linking artifacts, validator-run records, human review notes and lifecycle history.
- Root-confined artifact paths and SHA-256 integrity checks.
- Strict identifiers, references, timestamps and permitted state sequence.
- Human decisions remain unauthenticated records; lifecycle state never grants authority.
- Standard-library tests and mandatory dry-run CLI.
- No database, network, provider, executor, product repository writes or spending.

## Phase 2F — Human review checklist (documented)
- Added [Human Review Checklist](HUMAN_REVIEW_CHECKLIST.md) for discovery, evidence quality, architecture, cost/dependencies, security/privacy and next-phase boundaries.
- Includes review record fields, explicit outcomes, reviewer notes, stop conditions and decision definitions.
- Separates a completed human review from owner authorization to implement, spend, provision, use credentials or deploy.
- The checklist is guidance only; it does not authenticate reviewers, certify security or create machine-enforceable approval.

## Phase 2G — Read-only product case consistency checker
- Require exactly one Product Brief, discovery report, architecture package and evidence register in a single lifecycle manifest.
- Verify manifest artifact hashes and root-confined paths.
- Rerun existing brief and Phase 2 structural validators against current artifact bytes.
- Treat recorded validator runs, reviewer labels and lifecycle states as unauthenticated historical data.
- Report human-review readiness only; never grant implementation or release authority.
- Standard-library tests and mandatory dry-run CLI; no network, providers, writes or spending.

## Phase 2H — Read-only review findings and remediation tracker
- Versioned review record tied to one case and exact hashes of its four core artifacts.
- Structured findings with category, severity, status, owner label, next action and optional target date.
- Resolution notes required for claimed-resolved findings and accepted risks; these remain unverified claims.
- Deterministic local validator reruns the case consistency checks and verifies reviewed artifact references.
- Assistant-generated assessments remain explicitly distinct from human reviews.
- No authenticated assignments, notifications, workflow transitions, writes, network calls, providers, spending or authorization.

## Phase 2I — Independent security audit and bounded remediation (current gate)

The read-only audit is recorded in [Independent Security Audit — Control Plane](INDEPENDENT_SECURITY_AUDIT_2026-11-26.md). The audit found critical approval-identity and replay/revocation gaps, plus high-severity scope, trusted-policy, audit-evidence and artifact snapshot concerns.

**Required before any executor is reconsidered:**
1. **Completed — SEC-06 artifact snapshot consistency:** the case checker now reads each declared artifact once, hashes the captured bytes and uses those same bytes for structural validation. A regression test mutates the on-disk file between snapshot capture and manifest validation and confirms the original snapshot is consistently used. GitHub Actions passed 103 tests in run [45780074842](https://github.com/siraajhussain-sketch/saas-factory/actions/runs/45780074842).
2. **Completed — SEC-07 schema and chronology hardening:** lifecycle and review records now reject unknown/missing fields, enforce strict timestamp windows and validate nondecreasing state-history chronology. Review records cannot predate their linked product case. New negative tests cover these boundaries; GitHub Actions passed 113 tests in run [45780592803](https://github.com/siraajhussain-sketch/saas-factory/actions/runs/45780592803). Independent re-audit remains pending.
3. **SEC-03 v2 prototype implemented; independent re-audit pending:** binds declared full commit SHA, canonical phase-plan digest, operation-class registry version, exact action/path scope and HMAC signature. GitHub Actions run [45821430788](https://github.com/siraajhussain-sketch/saas-factory/actions/runs/45821430788) passed 142 tests. The actual checkout HEAD remains unverified; the HMAC issuer identity and replay/ledger gaps remain open. See [SEC-03 Approval Scope Binding Contract](SEC_03_APPROVAL_SCOPE_BINDING.md).
4. Define a trusted, integrity-protected policy configuration boundary and trusted checkout-revision verifier.
5. Design authenticated owner identity and protected asymmetric signing.
6. Design durable approval records, atomic one-time claims, independent revocation and replay prevention.
7. Preserve the distinction between verified evidence, human decisions and AI-generated suggestions.

**Exit condition:** all required remediations are implemented and tested, then independently reviewed. SEC-06 and SEC-07 are implemented with regression coverage but have not yet received a separate independent re-audit. Passing tests or a structurally valid review record do not themselves authorize execution.

**Current restriction:** remain read-only. No executor, product-repository writes, paid providers, credentials, production data, provisioning, deployment or release automation.

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
- **Blocked until Phase 2I exit conditions are independently satisfied and separately approved.**

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
