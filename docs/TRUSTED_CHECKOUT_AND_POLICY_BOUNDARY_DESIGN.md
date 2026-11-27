# Trusted Checkout and Policy Boundary — Design Proposal

**Status:** Design only. No verifier, trusted workflow, external policy store, signing service, secret, permission, environment, branch rule, or infrastructure is implemented or configured.

## 1. Decision

Keep the factory read-only. SEC-03 remains partially implemented until a trusted component proves that the actual checked-out repository revision equals the immutable revision bound into the signed approval. SEC-04 remains open until policy is loaded from a separately controlled trust boundary and its exact version is pinned into the request and approval.

The current local validator checks declared SHA syntax and cross-field consistency. It does not inspect Git metadata and must continue to report `DECLARED_ONLY_NOT_CHECKED_OUT`.

## 2. Threat model and trust boundaries

Treat product repository files, manifests, phase plans, pull-request branches, issue text, labels, model output, and artifacts produced by untrusted jobs as attacker-controlled inputs.

A future verifier must have a trust root independent of the checkout it is verifying:

| Component | Trust requirement | Prohibited assumption |
|---|---|---|
| Trusted verifier definition | Reviewed, immutable version controlled outside the target product worktree | A workflow file from the PR branch is trusted |
| Checkout identity | Repository owner/name and full commit SHA obtained from the signed approval and independently compared with actual Git state | A branch name, tag, manifest field, or Actions event label proves the checkout |
| Approval verification key | Public key or verification metadata obtained from the trusted verifier boundary | A key or verification policy supplied by the product checkout is trusted |
| Policy configuration | Separately controlled, versioned, integrity-checked configuration | Policy loaded from the same untrusted checkout can constrain that checkout |
| Product source | Read-only input at one immutable commit | Running product-controlled scripts is safe during verification |
| Human authorization | Verified independently by the issuer and ledger | A PR review, issue label, actor name, or workflow dispatch alone is approval |

## 3. Trusted checkout verifier requirements (SEC-03)

A future verifier should be a small, deterministic component with no product-code execution, no write token, no provider access, and no deployment capability.

### Required inputs

- Exact GitHub repository owner/name.
- Full lowercase 40-character commit SHA from the verified approval payload.
- Target branch as a separately approved destination constraint.
- Approval ID and canonical scope digest.
- Trusted verifier version and policy version/digest.

### Required checks

1. Confirm the runtime repository identity matches the signed owner/name exactly.
2. Confirm the expected immutable commit SHA comes from the verified approval, not an untrusted workflow input or manifest alone.
3. Check out that exact SHA; do not resolve a mutable branch or tag at verification time.
4. Compare `git rev-parse HEAD` with the signed SHA and fail closed on mismatch.
5. Confirm the commit object and tree are available and the checkout is not shallow in a way that prevents required ancestry or object checks.
6. Verify the ADR and phase-plan files from that exact commit/tree and compare their digests with the signed scope.
7. Ensure the verifier does not execute scripts, hooks, package lifecycle commands, submodules, LFS filters, or other product-controlled code.
8. Disable persisted checkout credentials; use read-only repository access only where access is required.
9. Emit a structured result containing repository identity, expected SHA, actual SHA, tree SHA, verifier version, policy digest, approval ID, and explicit pass/fail reasons.
10. Bind the result to the same approval and scope digest; reject missing, stale, ambiguous, or mismatched evidence.

### Pull request and merge-commit caution

GitHub pull-request workflows may test a synthetic merge commit rather than the pull-request head commit. Those are different Git objects. The verifier must define whether the approved subject is the PR head, a proposed merge tree, or the final merge commit. It must never silently substitute one for another.

For a phase approval, the safer default is to bind the exact commit whose content was reviewed. If merging changes the tree or creates a new commit, the approval must be re-evaluated against that new immutable revision. A successful test of a PR merge ref is not proof that the approved head SHA was checked out.

### Fail-closed conditions

Reject when repository identity is ambiguous, SHA is abbreviated or malformed, checkout HEAD differs, required Git objects are unavailable, the source is modified after checkout, the verifier cannot establish which commit was checked, or any product-controlled code would need to run to establish trust.

A verifier result is evidence of checkout identity only. It does not authenticate the approver, prevent replay, establish policy trust, or authorize execution.

## 4. Trusted policy boundary (SEC-04)

The policy must not be loaded from the product worktree whose behavior it constrains.

### Candidate design

Use a separately controlled factory-policy repository or equivalent owner-controlled configuration boundary. The trusted verifier pins an immutable policy commit and verifies the policy digest before evaluating a request.

The policy should contain:
- Allowed product and repository identities.
- Allowed target branches and lifecycle phases.
- Allowed path roots and path normalization rules.
- Operation-class registry version and enabled actions.
- Provider allowlist, environment policy and spend ceiling (zero by default).
- Required review level and approval class.
- Policy schema version, owner metadata, effective time and change history.

The approval payload should bind both the immutable policy revision and its canonical digest. A policy change must not retroactively widen an already-issued approval. A changed policy requires a new validation decision and, where authorization scope changes, a new approval.

### Policy update controls

- Only designated owners may propose or approve policy changes.
- Policy changes require a reviewed change record and independent validation.
- The verifier must reject unknown policy fields and unsupported policy versions.
- Policy rollback, key rotation and emergency revocation require explicit, auditable procedures.
- The verifier must fail closed if the pinned policy is missing, corrupt, unavailable, expired, or inconsistent with the approval.
- Policy source and verifier source must not be mutable by the same untrusted product build process.

### GitHub-only option

A protected repository, protected default branch, required reviewers, and a reusable workflow pinned to an immutable commit may be evaluated as a no-new-infrastructure option. These protections are not assumed to be available on the user's current plan or configured in this repository. Public visibility alone is not a trust boundary. Repository settings, plan entitlements, administrator permissions and workflow protections must be inspected read-only before selecting this option.

A workflow that reads policy from a separate repository is not sufficient unless the exact policy commit is pinned and its integrity is verified. A mutable branch such as `main` is a locator, not an immutable policy identity.

## 5. Interaction with SEC-01, SEC-02 and SEC-05

This design does not close the other authorization findings:

- **SEC-01:** a trusted checkout and policy do not prove who approved. A protected asymmetric signing boundary and authenticated owner identity remain necessary.
- **SEC-02:** a valid signature and exact checkout do not prevent replay. A durable ledger, independent revocation and atomic one-time claim remain necessary.
- **SEC-05:** verifier output and lifecycle records are not authenticated audit evidence unless emitted into a protected, tamper-evident audit boundary.

No future verifier result may be interpreted as permission to write, spend, provision, access production data, deploy, release, or perform destructive operations.

## 6. Verification and adversarial test matrix

| Test | Attack or mutation | Required outcome |
|---|---|---|
| V01 | Actual HEAD differs from signed commit SHA | Reject |
| V02 | Same SHA supplied for a different repository owner/name | Reject |
| V03 | Manifest SHA matches but approval SHA differs | Reject |
| V04 | Branch moves after approval | Continue using the signed immutable SHA; do not resolve branch again |
| V05 | PR merge commit substituted for approved head commit | Reject unless that exact merge commit was separately approved |
| V06 | Checkout is shallow or required objects unavailable | Reject when required identity/ancestry proof cannot be established |
| V07 | Product checkout changes after verification | Reject or invalidate evidence; do not rely on stale verification |
| V08 | Product repository supplies a weaker policy file | Ignore it; load only the pinned trusted policy |
| V09 | Trusted policy bytes change without a new approved digest | Reject |
| V10 | Policy revision is missing, unknown or unsupported | Reject |
| V11 | Policy is widened after approval | Existing approval remains bounded; new scope requires re-approval |
| V12 | Trusted verifier workflow is invoked from an untrusted PR ref | Reject or run only a separately pinned trusted verifier |
| V13 | Product-controlled script is required during verification | Reject; verification must remain data-only |
| V14 | Approval key or policy verification metadata is unavailable | Reject |

## 7. Implementation boundary and staged recommendation

No implementation is authorized by this design document.

Recommended order:
1. Independently re-audit the SEC-03 path and validity changes, plus SEC-06/SEC-07.
2. Select the trust root for the verifier and policy only after read-only inspection of repository settings, plan limits and owner permissions.
3. Define and test the verifier's immutable revision semantics, including PR head versus merge commit.
4. Define policy ownership, immutable version pinning, digest verification and emergency change process.
5. Resolve SEC-01 authenticated identity/signing and SEC-02 durable replay/revocation before any execution design.
6. Revisit SEC-05 audit evidence and recovery requirements.
7. Only then consider a separate, explicitly approved implementation proposal. Do not add an executor as part of verifier or policy work.

## 8. Explicit non-authorization

This proposal does not authorize branch protection or repository-setting changes, GitHub App installation, OAuth/OIDC configuration, secrets, signing keys, policy repository creation, cloud resources, paid services, provider calls, product repository writes, production access, deployment, DNS changes, or public launch.
