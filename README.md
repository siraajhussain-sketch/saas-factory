# SaaS Factory

A reusable, approval-gated framework for evaluating, designing, and building independent SaaS products.

The factory is a control plane. Each product has its own architecture, ownership model, security boundaries, repository and release approvals.

## Current status

This repository contains governance, design documents, a deterministic read-only validator and a read-only Phase 2 package completeness checker. It is not an autonomous build system and does not provision products, call paid AI providers, create cloud resources, handle production credentials or deploy applications.

## Core principles

- Product-specific architecture; no universal tenant model.
- Server-side authorization and explicit resource ownership.
- Zero-spend default; no paid APIs or infrastructure without explicit owner approval.
- Human approval for each material phase and release.
- Isolation of product repositories, credentials and customer data.
- Traceable evidence, decisions, validation and exceptions.

## Lifecycle

1. Product intake and discovery.
2. Product-specific architecture and threat-model draft.
3. Explicit approval of a bounded implementation phase.
4. Isolated product repository setup.
5. Small, ordered implementation phases with review.
6. Automated validation and human acceptance.
7. Separate release approval.

## Design and implementation notes

- [Factory architecture](docs/ARCHITECTURE.md)
- [Approval gates](docs/APPROVAL_GATES.md)
- [Approval service design](docs/APPROVAL_SERVICE_DESIGN.md)
- [Approval infrastructure options](docs/APPROVAL_INFRASTRUCTURE_OPTIONS.md)
- [Current zero-cost feasibility decision](docs/APPROVAL_ZERO_COST_FEASIBILITY_2026-11.md)
- [Phase 1 deterministic validator](docs/PHASE_1_CONTROL_PLANE.md)
- [Phase 1.1 strict input hardening](docs/PHASE_1_1_STRICT_INPUT_HARDENING.md)
- [Phase 2 discovery and architecture package](docs/PHASE_2_READ_ONLY_DISCOVERY.md)
- [Phase 2 package validator](docs/PHASE_2_PACKAGE_VALIDATOR.md)

## Important limitations

Documentation and passing tests do not establish production readiness. Each product requires independent security, privacy, legal, reliability, cost and operational review.

## Repository boundaries

Do not place customer data, secrets, provider credentials or confidential product specifications in this public repository. Use a private product repository for sensitive material.


## Phase 2 package validator

The local deterministic validator checks the structure of discovery, architecture and evidence documents. It uses only the Python standard library and never writes files or invokes providers.

See [Phase 2 validator](docs/PHASE_2_PACKAGE_VALIDATOR.md) for usage and limitations.
