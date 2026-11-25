# Approval Gates

Approvals are scoped decisions, not general permission to proceed. Each gate must record the decision-maker, scope, evidence, timestamp, expiry, and any limits.

## Gate 0 — Product intake

Required:
- Product brief with target users, buyer, problem, and critical workflows.
- Initial feasibility and differentiation assessment.
- Known regulatory, privacy, and data sensitivity considerations.
- Explicit list of assumptions and unresolved questions.

Outcome: approve discovery, request changes, or reject.

## Gate 1 — Architecture and security

Required:
- Product-specific architecture decision record.
- Tenant/ownership model and authorization graph.
- Threat model and data classification.
- Persistence, migration, privacy, retention, and recovery design.
- External dependency and cost assessment.
- Test and acceptance plan.

Outcome: approve a named ADR version for a named next phase, request changes, or block.

## Gate 2 — Repository setup

Required:
- Explicit target repository and owner.
- Repository visibility and data classification.
- Approved starter stack and baseline controls.
- Branch, path, and workflow permissions.
- Confirmation that no unrelated product repository will be modified.

Outcome: approve only the specified repository setup.

## Gate 3 — Implementation phase

Required:
- Exact phase identifier and scope.
- Approved ADR version/hash.
- Allowed repository, branch, and paths.
- Acceptance criteria and validation commands.
- Provider and spend policy.
- Expiry and revocation behavior.

Outcome: approve one bounded phase. A new phase requires a new approval.

## Gate 4 — External services and spending

Separate explicit approval is required before:
- Paid model/API calls or subscriptions.
- Cloud resources or services that can incur charges.
- Billing activation or payment processing.
- Production credentials or live third-party integrations.
- Use of real customer or employee data.

Approval must identify provider, purpose, environment, maximum spend, duration, and owner.

## Gate 5 — Production readiness

Required:
- Security and privacy review.
- Authorization and tenant-isolation test evidence.
- Backup and restore evidence.
- Monitoring, alerting, and incident response plan.
- Migration and rollback plan.
- Performance and reliability assessment.
- Legal/compliance review where applicable.
- Human acceptance testing.

Outcome: approve release review or block.

## Gate 6 — Release

Separate approval is required for:
- Production deployment.
- DNS or domain changes.
- Public launch or opening access to real users.
- Enabling production billing.
- Destructive migrations or data operations.

The release approval must specify the exact product, environment, version, and rollback owner.

## Stop conditions

Stop and request review when:
- The repository, branch, product, or target environment is ambiguous.
- An approval is missing, expired, revoked, malformed, or out of scope.
- The ADR changes after approval.
- Required validation fails or is skipped.
- A paid service, live credential, production data, or destructive action is proposed without its separate approval.
- A workflow attempts to infer authorization from issue labels, comments, or generic natural-language instructions.
