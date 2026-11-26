"""Read-only structural checks for a product intake brief.

A passing result means the brief is ready for discovery review, not that its
claims are true or that any implementation work is authorized.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_HEADINGS = [
    "1. Summary",
    "2. Problem and customer",
    "3. Geography and operating context",
    "4. Core workflows",
    "5. Data and privacy",
    "6. Tenant and authorization model",
    "7. Business model and cost constraints",
    "8. Non-functional requirements",
    "9. MVP boundaries",
    "10. Risks and open questions",
    "11. Acceptance criteria",
]
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$")
INSTRUCTIONAL_TEXT = re.compile(
    r"(?i)(describe the product|describe the painful job|list the smallest set|"
    r"list assumptions that require|define measurable outcomes|"
    r"\[insert[^\]]*\]|\[to be completed\]|\bTODO\b|\bTBD\b)"
)
BLANK_FIELD = re.compile(r"^\s*(?:-\s*)?(?:\*\*)?([A-Za-z][A-Za-z /()_-]*?)(?:\*\*)?:\s*(?:\*\*)?\s*$")
class BriefValidationError(ValueError):
    """Raised when an intake brief is structurally incomplete."""


def read_brief(path: str | Path) -> str:
    try:
        content = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise BriefValidationError(
            f"brief: cannot read UTF-8 document ({type(exc).__name__})"
        ) from exc
    if not content.strip():
        raise BriefValidationError("brief: document is empty")
    return content


def validate_brief(content: str) -> dict:
    if not isinstance(content, str) or not content.strip():
        raise BriefValidationError("brief: document is empty")

    headings = {
        match.group(1).strip()
        for line in content.splitlines()
        if (match := HEADING.match(line))
    }
    missing = [heading for heading in REQUIRED_HEADINGS if heading not in headings]
    if missing:
        raise BriefValidationError(
            "brief: missing required sections: " + ", ".join(missing)
        )

    if INSTRUCTIONAL_TEXT.search(content):
        raise BriefValidationError("brief: template instructions or unfinished placeholders remain")

    for line_number, line in enumerate(content.splitlines(), start=1):
        match = BLANK_FIELD.match(line)
        if match:
            field = match.group(1).strip()
            raise BriefValidationError(
                f"brief: field '{field}' is blank on line {line_number}; use UNKNOWN if undecided"
            )

    return {
        "status": "READY_FOR_DISCOVERY_REVIEW",
        "checks": {
            "required_sections": "complete",
            "template_instructions": "none",
            "blank_labeled_fields": "none",
            "unknown_values_allowed": True,
        },
        "limitations": [
            "Structural completeness only; claims, evidence, feasibility, legal matters, security and costs are not verified.",
            "This result is not owner approval and does not authorize implementation, spending, provisioning, credentials, production data or deployment.",
        ],
        "side_effects": False,
        "provider_calls": 0,
        "spend_usd": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check a product brief locally without executing product work."
    )
    parser.add_argument("--brief", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not args.dry_run:
        print("BLOCKED: --dry-run is required; execution is not implemented.", file=sys.stderr)
        return 2
    try:
        result = validate_brief(read_brief(args.brief))
        print(json.dumps(result, indent=2))
        return 0
    except BriefValidationError as exc:
        print(json.dumps({
            "status": "BLOCKED_BRIEF_VALIDATION",
            "reason": str(exc),
            "side_effects": False,
            "provider_calls": 0,
            "spend_usd": 0,
        }, indent=2))
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
