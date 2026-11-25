"""Deterministic, read-only SaaS factory request validator.

This module performs local validation only. It has no network, shell, Git,
filesystem-write, provider, deployment, or provisioning capabilities.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{1,62}$")
SHA256 = re.compile(r"^[a-f0-9]{64}$")
SIGNATURE = re.compile(r"^[a-f0-9]{64}$")
REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SECRET_KEY = re.compile(r"(secret|token|password|api[_-]?key|authorization|private[_-]?key|signature)", re.I)
SECRET_VALUE = re.compile(r"(?i)(gh[pousr]_[A-Za-z0-9_]{12,}|AIza[0-9A-Za-z_-]{20,}|sk-[A-Za-z0-9_-]{12,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)")

class ValidationError(ValueError):
    """Raised when an input violates the local policy."""

def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)

def keys(obj: dict[str, Any], required: set[str], optional: set[str] = frozenset()) -> None:
    require(isinstance(obj, dict), "expected a JSON object")
    missing = required - obj.keys()
    unknown = obj.keys() - required - optional
    require(not missing, f"missing fields: {', '.join(sorted(missing))}")
    require(not unknown, f"unknown fields: {', '.join(sorted(unknown))}")

def load_json(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read valid JSON input ({type(exc).__name__})") from exc
    require(isinstance(value, dict), "top-level JSON value must be an object")
    return value

def safe_relative_path(value: Any) -> str:
    require(isinstance(value, str) and value and not value.startswith("/"), "paths must be non-empty relative POSIX paths")
    require("\\" not in value and "\x00" not in value, "path contains an invalid character")
    # A single trailing slash denotes an allowed directory prefix.
    normalized = value[:-1] if value.endswith("/") else value
    require(normalized and not normalized.endswith("/"), "path contains an empty segment")
    parts = normalized.split("/")
    require(all(part not in ("", ".", "..") for part in parts), "path traversal or empty path segment rejected")
    require(not re.match(r"^[A-Za-z]:", value), "absolute drive paths are not permitted")
    return value

def resolve_file(root: Path, relative: str) -> Path:
    relative = safe_relative_path(relative)
    require(not relative.endswith("/"), "file path cannot end with a slash")
    base = root.resolve()
    target = (base / relative).resolve(strict=True)
    require(target.is_relative_to(base), "resolved path escapes repository root")
    require(target.is_file(), "referenced path must be a regular file")
    return target

def parse_timestamp(value: Any, field: str) -> datetime:
    require(isinstance(value, str), f"{field} must be an ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValidationError(f"{field} is invalid") from exc
    require(parsed.tzinfo is not None and parsed.utcoffset() is not None, f"{field} must include timezone")
    return parsed.astimezone(timezone.utc)

def validate_policy(policy: dict[str, Any]) -> None:
    keys(policy, {"allowed_repositories", "allowed_branches", "allowed_path_prefixes", "allowed_phases"})
    for field in ("allowed_repositories", "allowed_branches", "allowed_path_prefixes", "allowed_phases"):
        values = policy[field]
        require(isinstance(values, list) and all(isinstance(v, str) and v for v in values), f"{field} must be a list of non-empty strings")
        require(len(values) == len(set(values)), f"{field} contains duplicates")
    require(all(REPOSITORY.fullmatch(v) for v in policy["allowed_repositories"]), "policy contains an invalid repository name")
    for field in ("allowed_repositories", "allowed_branches", "allowed_path_prefixes", "allowed_phases"):
        require(policy[field], f"{field} is empty; fail closed")
    for prefix in policy["allowed_path_prefixes"]:
        require(prefix.endswith("/") and len(prefix) > 1, "path prefixes must be directory prefixes ending in /")
        safe_relative_path(prefix)

def validate_manifest(manifest: dict[str, Any], policy: dict[str, Any]) -> None:
    keys(manifest, {
        "schema_version", "product_id", "product_name", "repository", "default_branch",
        "adr_path", "adr_sha256", "requested_phase", "requested_paths",
        "provider_policy", "environment", "intent"
    })
    require(manifest["schema_version"] == "1.0", "unsupported manifest schema_version")
    require(isinstance(manifest["product_id"], str) and SAFE_ID.fullmatch(manifest["product_id"]), "invalid product_id")
    require(isinstance(manifest["product_name"], str) and 2 <= len(manifest["product_name"]) <= 120, "invalid product_name")
    require(isinstance(manifest["repository"], str) and REPOSITORY.fullmatch(manifest["repository"]), "invalid repository")
    require(manifest["repository"] in policy["allowed_repositories"], "repository is not allowlisted")
    require(manifest["default_branch"] in policy["allowed_branches"], "branch is not allowlisted")
    require(manifest["requested_phase"] in policy["allowed_phases"], "phase is not allowlisted")
    require(isinstance(manifest["adr_path"], str) and manifest["adr_path"].startswith("docs/adr/"), "adr_path must be under docs/adr/")
    safe_relative_path(manifest["adr_path"])
    require(isinstance(manifest["adr_sha256"], str) and SHA256.fullmatch(manifest["adr_sha256"]), "invalid ADR SHA-256")
    requested = manifest["requested_paths"]
    require(isinstance(requested, list) and 1 <= len(requested) <= 30, "requested_paths must contain 1..30 entries")
    require(all(isinstance(p, str) for p in requested), "requested_paths must contain strings")
    require(len(set(requested)) == len(requested), "duplicate requested paths")
    for path in requested:
        safe_relative_path(path)
        require(any(path.startswith(prefix) for prefix in policy["allowed_path_prefixes"]), f"path outside policy prefixes: {path}")
    provider = manifest["provider_policy"]
    keys(provider, {"enabled", "allowlist", "max_spend_usd"})
    require(provider["enabled"] is False and provider["allowlist"] == [], "providers must remain disabled")
    require(type(provider["max_spend_usd"]) in (int, float) and provider["max_spend_usd"] == 0, "spend cap must be zero")
    require(manifest["environment"] == "none" and manifest["intent"] == "dry-run", "only no-environment dry-run intent is permitted")

def verify_adr(manifest: dict[str, Any], root: Path) -> None:
    target = resolve_file(root, manifest["adr_path"])
    actual = hashlib.sha256(target.read_bytes()).hexdigest()
    require(hmac.compare_digest(actual, manifest["adr_sha256"]), "ADR file digest does not match manifest")

def canonical_approval(approval: dict[str, Any]) -> bytes:
    unsigned = {k: v for k, v in approval.items() if k != "signature"}
    return json.dumps(unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def verify_approval(approval: dict[str, Any], manifest: dict[str, Any], policy: dict[str, Any], now: datetime | None = None) -> None:
    keys(approval, {
        "schema_version", "approval_id", "product_id", "repository", "adr_sha256",
        "phase", "branch", "permitted_paths", "environment", "provider_allowlist",
        "max_spend_usd", "approver", "issued_at", "expires_at", "revoked", "nonce", "signature"
    })
    require(approval["schema_version"] == "1.0", "unsupported approval schema_version")
    require(isinstance(approval["approval_id"], str) and SAFE_ID.fullmatch(approval["approval_id"]), "invalid approval_id")
    require(isinstance(approval["nonce"], str) and SAFE_ID.fullmatch(approval["nonce"]), "invalid approval nonce")
    for field, expected in (("product_id", manifest["product_id"]), ("repository", manifest["repository"]), ("adr_sha256", manifest["adr_sha256"]), ("phase", manifest["requested_phase"]), ("branch", manifest["default_branch"])):
        require(approval[field] == expected, f"approval mismatch: {field}")
    permitted = approval["permitted_paths"]
    require(isinstance(permitted, list) and all(isinstance(p, str) for p in permitted), "permitted_paths must be a list of strings")
    for path in permitted:
        safe_relative_path(path)
    require(len(permitted) == len(set(permitted)), "duplicate permitted paths")
    require(set(permitted) == set(manifest["requested_paths"]), "approval paths must exactly match requested scope")
    require(approval["environment"] == "none" and approval["provider_allowlist"] == [], "approval cannot enable environments or providers")
    require(type(approval["max_spend_usd"]) in (int, float) and approval["max_spend_usd"] == 0, "approval spend cap must be zero")
    require(isinstance(approval["approver"], str) and len(approval["approver"]) >= 2, "approver is required")
    issued = parse_timestamp(approval["issued_at"], "issued_at")
    expires = parse_timestamp(approval["expires_at"], "expires_at")
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    require(issued <= current, "approval issued_at is in the future")
    require(expires > current, "approval has expired")
    require(expires > issued and expires - issued <= timedelta(days=7), "approval validity must be positive and no longer than seven days")
    require(approval["revoked"] is False, "approval is revoked")
    signature = approval["signature"]
    require(isinstance(signature, str) and SIGNATURE.fullmatch(signature), "invalid HMAC signature format")
    key = os.environ.get("FACTORY_APPROVAL_HMAC_KEY", "")
    require(len(key.encode("utf-8")) >= 32, "approval verification key unavailable (minimum 32 bytes)")
    expected_signature = hmac.new(key.encode("utf-8"), canonical_approval(approval), hashlib.sha256).hexdigest()
    require(hmac.compare_digest(signature, expected_signature), "approval signature verification failed")

def redact(value: Any, key: str = "") -> Any:
    if SECRET_KEY.search(key):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {k: redact(v, k) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, str) and SECRET_VALUE.search(value):
        return "[REDACTED]"
    return value

def build_plan(manifest: dict[str, Any], policy: dict[str, Any], root: Path, approval: dict[str, Any] | None = None, now: datetime | None = None) -> dict[str, Any]:
    validate_policy(policy)
    validate_manifest(manifest, policy)
    verify_adr(manifest, root)
    if approval is None:
        return {
            "status": "BLOCKED_MISSING_APPROVAL",
            "mode": "read-only-dry-run",
            "product_id": manifest["product_id"],
            "requested_phase": manifest["requested_phase"],
            "actions": [],
            "side_effects": False,
            "provider_calls": 0,
            "spend_usd": 0,
            "reason": "No signed, phase-bound owner approval was supplied."
        }
    verify_approval(approval, manifest, policy, now)
    return {
        "status": "PLAN_ONLY_APPROVAL_VALIDATED",
        "mode": "read-only-dry-run",
        "product_id": manifest["product_id"],
        "repository": manifest["repository"],
        "branch": manifest["default_branch"],
        "requested_phase": manifest["requested_phase"],
        "permitted_paths": manifest["requested_paths"],
        "actions": ["validate inputs", "record proposed phase scope for human review"],
        "side_effects": False,
        "provider_calls": 0,
        "spend_usd": 0,
        "reason": "Signature and scope validated; this validator cannot execute the proposed work."
    }

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a SaaS factory request without executing it.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--approval")
    parser.add_argument("--root", default=".")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not args.dry_run:
        print("BLOCKED: --dry-run is required; execution is not implemented.", file=sys.stderr)
        return 2
    try:
        manifest = load_json(args.manifest)
        policy = load_json(args.policy)
        approval = load_json(args.approval) if args.approval else None
        plan = build_plan(manifest, policy, Path(args.root), approval)
        print(json.dumps(redact(plan), indent=2, sort_keys=True))
        return 0 if plan["status"] == "PLAN_ONLY_APPROVAL_VALIDATED" else 3
    except ValidationError as exc:
        print(json.dumps({"status": "BLOCKED_VALIDATION_ERROR", "reason": str(exc), "side_effects": False, "provider_calls": 0, "spend_usd": 0}, indent=2))
        return 4

if __name__ == "__main__":
    raise SystemExit(main())
