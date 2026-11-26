# Phase 1 Validator — Security Gap Review

**Review type:** Read-only source and test review  
**Reviewed baseline:** Phase 1.1 strict-input-hardening commit  
**Decision:** Keep the validator plan-only. Do not connect an executor or treat its HMAC approval as production authorization.

## 1. Controls currently present

- Python standard library only; no network, shell, Git, repository-write, provider, provisioning or deployment capability.
- Explicit dry-run mode required at the CLI.
- Empty repository allowlist fails closed.
- Repository, branch, phase and path-prefix policy checks.
- ADR file confinement and SHA-256 content integrity verification.
- Exact equality between manifest paths and signed approval paths.
- Provider-disabled, zero-spend and no-environment constraints.
- Expiry, future-issued time, maximum seven-day lifetime and signed revocation-flag checks.
- Duplicate JSON object keys and non-standard JSON constants are rejected by the file loader.
- Path checks reject traversal, empty segments, backslashes, control/format characters, non-NFC Unicode, stream markers and ambiguous trailing dots/spaces.
- Resolved ADR paths escaping the repository root through symlinks are rejected.
- Approval nonce format requires 64 lowercase hexadecimal characters.
- Secret redaction and standard-library adversarial tests.

These controls support the stated read-only prototype boundary. They do not establish production authorization.

## 2. Gap status

| Priority | Gap | Current status | Required before a trusted issuer or executor |
|---|---|---|---|
| Critical | No authenticated issuer | **Open** — approver remains a free-form string | Bind a stable authenticated human subject and verified repository authority |
| Critical | Shared HMAC secret | **Open** — verifier and any key holder can create signatures | Isolated asymmetric signing boundary with key IDs, rotation and compromise handling |
| Critical | No durable replay/revocation ledger | **Open** — revocation is a signed boolean; no independent ledger | Durable transactional ledger, unique approval ID/nonce, atomic claim and revocation |
| Critical | No atomic one-time claim | **Open** — same valid approval can validate repeatedly | Claim state transition before any future side effect |
| High | No phase-plan digest | **Open** — approval binds phase name and paths, not exact plan and acceptance criteria | Bind immutable phase-plan digest |
| High | No immutable repository revision | **Open** — approval binds repository name, branch and ADR content hash, not repository commit identity | Bind immutable source commit and ADR blob identity |
| High | Incomplete approver evidence | **Open** — no authentication method, stable subject or evidence reference | Record identity proof reference and authorization result |
| High | No operation-class binding | **Open** — approval does not identify a narrow operation type | Add explicit operation class and allowed action set |
| High | No signing key ID | **Open** — validator reads one environment variable | Key IDs, key status, rotation and retirement checks |
| Medium | Nonce generation and uniqueness | **Partially addressed** — format is now exactly 64 lowercase hex characters; randomness and uniqueness are not proven | Trusted CSPRNG issuer plus durable uniqueness constraint |
| Medium | JSON duplicate-key ambiguity | **Addressed at file-input boundary** — duplicate keys rejected by object-pairs hook | Preserve strict parser at every future input boundary |
| Medium | Non-standard JSON constants | **Addressed at file-input boundary** — NaN and infinities rejected | Preserve strict parser at every future input boundary |
| Medium | Canonicalization contract | **Open** — local sorted compact JSON only; no cross-language canonicalization contract | Specify versioned canonical format and independent test vectors |
| Medium | Path edge-case coverage | **Improved** — traversal, Unicode normalization, control/format chars, Windows stream markers, trailing dot/space and symlink escape tests added | Revalidate paths at the actual filesystem write boundary before any future write |
| Medium | Audit and recovery | **Open** — no durable approval or execution audit exists | Define tamper-evident audit, backup, restore and incident recovery |

## 3. Specific remaining security observations

1. The approver field is not authentication. It is only a string checked for presence and length.
2. The HMAC key is read from FACTORY_APPROVAL_HMAC_KEY. This is suitable only for a local protocol experiment with a test key, not a production signing boundary.
3. The revoked flag is part of the signed payload. It cannot provide immediate independent revocation after issuance.
4. A 64-character hexadecimal nonce format does not prove cryptographic randomness, uniqueness or one-time use.
5. The canonical serializer sorts keys and removes whitespace, but there is no cross-language canonicalization contract.
6. The approval does not bind a phase-plan digest, immutable repository commit, operation class, authentication evidence or key ID.
7. Current path checks protect dry-run manifest validation and ADR lookup. Any future writer must revalidate normalized paths, symlinks and repository state immediately before writing; a prior dry-run check is not a write authorization.
8. No concurrency, durable replay, key rotation, or uncertain side-effect recovery tests exist because the issuer, ledger and executor do not exist.

## 4. Phase 1.1 disposition

**Completed:** strict duplicate-key JSON parsing, rejection of NaN/Infinity, top-level object requirement, nonce format validation, Unicode/path hardening, symlink escape coverage, documentation and adversarial tests.

The GitHub Actions check for the Phase 1.1 commit completed successfully: 32 unit tests passed.

**Not resolved:** authenticated owner identity, asymmetric signing, protected key management, durable replay/revocation ledger, atomic one-time claim, phase-plan digest, immutable repository revision binding, operation-class binding, audit and recovery.

## 5. Required disposition

- Keep Phase 1 and Phase 1.1 classified as local read-only validation prototypes.
- Do not add an executor, repository writer, provider adapter, deployment action or live credential.
- Do not create a signing key or place a shared HMAC key in GitHub Actions.
- Treat all current approval examples as test fixtures, not owner-issued authorization.
- Any future hardening must preserve the zero-side-effect boundary and receive its own tests and review.

## 6. Recommended next step

The next useful work is a design-level review of the remaining critical trust gaps and a practical no-cost feasibility comparison for a trusted identity boundary, asymmetric signer and durable transactional ledger. Do not implement those services or an executor until the design is reviewed, costs and recovery obligations are understood, and the owner explicitly approves a bounded implementation phase.
