# Phase 2 Package Validator

## Purpose

A deterministic local check for the three required Phase 2 documents: discovery report, architecture package and evidence register.

## Invocation

```bash
python -m control_plane.phase2_validator \
  --discovery path/to/DISCOVERY_REPORT.md \
  --architecture path/to/ARCHITECTURE_PACKAGE.md \
  --evidence path/to/EVIDENCE_REGISTER.md \
  --dry-run
```

The command reads UTF-8 Markdown files and prints a JSON result. It does not write files, access the network, invoke a model, inspect credentials, create approvals or execute product work. `--dry-run` is mandatory.

## Checks

- Required section headings exist in all three documents.
- Obvious unfinished placeholders are absent.
- The evidence register contains at least one complete row.
- Evidence types use the documented vocabulary.
- Primary, secondary and anecdotal evidence rows contain a source URL.
- All evidence rows populate the eleven register columns.

## What a pass means

`READY_FOR_HUMAN_REVIEW` means only that the package is structurally complete enough for a person to review. The validator does not verify sources, dates, claims, legal conclusions, market demand, security quality, architecture correctness or cost estimates. An assumption row is acceptable when clearly labelled; it is not treated as proof.

A passing result is not owner approval and grants no implementation, spending, provisioning, credential, production-data or deployment permission.

## Limitations

The Markdown table parser is intentionally simple and expects ordinary pipe-delimited rows. It is not a general Markdown parser. Human review remains mandatory.
