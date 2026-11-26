# Review Findings and Remediation Tracker

## Purpose

The review tracker records findings from a product-case review and makes follow-up visible. It is a local, read-only data contract and validator. It does not assign work, send notifications, change lifecycle state, close findings, authenticate a reviewer or authorize execution.

## Safety model

- A review record is data, not proof that a human review occurred.
- The included Workshop Queue record is an assistant-generated preliminary desk assessment. `human_review_completed` is explicitly false.
- Reviewer and owner labels are descriptive strings, not authenticated identities.
- Finding states such as `claimed_resolved` and `accepted_risk` are unverified claims. The validator never upgrades them to verified.
- A valid record does not authorize implementation, spending, provisioning, credentials, production-data access or deployment.
- The validator reads the record, lifecycle manifest and referenced product-case artifacts only. It requires `--dry-run`.

## Record contract

A version 1.0 record contains:

- Case and product IDs matching the lifecycle manifest.
- An explicit assessment type, creation timestamp, summary and recommendation.
- `human_review_completed: false` and `authorization_granted: false` for the assistant-generated sample.
- A `reviewed_artifacts` list binding the assessment to the exact IDs and SHA-256 hashes of the four core artifacts.
- A non-empty list of findings with unique IDs, category, severity, title, basis, status, owner label, next action, optional target date and optional resolution note.
- Exact field sets at the record, reviewed-artifact and finding levels; unknown or missing fields are rejected.
- A timezone-aware creation timestamp that cannot predate the linked product case.

Supported finding categories: `discovery`, `evidence`, `architecture`, `cost`, `security_privacy`, `phase_boundary`.

Supported severities: `critical`, `high`, `medium`, `low`.

Supported statuses:

- `open`
- `in_progress`
- `claimed_resolved`
- `deferred`
- `accepted_risk`
- `blocked`

A resolution note is required for `claimed_resolved` and `accepted_risk`. These labels remain claims; no verification workflow is implemented.

## Validate locally

From the repository root:

```bash
python -m control_plane.review_tracker \
  --record examples/lifecycle/workshop-queue/review-tracker.json \
  --manifest examples/lifecycle/sample-case.json \
  --root examples/lifecycle \
  --dry-run
```

Expected status for the committed fixture: `REVIEW_TRACKER_STRUCTURALLY_VALID_FOR_FOLLOW_UP`.

## What validation establishes

- The existing lifecycle manifest and linked product case pass their current structural checks.
- The record identifies the same case and product.
- The record's reviewed artifact IDs and hashes exactly match the current Product Brief, discovery report, architecture package and evidence register.
- Finding identifiers, categories, severities, statuses, required text and strict `YYYY-MM-DD` date formats are structurally valid.
- Unknown fields are rejected, and the review record's creation timestamp cannot predate the product case.

## What validation does not establish

- That a human reviewed or agreed with the assessment.
- That a finding is factually correct, complete or appropriately prioritized.
- That a remediation action was performed or its outcome is safe.
- That a `claimed_resolved` finding is actually resolved.
- That an accepted risk was accepted by an authenticated, authorized person.
- That the product is viable, compliant, secure or ready to build.
- That any implementation, spending, provisioning or release is authorized.

## Operational limitations and future design questions

This is a version-controlled file format, not a task-management system. It has no authenticated assignment, notifications, due-date scheduler, atomic updates, concurrency control, immutable audit ledger, reviewer signature, approval revocation or independent remediation verification. Those capabilities must not be inferred from a passing validator result.

Before introducing any connected workflow, separately design authenticated identities, immutable review scope, evidence retention, reviewer independence, change history, concurrency handling and explicit owner approval. Keep the executor and all external side effects disabled.
