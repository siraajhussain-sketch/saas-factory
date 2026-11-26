# SEC-03 — Approval Scope Binding Contract

**Status:** Design contract drafted; implementation and tests are pending. This document does not change the current validator or authorize execution.

## 1. Security objective

A future approval must describe one exact, immutable, bounded operation. A branch name, product label, issue description or mutable plan file is not sufficient identity. Any change to the source revision, phase plan, operation class, target branch, permitted paths or other signed constraint must invalidate the approval.

This contract addresses SEC-03 only. It does not solve authenticated approver identity (SEC-01), replay/revocation/atomic claim (SEC-02), trusted policy integrity (SEC-04), or authenticated audit evidence (SEC-05).

## 2. Versioned request and approval fields

The next approval-contract version must require the following fields in both the validated request scope and the signed approval payload. Names below are normative.

| Field | Required meaning |
|---|---|
| `schema_version` | New, explicit approval contract version; do not silently reinterpret v1 records |
| `product_id` | Stable product identifier |
| `repository` | Exact GitHub owner/name identity, not a display name or URL supplied by an agent |
| `repository_commit_sha` | Full 40-character lowercase Git commit SHA identifying the immutable source revision |
| `target_branch` | Exact intended branch; contextual destination only, never a substitute for the commit SHA |
| `adr_path` / `adr_sha256` | Confined ADR path and digest, checked against the pinned repository snapshot |
| `phase_id` | Stable phase identifier |
| `phase_plan_path` | Confined path to the versioned machine-readable phase plan in the pinned revision |
| `phase_plan_schema_version` | Exact phase-plan schema version |
| `phase_plan_sha256` | SHA-256 of the canonical phase-plan representation |
| `operation_class` | One value from the closed, versioned operation-class registry |
| `allowed_actions` | Exact action set permitted within that operation class |
| `permitted_paths` | Exact normalized path set; no wildcard expansion at execution time |
| `environment` | Exact environment; defaults to `none` |
| `provider_allowlist` | Exact provider set; defaults to empty |
| `max_spend` / `currency` | Explicit ceiling and currency; defaults to zero |
| `issued_at` / `not_before` / `expires_at` | Signed validity interval |
| `approval_id` / `nonce` | Unique identifiers; uniqueness and one-time use require SEC-02 ledger controls |
| `approver_identity` / `key_id` | Reserved for authenticated identity and protected signing design under SEC-01 |

The signature must cover every field above and every other authorization-relevant field. Unknown fields must be rejected. Missing fields must be rejected. A v1 approval must never be upgraded by inference or default values.

## 3. Immutable revision rules

1. Require a full commit SHA; reject branch-only, tag-only, abbreviated, malformed or mutable references.
2. The request and approval must contain the same repository owner/name and exact commit SHA.
3. The ADR and phase-plan artifacts must be resolved from that same pinned revision and their content digests verified.
4. The target branch must be separately signed and must match the approved destination policy. A branch moving after approval must not change the approved source revision.
5. A future executor must verify the actual checkout HEAD equals the signed commit SHA immediately before acting. It must fail closed on mismatch, shallow/ambiguous checkout state, unavailable Git metadata or inability to prove the source revision.
6. The current local read-only validator has no Git or network capability. It can validate SHA syntax and bind a declared SHA into a signature, but cannot prove that the local working tree is that commit. It must report this limitation explicitly and must not claim repository-revision verification.

A commit SHA pins Git content identity, but it does not authenticate who approved it. That remains SEC-01.

## 4. Canonical phase-plan digest

The phase plan must be a separate, versioned JSON artifact. It must contain at least:
- product ID, repository identity and pinned commit SHA;
- phase ID and phase-plan schema version;
- ordered implementation/validation steps;
- exact acceptance criteria for each step;
- exact expected output paths and permitted changed paths;
- dependencies and preconditions;
- operation class and allowed action set;
- environment, provider and spend constraints.

Canonicalization contract:
- Use RFC 8785 JSON Canonicalization Scheme (JCS), UTF-8 encoded, with duplicate JSON keys and non-finite numbers rejected before canonicalization.
- Hash the canonical byte representation with SHA-256.
- Store the canonicalization profile identifier (for example, `RFC8785`) in the versioned contract.
- Do not hash pretty-printed JSON, a parsed-and-reserialized object using unspecified language defaults, Markdown prose, or a digest field embedded inside the object being hashed.
- Verify the digest against the phase-plan artifact from the pinned commit. Any change to a step, order, acceptance criterion, output path, dependency, or constraint changes the digest and invalidates the approval.

Independent cross-language canonicalization test vectors are required before the contract is used outside this Python prototype.

## 5. Operation-class registry

Operation class is a closed, versioned enum, not free-form text. Proposed registry:

| Class | Meaning | Current prototype policy |
|---|---|---|
| `read_only_validation` | Read files and run deterministic validation without writes or external calls | Only class eligible for the current read-only prototype |
| `repository_write` | Create or modify repository content, branches, issues or pull requests | Disabled; separate future approval |
| `external_provisioning` | Create or modify external services or infrastructure | Disabled; separate future approval |
| `deployment` | Deploy, release, change DNS or expose a live environment | Disabled; separate future approval |
| `destructive_change` | Delete, revoke, migrate destructively or irreversibly alter data/resources | Disabled; separate future approval and stronger review |

The registry version and exact class must be signed. A request cannot be promoted from one class to another by changing an issue label, plan, workflow input or agent output. The current validator must reject every class except `read_only_validation`; the table does not grant capability to any future class.

## 6. Cross-field invariants

Before signature verification can produce a plan-only result, the next implementation must check:
- request and approval agree on product ID, repository, commit SHA, target branch, ADR digest, phase ID, plan path, plan schema version, plan digest and operation class;
- the phase plan itself agrees with the request on repository, commit, product, phase, operation class, action set, paths and environment/provider/spend constraints;
- the normalized path set is duplicate-free and exactly equal across request, plan and approval;
- all paths are confined to the approved repository root; case-folding collisions and platform-ambiguous paths are rejected where relevant;
- allowed actions are a subset of the closed registry for the named operation class;
- no action, provider, environment or spend ceiling can be inferred from omitted fields;
- the approval's signature is checked only after strict parsing and canonical field validation.

A valid result remains plan-only. SEC-01 and SEC-02 must be solved before any approval can be considered executable.

## 7. Required negative test matrix

| ID | Mutation / attack | Expected result |
|---|---|---|
| T01 | Replace request commit SHA but retain approval | Reject commit mismatch |
| T02 | Change approval commit SHA without re-signing | Reject signature |
| T03 | Supply branch name, tag, abbreviated or malformed SHA instead of full commit SHA | Reject request |
| T04 | Change phase-plan bytes while retaining recorded digest | Reject plan digest mismatch |
| T05 | Change phase-plan digest in request but retain approval | Reject plan digest mismatch |
| T06 | Change phase-plan schema version | Reject schema/version mismatch |
| T07 | Change one step, step order or acceptance criterion | Reject plan digest mismatch |
| T08 | Add/remove/reorder an output or permitted path | Reject unless canonical normalized set and plan digest are re-approved |
| T09 | Change operation class from read-only to repository-write | Reject operation-class mismatch and disabled class |
| T10 | Use unknown or unversioned operation class | Reject |
| T11 | Add an action not allowed by the class registry | Reject |
| T12 | Change repository owner/name while keeping product ID | Reject repository mismatch |
| T13 | Change target branch after approval | Reject branch mismatch |
| T14 | Change ADR bytes or ADR digest | Reject ADR digest mismatch |
| T15 | Make request, plan and approval internally disagree on product, phase, commit, paths or constraints | Reject cross-field inconsistency |
| T16 | Use Unicode/case/path aliases that collide on the target platform | Reject ambiguous path set |
| T17 | Present a valid signed declared commit while the actual checkout HEAD differs | Trusted checkout verifier must reject; current local validator must report this as unverified, never verified |
| T18 | Change trusted policy after approval | Must be blocked by the separate SEC-04 policy-version/integrity control; SEC-03 signature alone is insufficient |
| T19 | Replay the exact otherwise-valid approval | Must be blocked by SEC-02 durable atomic claim; SEC-03 alone cannot prevent replay |

Tests T01–T16 belong in the deterministic validator once implementation is approved. T17 requires a separately trusted repository-revision verifier. T18 and T19 are explicit dependencies on SEC-04 and SEC-02 and must not be misrepresented as solved by this contract.

## 8. Compatibility and migration

- Introduce a new major approval schema version; do not mutate v1 semantics in place.
- Reject v1 approval records for any future execution path.
- Keep the current v1 verifier plan-only and clearly label its limitations until a separately reviewed migration is complete.
- Add positive test vectors for a single valid read-only request and independent canonicalization vectors.
- Add negative tests before wiring the new fields into any future executor.
- Do not create real product approvals or configure product repositories as part of this work.

## 9. Acceptance criteria for SEC-03 implementation

SEC-03 is not remediated until:
1. The new strict request/approval schema binds all required immutable revision, plan and operation fields.
2. The validator verifies the phase-plan digest and all cross-field invariants.
3. Negative tests T01–T16 and positive canonicalization vectors pass.
4. Checkout-revision verification is explicitly delegated to a trusted component and its result is not fabricated by the local validator.
5. Output wording distinguishes declared revision binding from verified checkout identity.
6. The independent security audit is updated with evidence and remaining limitations.

Even after SEC-03 passes, execution remains blocked by SEC-01, SEC-02, SEC-04 and SEC-05, plus independent re-audit and explicit owner approval.

## 10. Current boundary

This is a design artifact only. No validator behavior, approval records, policy, repository permissions, workflow, product repository, credentials, provider, infrastructure, billing, production data or deployment has been changed. No execution capability is introduced.
