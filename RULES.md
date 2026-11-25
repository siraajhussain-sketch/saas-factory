# Engineering and Security Rules

These rules apply to the factory's reusable process. They do not replace product-specific architecture or security review.

## 1. Product-specific design

- Do not assume a universal tenant identifier such as `tenant_id`, `workspace_id`, `organization_id`, or a domain-specific key.
- Every product must define its own tenant or ownership root, ownership graph, memberships, roles, resource boundaries, and threat model.
- Document whether the product is single-business, multi-business, delegated-service, marketplace, or another model.
- Define authorization rules before implementing data access.

## 2. Authorization and data isolation

- Enforce authorization on the server for every read, write, mutation, background job, export, and administrative action.
- Never rely solely on client-side route guards, hidden UI elements, or user-supplied identifiers.
- Use row-level security or an equivalent database enforcement mechanism where supported.
- Validate ownership and membership relationships at every trust boundary.
- Test cross-tenant access denial, privilege escalation, unauthenticated access, and branch/resource scoping.

## 3. Data and privacy

- Minimize collection and retention of personal and sensitive data.
- Define data classification, purpose, retention, deletion, backup, export, and access logging before production use.
- Never place secrets, access tokens, credentials, or sensitive personal data in source code, prompts, logs, test fixtures, or public issues.
- Use synthetic data in development and tests.
- Document jurisdiction-specific privacy and legal requirements for each product.

## 4. Persistence and correctness

- Do not use browser storage as the authoritative persistence layer for business records.
- Do not present mock or in-memory persistence as production persistence.
- Use explicit, versioned database migrations and a documented recovery strategy.
- Handle currency with integer minor units or safe decimal arithmetic; never use binary floating-point for financial calculations.
- Store timestamps consistently and define product-specific timezone and date-only semantics.
- Make scheduled jobs, webhooks, and externally retried operations idempotent.

## 5. Quality and operations

- Add tests for business rules, authorization boundaries, failure paths, and migrations.
- Do not weaken or remove tests merely to make a build pass.
- Keep changes small, reviewable, and linked to an approved phase.
- Document monitoring, backup, restore, incident response, and support expectations before release.
- A successful compilation is not evidence of security or production readiness.

## 6. Cost and approvals

- Default to zero spend and disabled external providers.
- Do not make paid API calls, enable billing, create paid infrastructure, or introduce recurring costs without explicit owner approval.
- Do not use dummy credentials to probe live provider endpoints.
- Production credentials, customer data, deployment, DNS, public launch, and destructive actions each require explicit approval.
- Generic instructions such as “continue” do not authorize paid, production, or destructive actions.

## 7. Public repository hygiene

- Keep product-specific confidential material, customer data, credentials, and internal incident details out of public repositories.
- Review commit metadata, workflows, logs, examples, and issue content before publication.
- Pin third-party automation dependencies to reviewed immutable references where feasible.
- Grant workflows only the minimum permissions they need.
