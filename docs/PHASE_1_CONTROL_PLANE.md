# Phase 1 — Deterministic Control Plane

**Status:** Prototype implementation; read-only planning only.

## Included

- Strict JSON schemas for product manifests, local policy, and phase-bound approvals.
- Duplicate JSON object keys and non-standard numeric constants (NaN and Infinity) are rejected at file-input boundaries.
- Repository, branch, phase, and path-prefix allowlists supplied by local policy.
- Confined ADR file resolution and SHA-256 integrity verification.
- Path checks reject traversal, empty segments, backslashes, control/format characters, non-NFC Unicode, platform stream markers, and ambiguous trailing dots/spaces.
- HMAC-SHA256 approval verification using an environment-supplied key.
- Exact approval binding to product, repository, ADR digest, phase, branch, and path set.
- Approval nonce format requires 64 lowercase hexadecimal characters. A future issuer must generate these from a cryptographically secure random source.
- Expiry, future-issued, revocation-flag, nonce-format, and seven-day lifetime checks.
- Secret redaction and fail-closed behavior.
- Standard-library unit tests and read-only CI.

## Deliberate limitations

- The public example policy has an empty repository allowlist and therefore rejects all product repositories until an owner configures a local policy file.
- A nonce format check does not establish nonce randomness, uniqueness, or one-time use. Those require a trusted issuer and durable transactional ledger.
- No approval issuer, protected signing-key service, durable replay/revocation ledger, or atomic one-time claim exists.
- HMAC verification does not establish issuer identity by itself; anyone with the shared secret can create a valid signature.
- The validator does not execute commands, modify repositories, call providers, provision infrastructure, or deploy.
- A valid approval produces a plan-only result. It is not an execution authorization.
- No real product repository, credentials, customer data, paid service, or production environment is configured.

## Local usage

Copy policy.example.json to a local, untracked policy.json, then explicitly configure the allowed product repository and permitted paths. Never commit signing keys or real approval records.

Run:

~~~bash
python -m unittest discover -s tests -v
python -m control_plane.validator --manifest examples/sample-manifest.json --policy policy.json --root . --dry-run
~~~

The sample manifest references docs/adr/001-example.md and contains its SHA-256 digest. If the ADR fixture is edited, recompute the digest in the sample manifest before running the validator.

## Security boundary

This is an early deterministic validation prototype, not a production approval service. Do not use it to authorize side effects, spending, production access, or release.
