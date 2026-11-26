# Product Brief Validator

## Purpose

A deterministic local check that an intake brief is structurally complete before Phase 2 discovery begins.

## Invocation

```bash
python -m control_plane.product_brief_validator --brief path/to/PRODUCT_BRIEF.md --dry-run
```

The command reads one UTF-8 Markdown file and prints a JSON result. `--dry-run` is mandatory. The validator does not write files, access the network, invoke a model, inspect credentials, create approvals or execute product work.

## Checks

- All eleven required Product Brief sections are present with their expected headings.
- Obvious template instructions and unfinished placeholders are absent.
- Labeled fields are not left blank; use `UNKNOWN` when a decision or fact is not yet known.
- Explicit `UNKNOWN`, `Not applicable`, `N/A`, `None` and `Deferred` values are accepted.

## Passing result

`READY_FOR_DISCOVERY_REVIEW` means only that the brief is structurally ready for a human to begin discovery. It does not verify claims, evidence, feasibility, market demand, legal requirements, security, architecture or cost estimates. It is not owner approval and grants no implementation, spending, provisioning, credential, production-data or deployment permission.

## Limitations

This is a lightweight Markdown structure check, not a general Markdown parser or a quality assessment. Human review remains mandatory.
