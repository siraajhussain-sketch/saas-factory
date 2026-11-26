# Product Architecture Package

**Product:** Workshop Queue (synthetic example)
**Version / date:** 1.0 / 2026-11-26
**Status:** DRAFT — NOT APPROVED FOR IMPLEMENTATION

## 1. Context and quality attributes

The hypothetical system provides a job board for one or more independent vehicle repair workshops. Core workflows are job intake, status updates, promised collection tracking and manager visibility. Security and cross-workshop isolation are critical. Availability targets, scale and performance budgets remain undefined until a real market and operating model are selected.

## 2. Domain model

Candidate concepts:
- Workshop: business ownership root
- User: authenticated person
- Membership: relationship between user and workshop, including role and status
- Customer: person or business associated with a workshop job
- Vehicle: vehicle reference owned within a workshop context
- RepairJob: work item, customer/vehicle references, description, status and promised collection date
- JobStatusEvent: append-oriented record of status changes, actor and timestamp

A RepairJob must belong to exactly one Workshop. Customer and Vehicle records must also be scoped to a Workshop in the initial model. Referential integrity and deletion behavior require an ADR before implementation.

## 3. Ownership and authorization

- Ownership root and rationale: Workshop organization; business records are created for a workshop
- Resource ownership graph: Workshop → Customer, Vehicle, RepairJob; RepairJob → JobStatusEvent
- Membership/delegation model: User → Membership → Workshop
- Roles and permission matrix: Owner manages workshop and members; Manager manages jobs and operational records; Service Advisor creates and updates jobs but cannot change membership
- Server-side enforcement points: Every read and write resolves an authenticated user's active membership and verifies the target resource's workshop ownership
- Administrative/support access: Disabled by default; separate audited break-glass design required
- Cross-owner isolation tests: User from Workshop A cannot read, mutate, enumerate or infer identifiers belonging to Workshop B

The role model and one-user/multiple-workshop assumption are unvalidated design hypotheses.

## 4. Data and privacy

| Data category | Personal/sensitive? | Purpose | Minimize? | Retention/deletion | Export/audit |
|---|---|---|---|---|---|
| Customer name and contact | Potentially personal | Job communication reference | Store only necessary fields | UNKNOWN; define per jurisdiction | Customer/job export |
| Vehicle registration or identifier | May identify an owner indirectly | Identify vehicle and job | Avoid unnecessary documents | UNKNOWN; define per jurisdiction | Job export |
| Repair description | May contain personal details | Explain work requested | Warn users not to enter unnecessary sensitive data | UNKNOWN | Job export |
| Job status history | May identify staff activity | Operational traceability | Record necessary transitions only | Define retention policy | Audit export |

No real data is used in this exercise. Privacy roles, lawful basis, notices, data residency and deletion obligations require jurisdiction-specific review.

## 5. Application and persistence design

A future implementation may use a web client, authenticated API and relational database with explicit workshop ownership columns and database constraints. No framework, hosting provider or database is selected. Writes should validate state transitions and use idempotency where retries can create duplicate jobs or events. Schema migrations and backup/restore strategy must be designed before a pilot.

## 6. Integrations and dependencies

No external integration is required for the synthetic MVP. Authentication, email, messaging, hosting, database and payment providers are intentionally unselected. Any future dependency requires comparison of cost, free-tier limits, data processing, outage behavior, exportability and lock-in. All providers remain disabled until separately approved.

## 7. Localization and financial correctness

The actual country, locale, currency and timezone are unknown. Store instants in a consistent UTC representation and retain the workshop's configured timezone for local display and date-based business rules. Promised collection dates should be modeled as local calendar dates when they represent a date rather than a moment. Currency is not needed in the synthetic MVP; if estimates or invoices are later introduced, use explicit currency codes and decimal-safe arithmetic.

## 8. Security and threat model

Assets include customer contact data, vehicle references, repair details, job status and user identities. Main threats include cross-workshop data access, role escalation, insecure direct object references, account takeover, abusive enumeration, accidental disclosure through logs and unauthorized support access. Mitigations include server-side membership checks, ownership constraints, least privilege, secure session handling, rate limits, minimal logging, audit events and negative cross-owner tests. A formal threat model and independent review are required before a real pilot.

## 9. Operations

Before launch, define accountable operator, monitoring, incident response, support, backup frequency, restore testing, recovery objectives, retention, deletion and export processes. No operational service or cloud resource is configured by this synthetic design.

## 10. Test and acceptance strategy

- Unit tests for job state transitions and date handling
- API authorization tests for each role
- Cross-workshop read/write denial tests
- Tests for identifier enumeration and access-control edge cases
- Migration and referential-integrity tests
- Backup restore and export verification
- Accessibility and mobile usability tests
- Failure and retry tests for job creation and status updates

## 11. Architecture decisions

No implementation ADRs are approved. Candidate decisions include ownership root, membership cardinality, relational persistence, authentication, timezone semantics, audit retention and support access. Each decision needs options, evidence, consequences and owner review.

## 12. Open decisions and risks

| Item | Options | Recommendation | Evidence | Owner decision needed? |
|---|---|---|---|---|
| Initial geography | Select one city/country or remain undecided | Select only after buyer access is understood | None; currently unknown | Yes |
| Ownership model | One workshop per user or multi-workshop membership | Keep multi-membership as a hypothesis until validated | Synthetic brief only | Yes |
| Persistence | Relational database or document database | Compare after domain and query requirements are validated | No technical benchmark | Yes |
| Support access | No support access or controlled break-glass | Default disabled; design explicit audited process | Security recommendation | Yes |
| Data retention | Fixed periods or customer-configured policy | Decide after jurisdiction and workflow review | No legal review | Yes |

## 13. Implementation phase proposal

No implementation phase is proposed for approval. A future bounded planning exercise could define a synthetic prototype scope, but a real build should wait until buyer evidence, geography, privacy obligations, ownership decisions, cost estimates and security review are complete.

**Approval statement:** Review of this package is not authorization to provision, code, spend, access production data or deploy.
