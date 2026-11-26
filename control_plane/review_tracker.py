"""Read-only validation for review findings and remediation tracking records.

Records are untrusted workflow data. This module never authenticates reviewers,
verifies remediation claims, or authorizes implementation or other side effects.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

from control_plane.case_consistency import CaseConsistencyError, validate_case
from control_plane.lifecycle_manifest import ManifestValidationError, read_manifest

SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,79}$")
SEVERITIES = {"critical", "high", "medium", "low"}
STATUSES = {"open", "in_progress", "claimed_resolved", "deferred", "accepted_risk", "blocked"}
CATEGORIES = {"discovery", "evidence", "architecture", "cost", "security_privacy", "phase_boundary"}
REQUIRED_KINDS = {"product_brief", "discovery_report", "architecture_package", "evidence_register"}


class ReviewTrackerError(ValueError):
    """Raised when a review tracker record is invalid or stale."""


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ReviewTrackerError(message)


def text_field(value: Any, field: str, limit: int = 1000) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"{field}: must be a non-empty string")
    require(len(value) <= limit, f"{field}: exceeds {limit} characters")
    return value.strip()

def exact_keys(value: Any, required: set[str], field: str) -> None:
    require(isinstance(value, dict), f"{field}: must be an object")
    missing = required - set(value)
    unknown = set(value) - required
    require(not missing, f"{field}: missing required fields: " + ", ".join(sorted(missing)))
    require(not unknown, f"{field}: unknown fields: " + ", ".join(sorted(unknown)))


def parse_timestamp(value: Any, field: str) -> datetime:
    raw = text_field(value, field, 40)
    try:
        parsed = datetime.fromisoformat(raw[:-1] + "+00:00" if raw.endswith("Z") else raw)
    except ValueError as exc:
        raise ReviewTrackerError(f"{field}: must be an ISO-8601 timestamp") from exc
    require(parsed.tzinfo is not None, f"{field}: timezone is required")
    return parsed


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ReviewTrackerError(f"review record: duplicate JSON key {key}")
        result[key] = value
    return result


def reject_constant(value: str):
    raise ReviewTrackerError(f"review record: invalid numeric constant {value}")


def read_review_record(path: str | Path) -> dict:
    try:
        with Path(path).open("r", encoding="utf-8") as handle:
            return json.load(handle, object_pairs_hook=reject_duplicate_keys, parse_constant=reject_constant)
    except ReviewTrackerError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReviewTrackerError(
            f"review record: cannot read valid UTF-8 JSON ({type(exc).__name__})"
        ) from exc


def validate_review_record(record: Any, manifest: Any, root: str | Path) -> dict:
    exact_keys(record,{"schema_version","assessment_type","human_review_completed","authorization_granted","case_id","product_id","created_at","summary","recommendation","reviewed_artifacts","findings"},"review record")
    try:
        case_result = validate_case(manifest, root)
    except (ManifestValidationError, CaseConsistencyError) as exc:
        raise ReviewTrackerError(f"case package: {exc}") from exc

    require(record.get("schema_version") == "1.0", "schema_version: unsupported version")
    require(record.get("assessment_type") == "assistant_preliminary_desk_review",
            "assessment_type: must identify a preliminary assistant desk review")
    require(record.get("human_review_completed") is False,
            "human_review_completed: must be false for this assistant-generated fixture")
    require(record.get("authorization_granted") is False,
            "authorization_granted: must be false")
    require(record.get("case_id") == case_result["case_id"], "case_id: does not match lifecycle manifest")
    require(record.get("product_id") == case_result["product_id"], "product_id: does not match lifecycle manifest")
    created = parse_timestamp(record.get("created_at"), "created_at")
    case_created = parse_timestamp(manifest.get("created_at"), "manifest.created_at")
    require(created >= case_created, "created_at: review record must not predate the product case")

    artifacts = manifest["artifacts"]
    by_kind: dict[str, list[dict]] = {}
    for artifact in artifacts:
        by_kind.setdefault(artifact["kind"], []).append(artifact)
    require(REQUIRED_KINDS.issubset(by_kind), "manifest: core reviewed artifact kinds are incomplete")
    require(all(len(by_kind[kind]) == 1 for kind in REQUIRED_KINDS),
            "manifest: each core reviewed artifact kind must occur exactly once")

    reviewed = record.get("reviewed_artifacts")
    require(isinstance(reviewed, list), "reviewed_artifacts: must be an array")
    expected = {
        item["id"]: item["sha256"]
        for kind in REQUIRED_KINDS
        for item in by_kind[kind]
    }
    supplied = {}
    for index, item in enumerate(reviewed):
        exact_keys(item,{"artifact_id","sha256"},f"reviewed_artifacts[{index}]")
        ident = text_field(item.get("artifact_id"), f"reviewed_artifacts[{index}].artifact_id", 80)
        digest = text_field(item.get("sha256"), f"reviewed_artifacts[{index}].sha256", 64)
        require(ident not in supplied, f"reviewed_artifacts: duplicate artifact {ident}")
        supplied[ident] = digest
    require(supplied == expected, "reviewed_artifacts: source artifact IDs or hashes are stale/incomplete")

    findings = record.get("findings")
    require(isinstance(findings, list) and len(findings) > 0, "findings: at least one finding is required")
    seen = set()
    counts = {status: 0 for status in STATUSES}
    for index, finding in enumerate(findings):
        prefix = f"findings[{index}]"
        exact_keys(finding,{"id","category","severity","title","basis","status","owner_label","next_action","target_date","resolution_note"},prefix)
        ident = text_field(finding.get("id"), f"{prefix}.id", 80)
        require(bool(SLUG.fullmatch(ident)), f"{prefix}.id: invalid identifier")
        require(ident not in seen, f"findings: duplicate id {ident}")
        seen.add(ident)
        category = finding.get("category")
        require(isinstance(category, str) and category in CATEGORIES,
                f"{prefix}.category: unsupported category")
        severity = finding.get("severity")
        require(isinstance(severity, str) and severity in SEVERITIES,
                f"{prefix}.severity: unsupported severity")
        status = finding.get("status")
        require(isinstance(status, str) and status in STATUSES,
                f"{prefix}.status: unsupported status")
        counts[status] += 1
        text_field(finding.get("title"), f"{prefix}.title", 200)
        text_field(finding.get("basis"), f"{prefix}.basis", 1200)
        text_field(finding.get("next_action"), f"{prefix}.next_action", 1200)
        text_field(finding.get("owner_label"), f"{prefix}.owner_label", 120)
        due = finding.get("target_date")
        if due is not None:
            require(isinstance(due, str) and bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}",due)), f"{prefix}.target_date: must be YYYY-MM-DD or null")
            try:
                date.fromisoformat(due)
            except ValueError as exc:
                raise ReviewTrackerError(f"{prefix}.target_date: must be YYYY-MM-DD") from exc
        resolution = finding.get("resolution_note")
        if status in {"claimed_resolved", "accepted_risk"}:
            text_field(resolution, f"{prefix}.resolution_note", 1200)
        elif resolution is not None:
            text_field(resolution, f"{prefix}.resolution_note", 1200)

    recommendation = record.get("recommendation")
    require(isinstance(recommendation, str) and recommendation in {
        "do_not_proceed", "revise", "ready_for_owner_decision"
    }, "recommendation: unsupported value")
    critical_count = sum(1 for finding in findings if finding.get("severity") == "critical")
    require(recommendation != "ready_for_owner_decision" or critical_count == 0,
            "recommendation: critical findings prevent ready_for_owner_decision")
    text_field(record.get("summary"), "summary", 2000)

    return {
        "status": "REVIEW_TRACKER_STRUCTURALLY_VALID_FOR_FOLLOW_UP",
        "case_id": case_result["case_id"],
        "product_id": case_result["product_id"],
        "finding_count": len(findings),
        "findings_by_status": counts,
        "reviewed_artifacts": len(reviewed),
        "human_review_completed": False,
        "authorization_granted": False,
        "side_effects": False,
        "provider_calls": 0,
        "spend_usd": 0,
        "limitations": [
            "This is an assistant-generated preliminary assessment, not a human review.",
            "Reviewer and owner labels are untrusted descriptive text, not authenticated identities.",
            "Finding status and resolution notes are claims; claimed_resolved and accepted_risk are not independently verified.",
            "Artifact hashes establish byte identity only, not truth, completeness, safety or quality.",
            "A valid record does not authorize implementation, spending, provisioning, credential use, production-data access or deployment."
        ]
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a review/remediation record locally without authorizing work.")
    parser.add_argument("--record", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--root", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not args.dry_run:
        print("BLOCKED: --dry-run is required; execution is not implemented.", file=sys.stderr)
        return 2
    try:
        result = validate_review_record(
            read_review_record(args.record),
            read_manifest(args.manifest),
            args.root,
        )
        print(json.dumps(result, indent=2))
        return 0
    except (ReviewTrackerError, ManifestValidationError, CaseConsistencyError) as exc:
        print(json.dumps({
            "status": "BLOCKED_REVIEW_TRACKER_VALIDATION",
            "reason": str(exc),
            "human_review_completed": False,
            "authorization_granted": False,
            "side_effects": False,
            "provider_calls": 0,
            "spend_usd": 0,
        }, indent=2))
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
