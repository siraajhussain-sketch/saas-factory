# Synthetic End-to-End Product Case Walkthrough

## Purpose

This fixture exercises the factory's current read-only intake-to-review path using a fictional product named **Workshop Queue**. It is deliberately not market research and contains no real customer data.

The example is intended to prove that the artifacts can be linked, their byte hashes checked, and the existing structural validators rerun together. It does not prove that the product is viable, that assumptions are true, or that the architecture is safe to implement.

## Fixture layout

The lifecycle root is `examples/lifecycle/`.

- `sample-case.json` — lifecycle manifest for case `workshop-queue-demo-001`.
- `workshop-queue/product-brief.md` — fictional intake brief.
- `workshop-queue/discovery-report.md` — discovery draft with assumptions clearly identified.
- `workshop-queue/architecture-package.md` — product-specific architecture draft and unresolved decisions.
- `workshop-queue/evidence-register.md` — synthetic assumptions only; no sources or interviews are fabricated.

The manifest records a SHA-256 digest for each artifact. The consistency checker validates every digest before it reads the Markdown documents.

## Run from the repository root

All commands are local, read-only and require `--dry-run`.

### 1. Product Brief intake

```bash
python -m control_plane.product_brief_validator \
  --brief examples/lifecycle/workshop-queue/product-brief.md \
  --dry-run
```

Expected status: `READY_FOR_DISCOVERY_REVIEW`.

### 2. Discovery, architecture and evidence structure

```bash
python -m control_plane.phase2_validator \
  --discovery examples/lifecycle/workshop-queue/discovery-report.md \
  --architecture examples/lifecycle/workshop-queue/architecture-package.md \
  --evidence examples/lifecycle/workshop-queue/evidence-register.md \
  --dry-run
```

Expected status: `READY_FOR_HUMAN_REVIEW`.

### 3. Lifecycle manifest and file integrity

```bash
python -m control_plane.lifecycle_manifest \
  --manifest examples/lifecycle/sample-case.json \
  --root examples/lifecycle \
  --dry-run
```

Expected status: `STRUCTURALLY_VALID_FOR_HUMAN_REVIEW`.

### 4. Combined case consistency check

```bash
python -m control_plane.case_consistency \
  --manifest examples/lifecycle/sample-case.json \
  --root examples/lifecycle \
  --dry-run
```

Expected status: `CASE_PACKAGE_READY_FOR_HUMAN_REVIEW`.

The combined checker reruns the Product Brief and Phase 2 validators. The separate commands above are useful when diagnosing which stage is incomplete.

### 5. Automated regression test

```bash
python -m unittest discover -s tests -v
```

The test suite includes a regression test that loads the committed synthetic fixture and runs the combined checker. GitHub Actions runs this standard-library test suite on changes to the control plane and tests.

## Expected human-review outcome

A human reviewer should not accept the synthetic package as product evidence. In particular:

- Buyer, workflow frequency, urgency, alternatives and willingness to pay are unverified.
- No target geography has been selected.
- Privacy and legal obligations have not been assessed for a jurisdiction.
- Ownership and membership choices remain hypotheses.
- No persistence, identity, hosting or external provider has been selected.
- No implementation phase is approved.

A realistic next step for an actual product would be to replace the fictional brief with owner-supplied facts, research current sources, record real interviews only if conducted, and then have reviewers assess the evidence and architecture.

### 6. Preliminary review findings and remediation tracking

```bash
python -m control_plane.review_tracker \
  --record examples/lifecycle/workshop-queue/review-tracker.json \
  --manifest examples/lifecycle/sample-case.json \
  --root examples/lifecycle \
  --dry-run
```

Expected status: `REVIEW_TRACKER_STRUCTURALLY_VALID_FOR_FOLLOW_UP`.

The committed record is an assistant-generated preliminary desk assessment, not a human review. It binds itself to the exact hashes of the four core case artifacts and lists six illustrative findings. It does not add a human review to the lifecycle manifest, close findings, authenticate an owner or authorize work. Claimed remediation remains unverified.

## Editing the fixture safely

If any referenced artifact changes, update its SHA-256 value in `sample-case.json`. A hash mismatch must block the combined check. Do not manually mark the lifecycle as approved to make a check pass; lifecycle states and review records are untrusted descriptive data.

## Safety boundary

This walkthrough performs no network calls, model inference, provider integration, repository provisioning, writes to product repositories, spending, production-data access or deployment. The example is not an approval or execution test. The approval service and execution worker remain unimplemented and blocked.
