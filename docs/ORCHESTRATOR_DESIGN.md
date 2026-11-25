# Orchestrator Design — Proposal Only

**Status: design document. No autonomous executor is enabled by this document.**

## Components

1. Intake adapter — accepts a structured product brief.
2. Policy engine — validates repository, product, scope, and approval requirements.
3. Planner — proposes bounded phases and acceptance criteria.
4. Architecture reviewer — checks the product-specific architecture and threat model.
5. Approval controller — verifies owner decisions and their scope.
6. Repository provisioner — creates an isolated product repository after approval.
7. Implementation worker — performs only the approved phase.
8. Validation worker — runs deterministic checks and reports evidence.
9. Human review controller — requests acceptance or changes.
10. Audit reporter — records decisions, actions, results, and failures.

## State model

`INTAKE`, `DISCOVERY`, `ARCHITECTURE_DRAFT`, `AWAITING_OWNER_APPROVAL`, `APPROVED_FOR_PHASE`, `REPOSITORY_SETUP`, `IMPLEMENTATION`, `VALIDATION`, `AWAITING_HUMAN_REVIEW`, `BLOCKED`, `RELEASE_APPROVAL`, `RELEASED`.

State transitions must be explicit and validated. An error or unavailable approval service must fail closed.

## Approval binding

An approval should bind to:
- Product identifier and target repository.
- Exact ADR version or content hash.
- Exact phase and acceptance criteria.
- Branch and normalized allowed path set.
- Provider permissions and spend ceiling.
- Environment and permitted side effects.
- Issuer, issue time, expiry, and revocation status.
- Unique nonce or approval identifier.

A broad “approved” flag is insufficient. A generic “continue” message is not approval for spending, production, deployment, or destructive actions.

## Security requirements

- Labels and issue text are routing metadata, never authorization.
- Treat issue content, model output, repository files, and external responses as untrusted input.
- Use least-privilege identities and workflow permissions.
- Do not expose secrets to untrusted pull-request code or prompts.
- Pin automation dependencies and bound timeouts, retries, and concurrency.
- Make actions idempotent and record durable audit events.
- Verify approval scope immediately before every side effect.
- Revoke or invalidate approvals when their bound architecture or scope changes.

## Approval service dependency

A production approval service requires authenticated issuers, protected signing keys, key rotation, a durable transactional replay/revocation ledger, atomic one-time claims, audit controls, and independent security review. A local signature check alone does not provide replay protection or prove who approved an action.

## Safe initial implementation order

A future implementation should proceed incrementally:
A. Static schemas and deterministic policy validation.
B. Unit tests and CI for the validator.
C. Read-only planning with no provider calls.
D. Approval service and durable replay/revocation controls.
E. Repository provisioning behind explicit approval.
F. Bounded implementation and validation workers.

Each stage requires review before the next stage is enabled.
