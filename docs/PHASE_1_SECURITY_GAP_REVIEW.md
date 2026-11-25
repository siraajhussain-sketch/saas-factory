# Phase 1 Validator — Security Gap Review

**Review type:** Read-only source and test review  
**Reviewed baseline:** public default branch after the Phase 1 validator implementation  
**Decision:** Keep the validator plan-only. Do not connect an executor or treat its HMAC approval as production authorization.

## 1. What the current implementation does well

- Uses Python standard library only.
- Has no network, shell, Git, repository-write, provider, provisioning or deployment capability.
- Requires explicit dry-run mode at the CLI.
- Fails closed on an empty repository allowlist.
- Checks repository, branch, phase and path-prefix policy.
- Confines the ADR file to the supplied repository root and verifies its SHA-256 content digest.
- Requires exact equality between manifest paths and signed approval paths.
- Enforces provider-disabled, zero-spend and no-environment constraints.
- Checks approval expiry, future issue time, maximum seven-day lifetime and the signed revocation flag.
- Redacts selected secret-like fields and values.
- Has a focused standard-library test suite.

These controls support the stated read-only prototype boundary. They do not establish production authorization.

## 2. Gaps relative to the approval-service design

| Priority | Gap | Current behavior | Required before a trusted issuer or executor |
|---|---|---|---|
| Critical | No authenticated issuer | Approver is a free-form string with a minimum length | Bind a stable authenticated human subject and verified repository authority |
| Critical | Shared HMAC secret | Verifier and any key holder can create signatures | Isolated asymmetric signing boundary with key IDs, rotation and compromise handling |
| Critical | No durable replay/revocation ledger | Revocation is a signed boolean in the approval object; nonce is syntax-checked only | Durable transactional ledger, unique approval ID/nonce, atomic claim and revocation |
| Critical | No atomic one-time claim | The same valid approval can validate repeatedly | Claim state transition before any future side effect |
| High | No phase-plan digest | Approval binds phase name and paths, not the exact plan and acceptance criteria | Bind immutable phase-plan digest |
| High | No immutable repository revision | Approval binds repository name, branch and ADR content hash, not a repository commit identity | Bind immutable source commit and ADR blob identity |
| High | Incomplete approver evidence | No authentication method, stable subject, or evidence reference | Record identity proof reference and authorization result |
| High | No operation-class binding | Approval does not identify a narrow operation type | Add explicit operation class and allowed action set |
| High | No signing key ID | Validator reads one environment variable | Key IDs, key status, rotation and retirement checks |
| Medium | Nonce unpredictability is not enforced | Nonce is checked against a general identifier regex | Require cryptographically random nonce generation at issuance; validator checks strict encoding/length |
| Medium | JSON duplicate-key ambiguity | Standard JSON parsing accepts duplicate object keys by default | Reject duplicate keys at every input boundary |
| Medium | Canonicalization is local JSON serialization | Sorted compact JSON is used; no separately specified cross-language canonicalization profile | Specify and test a versioned canonical format with independent test vectors |
| Medium | Path edge-case coverage | Traversal and prefix checks exist; tests do not cover all Unicode, symlink and normalization edge cases | Add adversarial tests and re-check paths at the actual filesystem boundary before any write |
| Medium | Audit and recovery not implemented | No durable approval or execution audit exists | Define tamper-evident audit, backup, restore and incident recovery |

## 3. Specific code observations

1. The approval's approver field is not authentication. It is only a string comparison for presence/length.
2. The HMAC key is read from FACTORY_APPROVAL_HMAC_KEY. This is suitable only for a local protocol experiment with a test key, not a production signing boundary.
3. The revoked flag is part of the signed payload. It cannot provide immediate independent revocation after issuance.
4. The nonce format check does not prove randomness, uniqueness or one-time use.
5. The canonical serializer sorts keys and removes whitespace, but duplicate JSON keys are not rejected by the current loader and there is no cross-language canonicalization contract.
6. The approval does not bind a phase-plan digest, immutable repository commit, operation class, authentication evidence or key ID.
7. The current path checks protect the dry-run manifest and ADR lookup. Any future writer must revalidate normalized paths, symlinks and repository state immediately before writing; a prior dry-run check is not a write authorization.
8. The test suite exercises signature tampering, expiry, revocation flag, branch mismatch and path-scope expansion. It does not yet test duplicate JSON keys, random nonce issuance, durable replay, concurrent claims, key rotation, or uncertain side-effect recovery.

## 4. Required disposition

- Keep Phase 1 classified as a local read-only validation prototype.
- Do not add an executor, repository writer, provider adapter, deployment action or live credential.
- Do not create a signing key or place a shared HMAC key in GitHub Actions.
- Treat all current approval examples as test fixtures, not owner-issued authorization.
- Any future hardening of the validator must preserve the zero-side-effect boundary and receive its own tests and review.

## 5. Recommended next engineering phase

Before implementation, approve a bounded **Phase 1.1 — Strict Input and Protocol Hardening** proposal. It should be limited to deterministic local validation, with no network, signing service, database, GitHub writes, product repository access or execution.

Candidate scope:
- reject duplicate JSON object keys;
- define a versioned canonical payload and cross-language test vectors;
- strengthen nonce format expectations while documenting that uniqueness requires a ledger;
- add missing adversarial path and parsing tests;
- clarify that the current HMAC approval is test-only and cannot represent authenticated owner consent.

The issuer, asymmetric signer, durable ledger and executor remain separate future decisions. This review itself does not authorize Phase 1.1 implementation.
