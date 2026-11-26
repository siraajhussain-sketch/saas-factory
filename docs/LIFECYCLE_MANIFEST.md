# Lifecycle Manifest and State Contract

**Status:** Read-only local contract, version 1.0  
**Purpose:** Tie a product case's source artifacts, validator records, human review notes and lifecycle history together without creating an approval or execution mechanism.

## 1. Safety boundary

The manifest is a traceability record, not a trusted control plane. A value such as `accepted`, `OWNER_REVIEW` or `RELEASE_REVIEW` is only data supplied by whoever edits the JSON. The validator does not authenticate a reviewer, prove that a review occurred, rerun recorded validators, approve work, or authorize any side effect.

The command requires `--dry-run`. It reads the manifest and referenced files only. It makes no network or provider calls and writes no files.

## 2. Manifest shape

A version 1.0 manifest contains:

- `schema_version`: exact contract version.
- `case_id`, `product_id`: stable lowercase identifiers.
- `lifecycle_state`: current state, which must equal the final state-history entry.
- `created_at`, `updated_at`: ISO--8601 timestamps with timezone.
- `artifacts`: unique IDs, artifact kind, root-relative path and SHA-256 digest.
- `validator_runs`: unique run IDs, validator name, recorded status/time and artifact IDs.
- `human_reviews`: unique review IDs, stage, reviewer label, decision, timestamp and notes.
- `state_history`: sequence of permitted state transitions, with reason and timestamp.

See `examples/lifecycle/sample-case.json` for a minimal fixture. The referenced artifact is synthetic.

## 3. Lifecycle states

The allowed forward sequence is:

`INTAKE → DISCOVERY → ARCHITECTURE → OWNER_REVIEW → IMPLEMENTATION_PLANNING → IMPLEMENTATION → ACCEPTANCE → RELEASE_REVIEW → RELEASED`

A case may be closed from any non-terminal state. This validator checks the recorded sequence only; it does not decide whether evidence or approvals required to advance a stage are sufficient. In particular, `OWNER_REVIEW` is not approval, and reaching `IMPLEMENTATION` does not authorize code changes.

## 4. Validation performed

- Strict schema-version and required-field checks.
- Unique, bounded identifiers and supported status/decision values.
- Timezone-aware ISO-8601 timestamps.
- Unique artifact, validator-run and review IDs.
- Artifact paths must be relative, remain under the supplied root, contain no parent traversal or symlink component, and resolve to regular files.
- SHA-256 digest verification for every referenced artifact.
- Validator runs may reference only declared artifact IDs.
- State history must start at `INTAKE`, follow the allowed sequence and end at the declared current state.
- Duplicate JSON object keys and non-standard numeric constants are rejected.

## 5. Run locally

```bash
python -m control_plane.lifecycle_manifest \
  --manifest examples/lifecycle/sample-case.json \
  --root examples/lifecycle \
  --dry-run
```

A successful result is `STRUCTURALLY_VALID_FOR_HUMAN_REVIEW`. A failure is `BLOCKED_LIFECYCLE_VALIDATION`.

## 6. Important limitations

- Hashes establish byte identity, not truth, completeness, safety or quality.
- Validator-run entries are historical records; this command does not rerun validators or verify output logs.
- Reviewer labels and decisions are not authenticated.
- The manifest is not a durable audit ledger and does not prevent edits, replay or concurrent updates.
- The file-based format does not provide atomic state transitions or access control.
- This is not an authorization service, approval signer, executor, repository provisioner or release system.

## 7. Next review

Before connecting stages or automating state changes, separately review the human checklist, immutable artifact/version strategy, authenticated decision evidence, concurrency and audit requirements. Keep execution blocked until critical approval-service gaps are independently resolved and the owner explicitly approves a bounded implementation phase.
