"""Read-only cross-artifact consistency checks for one product case."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from control_plane.lifecycle_manifest import (
    ManifestValidationError,
    read_manifest,
    read_artifact_snapshots,
    validate_manifest,
)
from control_plane.phase2_validator import (
    PackageValidationError,
    validate_package,
)
from control_plane.product_brief_validator import (
    BriefValidationError,
    validate_brief,
)

REQUIRED_KINDS = {
    "product_brief",
    "discovery_report",
    "architecture_package",
    "evidence_register",
}


class CaseConsistencyError(ValueError):
    """Raised when a product case's linked artifacts are incomplete or inconsistent."""


def validate_case(manifest: Any, root: str | Path) -> dict:
    """Validate one manifest and re-run read-only structural checks on its core artifacts."""
    # Capture every declared artifact exactly once. Hash verification and all
    # downstream structural checks must consume these same immutable bytes.
    snapshots = read_artifact_snapshots(manifest, root)
    manifest_result = validate_manifest(manifest, root, artifact_snapshots=snapshots)
    artifacts = manifest["artifacts"]
    by_kind: dict[str, list[dict]] = {}
    for artifact in artifacts:
        kind = artifact["kind"]
        by_kind.setdefault(kind, []).append(artifact)

    missing = sorted(REQUIRED_KINDS - set(by_kind))
    if missing:
        raise CaseConsistencyError(
            "case package is missing required artifact kinds: " + ", ".join(missing)
        )
    duplicates = sorted(kind for kind in REQUIRED_KINDS if len(by_kind.get(kind, [])) != 1)
    if duplicates:
        raise CaseConsistencyError(
            "case package must contain exactly one artifact of each required kind; duplicates: "
            + ", ".join(duplicates)
        )

    contents: dict[str, str] = {}
    artifact_summary = []
    for kind in sorted(REQUIRED_KINDS):
        artifact = by_kind[kind][0]
        try:
            contents[kind] = snapshots[artifact["id"]].decode("utf-8")
        except UnicodeError as exc:
            raise CaseConsistencyError(
                f"artifact {artifact['id']}: snapshot is not valid UTF-8 text"
            ) from exc
        artifact_summary.append({
            "id": artifact["id"],
            "kind": kind,
            "sha256": artifact["sha256"],
        })

    try:
        brief_result = validate_brief(contents["product_brief"])
    except BriefValidationError as exc:
        raise CaseConsistencyError(f"product_brief: {exc}") from exc

    try:
        package_result = validate_package(
            contents["discovery_report"],
            contents["architecture_package"],
            contents["evidence_register"],
        )
    except PackageValidationError as exc:
        raise CaseConsistencyError(f"Phase 2 package: {exc}") from exc

    return {
        "status": "CASE_PACKAGE_READY_FOR_HUMAN_REVIEW",
        "case_id": manifest_result["case_id"],
        "product_id": manifest_result["product_id"],
        "lifecycle_state": manifest_result["lifecycle_state"],
        "artifacts": artifact_summary,
        "checks": {
            "manifest_and_artifact_hashes": "valid",
            "artifact_snapshot_reuse": "same_bytes_hashed_and_structurally_validated",
            "required_artifact_kinds": "complete",
            "artifact_kind_cardinality": "exactly_one_each",
            "product_brief_structure": brief_result["status"],
            "discovery_architecture_evidence_structure": package_result["status"],
            "recorded_validator_run_count": len(manifest.get("validator_runs", [])),
            "recorded_validator_runs_are_historical_only": True,
            "all_artifacts_linked_by_same_manifest": True,
        },
        "limitations": [
            "Artifacts are grouped by this manifest; the checker cannot prove they were authored for the same real-world product or case.",
            "Artifact hashes prove byte identity only. They do not prove factual accuracy, source quality, interpretation, architecture correctness or security.",
            "The brief and Phase 2 structural validators are rerun, but prior validator-run records are historical, unauthenticated claims.",
            "Human review labels and lifecycle states are not authenticated and do not constitute approval.",
            "This result is not authorization to modify repositories, spend money, provision services, access production data, execute code or deploy.",
        ],
        "side_effects": False,
        "provider_calls": 0,
        "spend_usd": 0,
        "authorization_granted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check one product case's linked artifacts locally without executing work."
    )
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--root", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not args.dry_run:
        print("BLOCKED: --dry-run is required; execution is not implemented.", file=sys.stderr)
        return 2
    try:
        result = validate_case(read_manifest(args.manifest), args.root)
        print(json.dumps(result, indent=2))
        return 0
    except (ManifestValidationError, CaseConsistencyError) as exc:
        print(json.dumps({
            "status": "BLOCKED_CASE_CONSISTENCY",
            "reason": str(exc),
            "side_effects": False,
            "provider_calls": 0,
            "spend_usd": 0,
            "authorization_granted": False,
        }, indent=2))
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
