# Follow-up Security Review — SEC-03, SEC-06 and SEC-07

**Review date:** 2026-11-27  
**Repository:** `siraajhussain-sketch/saas-factory`  
**Reviewed branch:** `security/sec-03-approval-scope-contract`  
**Reviewed head at time of review:** `91d588239f04ec96252f17f9ae2f7390de1e4955`  
**Review type:** Read-only assistant code review and CI evidence check. This is not a third-party audit, penetration test, cryptographic certification or guarantee of security.

## Decision

**Keep the factory read-only. Do not merge this draft PR or implement an executor based on this review.**

The follow-up code review found that the latest SEC-03 changes are internally consistent for their stated local, plan-only purpose. The identified SEC-06 double-read defect is addressed by snapshot reuse, and SEC-07 schema/chronology hardening is present. The authorization-critical gaps SEC-01, SEC-02, SEC-04 and SEC-05 remain open. SEC-03 remains partial because the actual checkout is not verified against the declared commit SHA.

## CI evidence

GitHub Actions run [45827461196](https://github.com/siraajhussain-sketch/saas-factory/actions/runs/45827461196) completed successfully for head `91d588239f04ec96252f17f9ae2f7390de1e4955`: **146 standard-library tests passed**.

The preceding follow-up run exposed a fixture-signature mismatch in a new positive exact-file-scope test. The fixture was corrected to sign the changed manifest, and the subsequent complete suite passed. The failed run remains visible in CI history; it was not hidden or rewritten.

## SEC-03 — partial implementation, not closed

### Confirmed in source

- V2 manifest requires a full lowercase 40-character declared commit SHA.
- The signed approval binds repository identity, declared commit, target branch, ADR digest, phase-plan path/schema/digest, phase, operation-class registry/version, action set, exact permitted path list, environment, provider allowlist, zero-spend ceiling and validity timestamps.
- The phase plan is parsed with duplicate-key/non-finite-number rejection, canonicalized using the documented restricted safe-integer profile, hashed and cross-checked against the manifest.
- Plan steps must use the closed read-only action set; write, provisioning, deployment and destructive operation classes are disabled.
- Expected output paths are checked against directory scopes as prefixes and file scopes by exact equality. A filename-prefix sibling is rejected.
- Signed `not_before` is required and enforced, with `issued_at <= not_before < expires_at`.
- The validator explicitly reports `DECLARED_ONLY_NOT_CHECKED_OUT`; it does not claim that the runtime checkout matches the declared SHA.

### Remaining blockers

1. There is no trusted verifier that compares actual checkout HEAD and repository identity with the signed revision.
2. HMAC is still a shared secret. Anyone holding it can mint approvals and claim an arbitrary approver label; identity is not authenticated (SEC-01).
3. There is no durable replay/revocation ledger or atomic one-time claim (SEC-02).
4. Policy is not yet protected by a separately trusted configuration boundary (SEC-04).
5. Approval and review records are not authenticated audit evidence (SEC-05).

The v2 contract is a local validation prototype, not executable authorization. Its canonicalization profile is intentionally restricted; it must not be advertised as a general-purpose implementation of RFC 8785.

## SEC-06 — identified double-read gap remediated

The current case consistency flow captures declared artifact bytes once, passes those snapshots to manifest hash verification, and decodes the same bytes for structural validation. The regression test covers mutation of the on-disk file after snapshot capture and confirms that the checker continues using the hash-matched snapshot. This addresses the originally reported condition where bytes hashed could differ from bytes structurally checked.

**Residual hardening note:** path confinement currently checks symlink components and then opens the resolved path. A hostile process able to race filesystem path replacement during snapshot capture could potentially exploit a check/open race. The current regression test does not establish race-free file opening against a concurrent filesystem attacker. This is outside the originally identified hash-versus-validation double-read defect and should be addressed before treating the local file reader as robust against hostile concurrent writers. No executor or untrusted product-repository integration should be enabled in the meantime.

## SEC-07 — schema and chronology hardening present

The lifecycle and review validators reject unknown/missing fields for their current schema versions, require timezone-aware timestamps, enforce case timestamp bounds and state-history ordering, and validate review target-date format. Review records remain descriptive, editable claims: reviewer labels, finding statuses and resolution notes are not authenticated or independently verified. Structural validity is not human review or authorization.

## Safety boundary verified

- The reviewed v2 path is plan-only and has no executor.
- Provider calls, spend and environment access remain disabled in the v2 contract.
- The PR branch contains no workflow change as part of this follow-up.
- No merge, product-repository write, secret, credential, infrastructure, billing, deployment or production action was performed.

## Next bounded work

1. Keep PR #1 in draft and unmerged.
2. Design and test the trusted checkout verifier and separately trusted policy boundary; do not implement either until their trust root and exact PR-head-versus-merge-commit semantics are approved.
3. Resolve authenticated identity/signing and durable replay/revocation/atomic claim before any executor proposal.
4. Consider race-resistant file opening for the local artifact reader.
5. Revisit SEC-05 audit integrity and recovery.
6. Only after all critical/high authorization gates pass independent review should a separate executor proposal be considered.

**No authorization is granted by this review.** It does not approve implementation execution, product-repository mutation, paid services, credentials, provisioning, production-data access, deployment, DNS changes or public launch.
