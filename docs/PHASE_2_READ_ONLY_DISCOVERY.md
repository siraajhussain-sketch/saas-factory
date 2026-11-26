# Phase 2 — Read-Only Product Discovery and Architecture Package

**Status:** Proposed operating contract; documentation and analysis only.

## Purpose
Turn a product idea into a decision-ready discovery and architecture package before any repository provisioning or implementation.

## Inputs
Use the Product Brief template and the intake issue contract. Missing information must be marked `UNKNOWN`; do not silently infer it. Ask only the highest-impact clarifying question when the missing answer blocks useful analysis.

## Required outputs
1. **Discovery report:** buyer, users, problem, workflows, alternatives, market/geography, business-model hypotheses, MVP boundary, risks and unresolved questions.
2. **Evidence register:** each material claim, source URL or owner-provided evidence, publisher, publication/access date, evidence type, confidence, limitations and the decision it informs.
3. **Architecture package:** domain model, ownership root and graph, identity/membership/authorization, data classification, persistence, integrations, privacy, localization, operations, test strategy and ADR drafts.
4. **Cost and dependency assessment:** development and runtime dependencies, free-tier assumptions, quota/retention/pause limits, migration costs, vendor lock-in, and recurring-cost scenarios. No account/resource is created to verify a tier.
5. **Decision log:** explicit owner decisions, recommended decisions, unresolved choices and rejected options only when useful to explain a material trade-off.
6. **Phase proposal:** smallest bounded next phase, exact deliverables, acceptance criteria, files/repositories in scope, out-of-scope actions and expected costs.

## Evidence rules
- Separate verified facts, sourced estimates, assumptions, hypotheses and recommendations.
- Cite current sources for market, competitor, legal, pricing, vendor-plan and technical capability claims.
- Record source date and geography; distinguish global information from jurisdiction-specific requirements.
- Do not present search-result counts, vendor marketing claims or anecdotal reviews as proof of demand.
- Never invent customer interviews, willingness-to-pay, competitor capabilities, regulatory advice or cost guarantees.
- If evidence is missing, state what must be validated and how, without claiming validation has occurred.

## Architecture rules
- No universal tenant identifier or shared domain model. Each product defines its own ownership root and resource graph.
- Design authorization server-side and test cross-owner access denial.
- Define data classification, minimization, retention, deletion, export and audit needs before implementation.
- Define date-only, timezone, currency and locale semantics explicitly.
- Identify provider and infrastructure alternatives; default to no provider and zero spend.
- Document backup, restore, monitoring, incident response and support obligations, even if deferred from MVP.

## Decision states
- `DRAFT`: incomplete or awaiting evidence.
- `READY_FOR_OWNER_REVIEW`: package is internally complete, but no implementation is authorized.
- `BLOCKED`: critical unknown, unsafe assumption or missing evidence prevents a sound recommendation.
- `OWNER_APPROVED_FOR_NEXT_PHASE`: explicit approval for one separately scoped next phase only.

## Hard boundary
Phase 2 is read-only. It does not create repositories, issues, branches, files in product repositories, credentials, cloud resources, databases, provider calls, paid subscriptions, customer accounts, production data or deployments. An owner approval of discovery does not approve implementation.

## Acceptance criteria
- Every material recommendation has evidence or is explicitly labelled a hypothesis.
- Product-specific ownership and authorization model is documented or marked blocked.
- Data categories and privacy implications are identified.
- MVP and exclusions are explicit.
- Cost assumptions and recurring dependencies are visible.
- Risks, unknowns and validation actions are recorded.
- A bounded next-phase proposal exists, with no implied authorization.