# SaaS Factory

A reusable, approval-gated framework for evaluating, designing, and building independent SaaS products.

The factory is a control plane. Each product has its own architecture, ownership model, security boundaries, repository and release approvals.

## Current status

This repository contains governance, design documents, deterministic read-only validators and a no-network mock for the optional AI discovery boundary. It is not an autonomous build system and does not provision products, call paid AI providers, create cloud resources, handle production credentials or deploy applications.

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
- [Factory lifecycle audit (2026-11-26)](docs/FACTORY_LIFECYCLE_AUDIT_2026-11.md)
- [Lifecycle manifest and state contract](docs/LIFECYCLE_MANIFEST.md)
- [Product case consistency checker](docs/CASE_CONSISTENCY_CHECKER.md)
- [Synthetic end-to-end product case walkthrough](docs/SYNTHETIC_END_TO_END_WALKTHROUGH.md)
- [Approval gates](docs/APPROVAL_GATES.md)
- [Approval service design](docs/APPROVAL_SERVICE_DESIGN.md)
- [Approval infrastructure options](docs/APPROVAL_INFRASTRUCTURE_OPTIONS.md)
- [Current zero-cost feasibility decision](docs/APPROVAL_ZERO_COST_FEASIBILITY_2026-11.md)
- [Phase 1 deterministic validator](docs/PHASE_1_CONTROL_PLANE.md)
- [Phase 1.1 strict input hardening](docs/PHASE_1_1_STRICT_INPUT_HARDENING.md)
- [Phase 2 discovery and architecture package](docs/PHASE_2_READ_ONLY_DISCOVERY.md)
- [Product Brief validator](docs/PRODUCT_BRIEF_VALIDATOR.md)
- [Phase 2 package validator](docs/PHASE_2_PACKAGE_VALIDATOR.md)
- [AI-assisted discovery design](docs/AI_ASSISTED_DISCOVERY_DESIGN.md)
- [AI output contract and no-network mock](docs/AI_OUTPUT_CONTRACT.md)
- [NLP evaluation dataset and scoring harness](docs/AI_EVALUATION_HARNESS.md)

## Important limitations

The AI output validator checks structure and exact source-span traceability only; it does not verify factual truth, source quality or interpretation. Mock output is fixed fixture data, not model inference. Documentation and passing tests do not establish production readiness. Each product requires independent security, privacy, legal, reliability, cost and operational review.

## Repository boundaries

Do not place customer data, secrets, provider credentials or confidential product specifications in this public repository. Use a private product repository for sensitive material.
