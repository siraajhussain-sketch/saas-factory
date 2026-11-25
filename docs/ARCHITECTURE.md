# Factory Architecture

## 1. Purpose

The factory coordinates a controlled product lifecycle. It is not itself the runtime or data plane for customer-facing SaaS products.

## 2. Separation of responsibilities

### Factory control plane

Responsible for:
- Product intake and structured requirements.
- Governance and approval records.
- Architecture review coordination.
- Repository provisioning requests.
- Phase planning and validation orchestration.
- Audit records and human review checkpoints.

### Product repository and runtime

Responsible for:
- Product-specific source code and configuration.
- Product architecture decisions and threat model.
- Tenant, identity, membership, and authorization implementation.
- Database schema, migrations, and data lifecycle.
- Product-specific tests, deployment, monitoring, and support.

The factory must not become a shared runtime database for unrelated products. Product secrets and production data belong in product-specific security boundaries.

## 3. Product architecture package

Before implementation, each product must document:

1. Product purpose, users, buyer, and critical workflows.
2. Domain entities and data classification.
3. Tenant or ownership root and complete ownership graph.
4. Identity, membership, roles, and server-side authorization.
5. Database isolation and migration strategy.
6. Threat model and abuse cases.
7. Privacy, retention, deletion, export, and audit requirements.
8. Date, timezone, currency, and localization semantics.
9. External providers, dependencies, and cost assumptions.
10. Backup, recovery, monitoring, and operational responsibilities.
11. Test strategy and measurable acceptance criteria.
12. Explicitly deferred features and known risks.

## 4. Architecture decision records

Each material architecture choice should have an ADR containing:
- Context and problem statement.
- Constraints and assumptions.
- Options considered.
- Decision and rationale.
- Security and privacy implications.
- Cost and operational implications.
- Consequences, trade-offs, and unresolved questions.
- Owner, status, version, and review date.

An implementation approval must identify the exact ADR version or content hash it covers. Changing a material decision invalidates the affected approval until reviewed again.

## 5. Orchestration lifecycle

The intended lifecycle is:

`INTAKE → DISCOVERY → ARCHITECTURE_DRAFT → AWAITING_OWNER_APPROVAL → REPOSITORY_SETUP → IMPLEMENTATION → VALIDATION → AWAITING_HUMAN_REVIEW → RELEASE_APPROVAL`

Any stage may enter `BLOCKED` when required evidence, permissions, approvals, or validation are missing.

Each implementation phase must have its own scope, acceptance criteria, branch/path boundaries, validation commands, and approval.

## 6. Provider adapters

External model and service providers must be optional adapters:
- Disabled by default.
- Invoked only in an explicitly approved phase.
- Configured with an explicit provider, model, purpose, and spend ceiling.
- Kept separate from deterministic validation and policy checks.
- Prevented from receiving secrets or unnecessary personal data.

The factory must remain useful for manual workflows and deterministic checks when all AI providers are disabled.

## 7. Current implementation status

This repository is currently a documentation and governance baseline. The architecture above describes intended behavior; it must not be interpreted as proof that an executor, approval service, replay ledger, or production control plane exists.
