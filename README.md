# SaaS Factory

A reusable, approval-gated framework for evaluating, designing, and building independent SaaS products.

The factory is a control plane. Each product must have its own repository, architecture decisions, tenant and authorization model, data boundaries, operational configuration, and release approvals.

## Current status

This repository currently contains public, product-agnostic governance and design documents. It is not an autonomous build system and does not provision products, call paid AI providers, create cloud resources, handle production credentials, or deploy applications.

No product implementation is authorized by the presence of these documents.

## Core principles

- Product-specific architecture: no universal tenant key or assumed data model.
- Secure by default: server-side authorization and explicit resource ownership.
- Zero-spend default: no paid APIs, services, or infrastructure without explicit owner approval.
- Human approval: discovery, architecture, implementation phases, external spend, and release are separate decisions.
- Isolation: product repositories and credentials are separated from the factory.
- Traceability: decisions, approvals, validation results, and exceptions are recorded.

## Lifecycle

1. Product intake and discovery.
2. Product-specific architecture and threat-model draft.
3. Explicit approval of the architecture and first implementation phase.
4. Isolated product repository setup.
5. Small, ordered implementation phases with review.
6. Automated validation and human acceptance.
7. Separate release approval.

## Design and implementation notes

- [Factory architecture](docs/ARCHITECTURE.md)
- [Approval gates](docs/APPROVAL_GATES.md)
- [Approval service design](docs/APPROVAL_SERVICE_DESIGN.md)
- [Approval control-plane threat model](docs/APPROVAL_CONTROL_PLANE_THREAT_MODEL.md)
- [Approval infrastructure options](docs/APPROVAL_INFRASTRUCTURE_OPTIONS.md)
- [Phase 1 deterministic validator](docs/PHASE_1_CONTROL_PLANE.md)
- [Phase 1 validator security gap review](docs/PHASE_1_SECURITY_GAP_REVIEW.md)
- [Cost policy](docs/COST_POLICY.md)

## Important limitations

This repository is a governance baseline, not a production-readiness guarantee. Each product requires independent security, privacy, legal, reliability, cost, and operational review. A passing build or test suite does not establish production readiness.

## Repository boundaries

Do not place customer data, secrets, provider credentials, private product specifications, or product-specific architecture documents in this public repository. Use a private product repository for sensitive or commercially confidential material.
