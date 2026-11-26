# Product Case Consistency Checker

## Purpose

A deterministic, local, read-only check that the core artifacts for one product case are linked through the same lifecycle manifest and pass the existing structural validators.

## Invocation

```bash
python -m control_plane.case_consistency \
  --manifest path/to/case.json \
  --root path/to/case-artifacts \
  --dry-run
```

The manifest paths must be relative to the supplied root. The checker reads the manifest and referenced UTF-8 Markdown files only. `--dry-run` is mandatory.

## Required artifact kinds

The manifest must contain exactly one artifact of each kind:

- `product_brief`
- `discovery_report`
- `architecture_package`
- `evidence_register`

Every artifact declared in the manifest is first checked by the lifecycle manifest validator for root confinement, regular-file status and SHA-256 integrity. The checker then reruns the Product Brief structural validator and the Phase 2 discovery/architecture/evidence structural validator on the four required artifacts.

Additional artifact kinds may be present, and their paths and hashes are still checked by the manifest validator.

## What a pass means

`CASE_PACKAGE_READY_FOR_HUMAN_REVIEW` means:

- The lifecycle manifest passes its structural and integrity checks.
- The four required artifact kinds are present exactly once.
- The required artifacts are linked by one manifest and their hashes match.
- The Product Brief and Phase 2 package pass their existing structural checks.

This is a readiness signal for human review only. It is not a finding that the documents describe the same real-world product, that their claims are true, or that the design is safe or viable.

## Historical validator and review records

The checker does not trust recorded validator runs as proof. It reruns the current structural validators against the current artifact bytes. Existing validator-run records are reported as historical, unauthenticated records only.

Reviewer labels, review decisions and lifecycle state are also unverified data. They do not authenticate a person, prove a review occurred, or authorize implementation.

## Safety boundary

- No network, model or provider calls.
- No writes, repository changes, execution worker, provisioning or deployment.
- No credentials or production data are accessed.
- No spend; the command requires `--dry-run`.
- A passing result explicitly reports `authorization_granted: false`.

## Limitations and next improvements

The manifest groups the artifacts, but the checker cannot prove they were authored for the same real-world product or case. Hashes prove byte identity, not factual accuracy, evidence quality, interpretation, architecture correctness or security. The checker does not rerun the full discovery research process or authenticate human decisions.

Before introducing automated lifecycle transitions, separately design immutable case identity/version metadata inside artifacts, authenticated review evidence, concurrency controls and a durable audit mechanism. Keep execution and spending blocked until the approval-service gaps are independently resolved and the owner approves a bounded phase.
