# Human Review Checklist

**Status:** Review aid only. This checklist does not grant implementation, spending, provisioning, credential, deployment or release authority.

## How to use

- Review the artifacts for one product case and one immutable version at a time.
- Record the reviewer, review date, artifact versions/digests, evidence considered, findings and decision.
- Mark each item **PASS**, **FAIL** or **N/A**. Explain every FAIL and N/A; do not silently skip unresolved items.
- A checklist pass means only that the named human review was completed against the stated scope. It is not proof that claims are true, that the product is secure, or that a later phase is authorized.
- Keep model-generated content clearly marked as draft. A model's confidence, citations, validation result or recommendation is not human approval.
- If a critical fact is unknown, preserve it as **UNKNOWN** and block decisions that depend on it rather than filling the gap with an assumption.

## Review record

- Product case ID:
- Product name:
- Review stage: Discovery / Evidence / Architecture / Cost / Security / Combined
- Artifact version(s) and SHA-256 digest(s):
- Reviewer(s):
- Review date (UTC):
- Scope and exclusions:
- Decision: ACCEPT FOR NEXT HUMAN REVIEW / REVISE / BLOCKED
- Conditions and unresolved questions:

## 1. Discovery and product understanding

- [ ] The intended buyer, end user and other affected parties are distinguished.
- [ ] The problem is described as a concrete workflow and outcome, not merely a feature or technology.
- [ ] The frequency, urgency and consequences of the problem are stated; unsupported claims remain assumptions.
- [ ] Current alternatives, including manual work, spreadsheets, incumbent products and doing nothing, are considered.
- [ ] Geography, language, jurisdiction and operating context are explicit.
- [ ] The proposed business model and payer are hypotheses unless supported by direct evidence.
- [ ] MVP scope is narrow, testable and linked to the primary user outcome.
- [ ] Out-of-scope features and non-goals are explicit.
- [ ] Critical unknowns, adoption barriers, switching costs and operational dependencies are recorded.
- [ ] No interviews, customer commitments, demand, willingness-to-pay or market facts are invented or implied without evidence.

**Reviewer notes / evidence / required changes:**

## 2. Evidence quality and claim traceability

- [ ] Material claims are listed in the evidence register and linked to the decision they inform.
- [ ] Each claim is correctly classified as owner fact, sourced fact candidate, assumption, hypothesis, recommendation or unknown.
- [ ] Source identity, URL or owner-provided evidence, publisher, publication date and access date are recorded where applicable.
- [ ] Sources are primary or authoritative where reasonably available; secondary and anecdotal evidence is labelled as such.
- [ ] Sources are current enough for volatile claims such as competitors, prices, laws, vendor limits and market conditions.
- [ ] The source actually supports the claim; the reviewer has checked the relevant passage, not just the title or search snippet.
- [ ] Geography, customer segment, date range and definitions match the claim being made.
- [ ] Conflicting, missing, inaccessible or paywalled evidence and source limitations are disclosed.
- [ ] Estimates and extrapolations show their method and uncertainty.
- [ ] No fabricated citations, interviews, statistics, legal conclusions or customer validation are present.
- [ ] Model-extracted excerpts are checked against the original source; excerpt traceability is not treated as proof of correct interpretation.

**Reviewer notes / evidence / required changes:**

## 3. Architecture and product boundaries

- [ ] The domain model reflects this product's actual entities, relationships and lifecycle; no universal tenant or ownership field is assumed.
- [ ] The authoritative ownership root and ownership graph are explicit, including shared, delegated and cross-organization access where relevant.
- [ ] Authentication, membership, roles and authorization are distinguished.
- [ ] Every sensitive read and write has a defined server-side authorization boundary; client-side hiding is not treated as security.
- [ ] Cross-tenant / cross-owner denial cases and privilege-escalation cases have explicit test scenarios.
- [ ] Data classification, minimization, retention, deletion, export and audit requirements are documented.
- [ ] Personal, financial, identity and other sensitive data are identified; unnecessary collection is excluded.
- [ ] Integrations and external trust boundaries are listed, including data sent, purpose, permissions and failure behavior.
- [ ] Localization covers language, script direction, dates, time zones, currency, number formats and jurisdiction-specific behavior as applicable.
- [ ] Persistence, migrations, consistency, idempotency and concurrency expectations are described.
- [ ] Backup, restore, monitoring, incident handling, support and operational ownership are addressed.
- [ ] Test strategy includes unit, integration, authorization, abuse, migration, recovery and acceptance tests as appropriate.
- [ ] Architecture decisions identify alternatives, trade-offs, assumptions and unresolved choices.
- [ ] No product repository, cloud resource, provider, credential or production data is accessed as part of this read-only review.

**Reviewer notes / evidence / required changes:**

## 4. Cost, dependencies and feasibility

- [ ] Every required service, provider, runtime, database, domain, email/SMS/WhatsApp channel and operational dependency is listed.
- [ ] Free-tier claims are checked against current official vendor documentation and dated.
- [ ] Limits, inactivity pauses, quotas, backup/restore limits, retention, support and overage behavior are recorded.
- [ ] The design distinguishes free-to-start from free-to-operate; hidden operational and human costs are included.
- [ ] Expected usage assumptions and low / expected / high scenarios are stated.
- [ ] Recurring costs, variable costs, payment fees, taxes and currency assumptions are disclosed where known.
- [ ] Migration, lock-in, data export and exit costs are considered.
- [ ] A safe fallback exists for unavailable, paused, quota-limited or discontinued dependencies.
- [ ] Development defaults to no provider calls and zero spend; any proposed exception is separately scoped and requires explicit owner approval.
- [ ] Unknown pricing or account-specific eligibility is marked UNKNOWN, not guessed.

**Reviewer notes / evidence / required changes:**

## 5. Security, privacy and abuse review

- [ ] Assets, trust boundaries, threat actors and likely abuse cases are identified.
- [ ] Authentication and authorization decisions are server-enforced and deny by default.
- [ ] Tenant/owner isolation, object-level access and indirect reference attacks are considered.
- [ ] Secrets are not placed in source, logs, fixtures, prompts, issues or public artifacts.
- [ ] Input validation, output encoding, file upload, parsing and injection risks are considered.
- [ ] AI-specific risks include prompt injection, untrusted retrieved content, data leakage, unsafe tool use and model overreach where applicable.
- [ ] Sensitive data sent to any external service is minimized and requires separate approval.
- [ ] Logging and audit records avoid unnecessary personal data and secrets.
- [ ] Retention, deletion, backup, restore and incident response are defined at an appropriate level.
- [ ] Dependency and supply-chain risks, update strategy and vulnerability handling are addressed.
- [ ] Security claims are supported by tests or independent evidence; a document review is not called a security certification.
- [ ] Critical unresolved security gaps are blockers, not accepted silently as future work.

**Reviewer notes / evidence / required changes:**

## 6. Decision and next-phase boundary

- [ ] The review decision is explicit: ACCEPT FOR NEXT HUMAN REVIEW, REVISE or BLOCKED.
- [ ] Every condition, unresolved question and accepted risk has an owner and follow-up.
- [ ] The proposed next phase names exact deliverables, files/repositories, acceptance criteria and exclusions.
- [ ] The next phase states whether it is read-only or changes files, and identifies any external side effects.
- [ ] Provider, model, credential, billing, infrastructure, production-data, deployment and public-launch needs are separately identified.
- [ ] Any spend has an explicit amount, currency, period, cap and owner approval requirement; no spend is implied by this checklist.
- [ ] Approval for one phase is not interpreted as approval for later phases or broader scope.
- [ ] The lifecycle manifest and validator outputs are treated as records and structural checks, not authenticated authorization.
- [ ] No implementation or external action begins until the owner gives a separate, explicit approval for the exact bounded phase.

**Final rationale and conditions:**

## Review outcome definitions

- **ACCEPT FOR NEXT HUMAN REVIEW** — This review's stated scope is sufficiently addressed to proceed to the next human review checkpoint only. It does not authorize implementation or spending.
- **REVISE** — The package is potentially viable but requires named corrections before another review.
- **BLOCKED** — A critical unknown, evidence gap, architecture/security concern or unacceptable dependency prevents progression.

## Important limitations

This checklist is a human aid, not a formal audit standard, legal opinion, penetration test, security certification, market validation or guarantee of product success. Review quality depends on reviewer competence, source quality and the completeness of the supplied artifacts. A completed checklist does not authenticate the reviewer or create machine-enforceable approval.
