"""Read-only completeness checks for Phase 2 discovery packages.

This validator checks document structure and obvious unfinished placeholders.
It cannot establish that claims are true, sources are credible, or a product is viable.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_HEADINGS = {
    "discovery": [
        "1. Executive assessment", "2. Buyer and user", "3. Problem and workflows",
        "4. Alternatives and competition", "5. Market and geography",
        "6. Business model hypotheses", "7. MVP boundary", "8. Risks and unknowns",
        "9. Recommendation and next decision",
    ],
    "architecture": [
        "1. Context and quality attributes", "2. Domain model",
        "3. Ownership and authorization", "4. Data and privacy",
        "5. Application and persistence design", "6. Integrations and dependencies",
        "7. Localization and financial correctness", "8. Security and threat model",
        "9. Operations", "10. Test and acceptance strategy",
        "11. Architecture decisions", "12. Open decisions and risks",
        "13. Implementation phase proposal",
    ],
    "evidence": ["Evidence types", "Confidence guidance", "Rules"],
}
PLACEHOLDERS = re.compile(
    r"(?i)(\bTODO\b|\bTBD\b|\[insert[^\]]*\]|\[to be completed\]|"
    r"\bdescribe the painful job\b|\blist the smallest\b|\bstate what the evidence supports\b)"
)
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$")
URL = re.compile(r"https?://[^\s|)]+", re.I)


class PackageValidationError(ValueError):
    """Raised when a Phase 2 package cannot pass structural checks."""


def read_document(path: str | Path, label: str) -> str:
    try:
        content = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise PackageValidationError(f"{label}: cannot read UTF-8 document ({type(exc).__name__})") from exc
    if not content.strip():
        raise PackageValidationError(f"{label}: document is empty")
    return content


def validate_document(content: str, label: str, kind: str) -> list[str]:
    if kind not in REQUIRED_HEADINGS:
        raise PackageValidationError(f"unsupported document kind: {kind}")
    headings = {match.group(1).strip() for line in content.splitlines() if (match := HEADING.match(line))}
    missing = [heading for heading in REQUIRED_HEADINGS[kind] if heading not in headings]
    if missing:
        raise PackageValidationError(f"{label}: missing required sections: {', '.join(missing)}")
    if PLACEHOLDERS.search(content):
        raise PackageValidationError(f"{label}: unfinished placeholder text remains")
    return []


def validate_evidence_rows(content: str) -> int:
    rows = []
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or stripped.count("|") < 3:
            continue
        if re.fullmatch(r"[|\s:-]+", stripped):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells and cells[0].lower() != "id":
            rows.append(cells)
    if not rows:
        raise PackageValidationError("evidence: add at least one evidence or explicitly recorded assumption row")
    for index, cells in enumerate(rows, start=1):
        if len(cells) < 11 or any(not cell for cell in cells):
            raise PackageValidationError(f"evidence: row {index} must fill all 11 register columns")
        evidence_type = cells[2].lower()
        if evidence_type not in {"primary source", "secondary source", "anecdotal", "owner-provided", "assumption"}:
            raise PackageValidationError(f"evidence: row {index} has an unrecognized evidence type")
        source = cells[3].lower()
        if evidence_type in {"primary source", "secondary source", "anecdotal"} and not URL.search(cells[3]):
            raise PackageValidationError(f"evidence: row {index} needs a source URL")
        if evidence_type == "owner-provided" and not source:
            raise PackageValidationError(f"evidence: row {index} needs provenance")
    return len(rows)


def validate_package(discovery: str, architecture: str, evidence: str) -> dict:
    validate_document(discovery, "discovery", "discovery")
    validate_document(architecture, "architecture", "architecture")
    validate_document(evidence, "evidence", "evidence")
    evidence_count = validate_evidence_rows(evidence)
    return {
        "status": "READY_FOR_HUMAN_REVIEW",
        "checks": {
            "discovery_sections": "complete",
            "architecture_sections": "complete",
            "evidence_register": "complete",
            "evidence_rows": evidence_count,
            "obvious_placeholders": "none",
        },
        "limitations": [
            "Structural completeness only; no claim, source, market, legal, security, or cost fact is verified.",
            "This result is not owner approval and does not authorize implementation, spending, provisioning, credentials, or deployment.",
        ],
        "side_effects": False,
        "provider_calls": 0,
        "spend_usd": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check a Phase 2 package locally without executing product work.")
    parser.add_argument("--discovery", required=True)
    parser.add_argument("--architecture", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not args.dry_run:
        print("BLOCKED: --dry-run is required; execution is not implemented.", file=sys.stderr)
        return 2
    try:
        result = validate_package(
            read_document(args.discovery, "discovery"),
            read_document(args.architecture, "architecture"),
            read_document(args.evidence, "evidence"),
        )
        print(json.dumps(result, indent=2))
        return 0
    except PackageValidationError as exc:
        print(json.dumps({
            "status": "BLOCKED_PACKAGE_VALIDATION",
            "reason": str(exc),
            "side_effects": False,
            "provider_calls": 0,
            "spend_usd": 0,
        }, indent=2))
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
