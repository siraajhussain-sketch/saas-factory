# Product Brief

**Status:** Synthetic example
**Product name:** Workshop Queue
**Owner:** Example product owner
**Last updated:** 2026-11-26

## 1. Summary

Workshop Queue is a hypothetical web application that helps independent vehicle repair workshops track jobs from vehicle check-in through promised collection. It is an example used only to test the SaaS Factory's intake and review workflow.

## 2. Problem and customer

- Target buyer: Owner of an independent vehicle repair workshop
- Primary users: Service advisor and workshop manager
- Problem being solved: Job status and promised collection details are currently scattered across paper notes and chat messages
- Current alternatives: Paper job cards, spreadsheets and general messaging apps
- Why this product should exist: A focused job board may make current work and customer commitments easier to see

## 3. Geography and operating context

- Initial market: Hypothetical single-city pilot; country not selected
- Applicable jurisdictions: UNKNOWN
- Languages: English for this synthetic example; localization requirements UNKNOWN
- Currency and timezone requirements: To be selected with the pilot market

## 4. Core workflows

A service advisor records a vehicle and customer contact, opens a repair job, records the promised collection date and current status, and updates the job as work progresses. A workshop manager views open, delayed and completed jobs. Customer notifications are out of scope for this example.

## 5. Data and privacy

- Data categories: Customer contact details, vehicle identifiers, job descriptions, status and promised dates
- Personal or sensitive data: Customer contact details may be personal data; jurisdiction-specific classification is UNKNOWN
- Data ownership: The workshop is the intended business data controller; contractual roles require review
- Retention and deletion expectations: UNKNOWN; define before any real pilot
- Export and audit requirements: CSV export and a history of job status changes are proposed

## 6. Tenant and authorization model

- Ownership root: Workshop organization
- Membership relationships: A user may be a member of one or more workshop organizations; this is a hypothesis to validate
- Roles and permissions: Workshop owner, manager and service advisor
- Resource ownership graph: Workshop owns jobs; each job belongs to one workshop and may reference a customer and vehicle record
- Cross-organization or delegated access: No cross-workshop access is intended
- Administrative access model: Support access is disabled by default and requires a separately reviewed process

## 7. Business model and cost constraints

- Pricing hypothesis: Monthly subscription per workshop
- Billing requirements: Deferred until demand and pricing are validated
- External providers: None required for the synthetic prototype
- Zero-cost alternatives: Local development, synthetic data and standard-library tests
- Maximum approved development spend: USD 0 for this exercise

## 8. Non-functional requirements

- Security: Server-side authorization and tests that deny cross-workshop access
- Availability: No service-level commitment is proposed for the hypothetical MVP
- Performance: Common job-board actions should feel responsive on a modest mobile connection
- Backup and recovery: Backup and restore design is required before a real pilot
- Accessibility: Keyboard-operable controls and readable status indicators
- Localization: Locale, currency and timezone behavior must be selected for the actual market

## 9. MVP boundaries

- Included: Workshop profile, user membership, vehicle and customer references, repair jobs, job status, promised collection date and a basic job board
- Explicitly excluded: Payments, parts inventory, accounting, customer messaging, AI features and multi-branch analytics
- Deferred: Integrations, automated reminders and advanced reporting

## 10. Risks and open questions

Demand, willingness to pay, existing workshop workflows, local privacy obligations, data retention, mobile usability and the preferred ownership model remain UNKNOWN. The example does not contain customer interviews or market evidence.

## 11. Acceptance criteria

The synthetic case contains a structurally valid brief, discovery report, architecture package, evidence register and lifecycle manifest. The read-only case checker can verify their linkage and hashes. A human reviewer can identify unsupported assumptions and decisions still needed.
