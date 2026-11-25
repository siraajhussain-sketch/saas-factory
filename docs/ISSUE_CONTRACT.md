# Product Intake Issue Contract

A product intake issue requests evaluation, not implementation.

## Required intake fields

- Product name and one-sentence purpose.
- Target buyer and user.
- Problem and current alternatives.
- Primary workflows.
- Intended geography and operating jurisdictions.
- Data types and sensitivity.
- Proposed business model.
- Known integrations and external dependencies.
- Cost constraints.
- Assumptions and unanswered questions.

## Routing labels

Suggested labels:
- `product-intake`
- `discovery-review`
- `architecture-review`
- `architecture-approved`
- `phase-review`
- `blocked`
- `human-review`
- `release-review`

Labels may route work or make queues easier to manage. They must never authorize implementation, spending, credential use, production access, or release.

## Structured approval record

An approval record should include:
- Approval identifier.
- Issuer identity and authentication evidence.
- Product and repository.
- ADR version/hash.
- Exact phase and acceptance criteria.
- Branch and allowed paths.
- Provider permissions and spend cap.
- Environment and permitted side effects.
- Issued-at and expiry timestamps.
- Nonce, revocation state, and audit reference.

Do not parse free-form issue comments as machine authorization. If approval is ambiguous or cannot be cryptographically and transactionally verified, stop.
