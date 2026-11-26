# Independent Security Audit — Control Plane

**Audit date:** 2026-11-26  
**Repository:** `siraajhussain-sketch/saas-factory`  
**Audited baseline:** `d33c392c128c8855a500b52e1442989bbbe83d55`  
**Scope:** Read-only review of the control-plane implementation, tests, CI workflow and relevant governance/security documentation.

## Executive decision

**Decision: remain read-only; do not implement an executor or connect product repositories yet.**

The reviewed repository is currently a governance and validation prototype. The reviewed CI workflow runs tests with read-only repository permissions. The audited tree contains no implementation worker, deployment worker, product-repository writer, provisioning integration, authenticated approval issuer or durable approval ledger. No direct capability to deploy or modify a product was identified in the audited baseline.

That limited capability is a meaningful safety boundary, but it must not be confused with a production-ready authorization system. The current approval prototype has critical authorization gaps. These are release blockers for any future execution automation.

## Findings and severity

### SEC-01 — Critical: approver identity is not authenticated

The approval record's approver field is descriptive data, not proof of identity. The prototype uses a shared HMAC secret; anyone who obtains that secret can create valid signatures and claim any approver name. The verifier cannot establish that the named person actually approved the operation.

**Required before execution:** authenticated owner identity, a protected signing boundary, key identity/rotation and a verifiable signature contract. Prefer asymmetric signing with the private key held outside the repository and public verification keys available to the verifier.

### SEC-02 — Critical: no durable replay protection, independent revocation or atomic claim

The prototype has no durable approval ledger or atomic one-time claim. A valid approval can be verified repeatedly. Its revoked flag is part of the signed payload, so it is not an independent, live revocation mechanism.

**Required before execution:** durable transactional approval records; atomic claim; independently recorded revocation; unique approval ID and nonce; explicit states such as ISSUED, REVOKED, CLAIMED, SUCCEEDED, FAILED and EXPIRED. Fail closed when the ledger is unavailable.

### SEC-03 — High: approval is not bound to an immutable source revision and complete phase plan

The current approval binds several useful scope fields, including product, repository, branch, phase, path set and ADR digest, but does not bind an immutable repository commit identity and exact phase-plan digest. A branch name can move, and a plan can change without the approval representing the exact source and plan being executed.

**Status: partially implemented as a read-only v2 prototype; independent re-audit pending.** The v2 validator now binds a declared full commit SHA, canonical phase-plan digest, ADR digest, exact path set, operation class and registry version, actions, environment, provider policy and zero-spend ceiling. The phase plan is hashed using a restricted RFC 8785-compatible canonical JSON profile (safe-range integers only; floats rejected). Negative tampering tests and canonicalization tests are included. GitHub Actions run [45821136897](https://github.com/siraajhussain-sketch/saas-factory/actions/runs/45821136897) passed 138 tests.

The local validator does **not** verify that the actual checkout HEAD equals the declared commit; it reports `DECLARED_ONLY_NOT_CHECKED_OUT`. A trusted checkout verifier remains required. HMAC remains a shared-secret prototype, and SEC-01/SEC-02/SEC-04 remain open. This finding is not closed and the prototype is not executable authorization.

**Required before execution:** independently review the v2 schema and canonicalization; implement a separately trusted checkout-revision verifier; bind a protected policy version; and resolve the authenticated identity, signing, replay and atomic-claim gaps.

### SEC-04 — High: trusted policy configuration boundary is undefined

The local policy file is not protected by a separate trusted configuration boundary. If a future worker reads policy from an editable or attacker-controlled checkout, a repository change could weaken the policy that is supposed to constrain that same repository.

**Required before execution:** define where policy is stored, who can change it, how its integrity is verified, and how policy versions are pinned to an operation. Do not trust policy loaded from the untrusted worktree being authorized.

### SEC-05 — High: lifecycle and review records are editable claims, not authenticated audit evidence

Lifecycle history, reviewer labels, finding statuses and resolution notes are not authenticated. Hashes can establish that artifact bytes match a manifest's recorded digest; they do not prove who authored a review, that a human performed it, or that a claimed remediation is true.

**Required before execution:** distinguish machine-verified facts from unverified claims; authenticate reviewers and owners; preserve append-only audit events with integrity protection; require independent evidence for closure of security-critical findings. Do not treat a lifecycle state or review status as authorization.

### SEC-06 — High: potential time-of-check/time-of-use gap in case consistency validation

**Status: remediated in the follow-up change; independent re-audit still pending.** At the audited baseline, the manifest validation path hashed artifact bytes, while the case-consistency checker subsequently reopened artifact files for content validation. A concurrent local modification could therefore have caused different bytes to be hashed and structurally checked.

The follow-up implementation now captures each declared artifact once as bytes, verifies the SHA-256 digest against that snapshot, and passes the same snapshot bytes to downstream structural validators. A regression test mutates the on-disk brief after snapshot capture but before manifest validation; the checker confirms that it uses the original hash-matched snapshot. GitHub Actions run [45780074842](https://github.com/siraajhussain-sketch/saas-factory/actions/runs/45780074842) passed all 103 tests.

This closes the identified double-read gap in the current local checker design. It is not a formal proof against a fully privileged local attacker, and it has not yet received a separate independent re-audit.

### SEC-07 — Medium: schema strictness and chronology validation are incomplete

**Status: remediated in the follow-up change; independent re-audit still pending.** At the audited baseline, some lifecycle/review records accepted unknown fields and timestamp/history chronology was not fully constrained.

The follow-up now rejects unknown or missing fields at lifecycle manifest, artifact, validator-run, human-review, state-history, review-record, reviewed-artifact and finding levels. Lifecycle timestamps must be timezone-aware; `updated_at` cannot precede `created_at`; validator and review events must fall within the case interval; state-history events must be nondecreasing. Review records must not predate their linked product case, and target dates use a strict `YYYY-MM-DD` format. Negative tests cover these conditions. GitHub Actions run [45780592803](https://github.com/siraajhussain-sketch/saas-factory/actions/runs/45780592803) passed all 113 tests.

This is strict validation for the current versioned local file contracts, not authenticated evidence or an independent certification. It has not yet received a separate independent re-audit.

### SEC-08 — Medium: AI provenance is not semantic correctness

The AI output contract's exact excerpt/source-span checks establish that cited text occurs in a source document. They do not establish that the model's interpretation, categorization, omission or conclusion is correct. This limitation is documented and must remain explicit.

**Required controls:** human review for consequential findings, evidence-quality assessment, uncertainty/contradiction handling, language-specific evaluation and no automatic promotion of model output to verified fact or approval.

## Existing safeguards observed

- No executor, product-repository writer, deployment or provisioning worker was present in the audited tree.
- CI workflow permissions are read-only for repository contents.
- Third-party workflow actions are pinned to immutable revisions.
- The validators are designed as local/read-only tools and require explicit dry-run operation.
- Strict JSON parsing, duplicate-key handling, path confinement and symlink checks are present in relevant validation paths.
- Provider use, spending and environment access remain disabled by default.
- Human review is documented as separate from owner authorization.

These safeguards reduce current exposure, but they do not close the authorization gaps above.

## Remediation order

1. **SEC-06 — completed, pending independent re-audit:** snapshot each artifact once; hash and validate the same bytes; regression coverage passes.
2. **SEC-07 — completed, pending independent re-audit:** strict versioned schemas and chronology checks are implemented and tested.
3. **SEC-03 partially implemented; independent re-audit pending:** v2 manifest/approval validation binds declared commit SHA, canonical phase-plan digest, operation class/registry version, exact actions and paths. CI run [45821136897](https://github.com/siraajhussain-sketch/saas-factory/actions/runs/45821136897) passed 138 tests. Actual checkout identity remains unverified; HMAC identity and replay/ledger gaps remain. See [SEC-03 Approval Scope Binding Contract](SEC_03_APPROVAL_SCOPE_BINDING.md).
4. **Define trusted policy boundary (SEC-04):** policy integrity, ownership, versioning and pinning.
5. **Design authenticated identity and signing (SEC-01):** protected asymmetric signing and key lifecycle.
6. **Design durable approval lifecycle (SEC-02):** atomic one-time claims, independent revocation, replay prevention and recovery.
7. **Improve audit evidence (SEC-05) and AI review boundaries (SEC-08).**
8. Only after independent review of the above should a narrowly scoped executor be reconsidered. Execution, paid services, credentials, production data, deployment and release each require separate owner approval.

## Explicit non-authorization

This audit is a preliminary technical review of the named repository baseline, not a formal penetration test, cryptographic certification, legal review or guarantee of security. It does not authorize implementation, spending, credentials, provisioning, production data access, deployment, DNS changes or public launch.

The synthetic Workshop Queue case and its review tracker remain illustrative. Their content and statuses are not real market evidence, authenticated human review or owner authorization.

## Audit outcome

**Current state:** suitable for continued read-only prototype development and bounded remediation.  
**Not suitable for:** automated code execution, product-repository mutation, paid-provider calls, resource provisioning or release automation.  
**Next recommended work:** implement SEC-03's versioned contract and negative tests only after the design is reviewed; independently re-audit the completed SEC-06/SEC-07 remediations. Keep the factory read-only throughout.
