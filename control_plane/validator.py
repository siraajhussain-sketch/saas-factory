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
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{1,62}$")
SHA256 = re.compile(r"^[a-f0-9]{64}$")
SIGNATURE = re.compile(r"^[a-f0-9]{64}$")
NONCE = re.compile(r"^[a-f0-9]{64}$")
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

def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key rejected")
        result[key] = value
    return result

def _reject_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant rejected: {value}")

def load_json(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(
            Path(path).read_text(encoding="utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except (OSError, UnicodeError, ValueError) as exc:
        detail = str(exc)
        if len(detail) > 100:
            detail = detail[:100]
        raise ValidationError(f"cannot read valid JSON input ({type(exc).__name__}: {detail})") from exc
    require(isinstance(value, dict), "top-level JSON value must be an object")
    return value

def safe_relative_path(value: Any) -> str:
    require(isinstance(value, str) and value and not value.startswith("/"), "paths must be non-empty relative POSIX paths")
    require("\\" not in value and "\x00" not in value, "path contains an invalid character")
    require(unicodedata.normalize("NFC", value) == value, "path must use Unicode NFC normalization")
    require(not any(unicodedata.category(char) in ("Cc", "Cf") for char in value), "path contains a control or formatting character")
    require(not any(char in value for char in (":",)), "path contains a platform-specific separator or stream marker")
    # A single trailing slash denotes an allowed directory prefix.
    normalized = value[:-1] if value.endswith("/") else value
    require(normalized and not normalized.endswith("/"), "path contains an empty segment")
    parts = normalized.split("/")
    require(all(part not in ("", ".", "..") for part in parts), "path traversal or empty path segment rejected")
    require(all(not part.endswith((".", " ")) for part in parts), "path segment has a platform-ambiguous suffix")
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



# Version 2 scope binding. This remains a local, read-only, plan-only validator.
GIT_COMMIT_SHA = re.compile(r"^[a-f0-9]{40}$")
OPERATION_CLASSES = {
    "read_only_validation": {"validate_inputs", "validate_phase_plan", "produce_plan_only_result"},
    "repository_write": set(),
    "external_provisioning": set(),
    "deployment": set(),
    "destructive_change": set(),
}
OPERATION_CLASS_REGISTRY_VERSION = "1.0"
JCS_PROFILE = "RFC8785_RESTRICTED_SAFE_INTEGER_V1"
MAX_SAFE_INTEGER = (2 ** 53) - 1

def _jcs_encode(value: Any) -> str:
    """RFC 8785-compatible serialization for a deliberately restricted JSON subset.

    Integers are limited to the interoperable IEEE-754 safe range; floats are
    rejected. This avoids pretending Python's generic JSON encoder implements
    all ECMAScript number serialization rules.
    """
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        require(-MAX_SAFE_INTEGER <= value <= MAX_SAFE_INTEGER, "JCS integer outside safe interoperable range")
        return str(value)
    if isinstance(value, float):
        raise ValidationError("JCS profile rejects floating-point numbers; use safe integers")
    if isinstance(value, str):
        try:
            value.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise ValidationError("JCS string contains invalid Unicode surrogate") from exc
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, list):
        return "[" + ",".join(_jcs_encode(item) for item in value) + "]"
    if isinstance(value, dict):
        require(all(isinstance(key, str) for key in value), "JCS object keys must be strings")
        try:
            ordered = sorted(value, key=lambda key: key.encode("utf-16-be"))
        except UnicodeEncodeError as exc:
            raise ValidationError("JCS object key contains invalid Unicode surrogate") from exc
        return "{" + ",".join(
            _jcs_encode(key) + ":" + _jcs_encode(value[key]) for key in ordered
        ) + "}"
    raise ValidationError("JCS profile contains an unsupported value type")

def canonical_jcs(value: Any) -> bytes:
    return _jcs_encode(value).encode("utf-8")

def canonical_approval_v2(approval: dict[str, Any]) -> bytes:
    unsigned = {key: value for key, value in approval.items() if key != "signature"}
    return canonical_jcs(unsigned)

def _validate_scope_paths(paths: Any, policy: dict[str, Any], field: str) -> list[str]:
    require(isinstance(paths, list) and 1 <= len(paths) <= 30, f"{field} must contain 1..30 entries")
    require(all(isinstance(path, str) for path in paths), f"{field} must contain strings")
    require(len(paths) == len(set(paths)), f"{field} contains duplicate paths")
    folded = [path.casefold() for path in paths]
    require(len(folded) == len(set(folded)), f"{field} contains case-folding collisions")
    for path in paths:
        safe_relative_path(path)
        require(any(path.startswith(prefix) for prefix in policy["allowed_path_prefixes"]), f"path outside policy prefixes: {path}")
    return paths

def validate_manifest_v2(manifest: dict[str, Any], policy: dict[str, Any]) -> None:
    keys(manifest, {
        "schema_version", "product_id", "product_name", "repository",
        "repository_commit_sha", "target_branch", "adr_path", "adr_sha256",
        "requested_phase", "phase_plan_path", "phase_plan_schema_version",
        "phase_plan_sha256", "operation_class_registry_version", "operation_class", "allowed_actions",
        "requested_paths", "provider_policy", "environment", "intent"
    })
    require(manifest["schema_version"] == "2.0", "unsupported manifest schema_version")
    require(isinstance(manifest["product_id"], str) and SAFE_ID.fullmatch(manifest["product_id"]), "invalid product_id")
    require(isinstance(manifest["product_name"], str) and 2 <= len(manifest["product_name"]) <= 120, "invalid product_name")
    require(isinstance(manifest["repository"], str) and REPOSITORY.fullmatch(manifest["repository"]), "invalid repository")
    require(manifest["repository"] in policy["allowed_repositories"], "repository is not allowlisted")
    require(isinstance(manifest["repository_commit_sha"], str) and GIT_COMMIT_SHA.fullmatch(manifest["repository_commit_sha"]), "repository_commit_sha must be a full 40-character lowercase Git commit SHA")
    require(isinstance(manifest["target_branch"], str) and manifest["target_branch"] in policy["allowed_branches"], "target branch is not allowlisted")
    require(manifest["requested_phase"] in policy["allowed_phases"], "phase is not allowlisted")
    require(isinstance(manifest["adr_path"], str) and manifest["adr_path"].startswith("docs/adr/"), "adr_path must be under docs/adr/")
    safe_relative_path(manifest["adr_path"])
    require(isinstance(manifest["adr_sha256"], str) and SHA256.fullmatch(manifest["adr_sha256"]), "invalid ADR SHA-256")
    require(isinstance(manifest["phase_plan_path"], str) and manifest["phase_plan_path"].startswith("docs/phase-plans/"), "phase_plan_path must be under docs/phase-plans/")
    safe_relative_path(manifest["phase_plan_path"])
    require(isinstance(manifest["phase_plan_schema_version"], str) and manifest["phase_plan_schema_version"] == "1.0", "unsupported phase plan schema version")
    require(isinstance(manifest["phase_plan_sha256"], str) and SHA256.fullmatch(manifest["phase_plan_sha256"]), "invalid phase plan SHA-256")
    require(manifest["operation_class_registry_version"] == OPERATION_CLASS_REGISTRY_VERSION, "operation class registry version mismatch")
    require(manifest["operation_class"] in OPERATION_CLASSES, "unknown operation class")
    require(manifest["operation_class"] == "read_only_validation", "operation class is disabled in this prototype")
    actions = manifest["allowed_actions"]
    require(isinstance(actions, list) and all(isinstance(item, str) for item in actions), "allowed_actions must be a list of strings")
    require(len(actions) == len(set(actions)), "allowed_actions contains duplicates")
    require(set(actions) == OPERATION_CLASSES["read_only_validation"], "allowed_actions must exactly match the read-only operation registry")
    _validate_scope_paths(manifest["requested_paths"], policy, "requested_paths")
    provider = manifest["provider_policy"]
    keys(provider, {"enabled", "allowlist", "max_spend_usd"})
    require(provider["enabled"] is False and provider["allowlist"] == [], "providers must remain disabled")
    require(type(provider["max_spend_usd"]) is int and provider["max_spend_usd"] == 0, "spend cap must be integer zero")
    require(manifest["environment"] == "none" and manifest["intent"] == "dry-run", "only no-environment dry-run intent is permitted")

def validate_phase_plan_v2(plan: dict[str, Any], manifest: dict[str, Any]) -> None:
    keys(plan, {
        "schema_version", "canonicalization_profile", "operation_class_registry_version",
        "product_id", "repository", "repository_commit_sha", "target_branch",
        "phase_id", "steps", "acceptance_criteria", "permitted_paths",
        "operation_class", "allowed_actions", "environment", "provider_allowlist",
        "max_spend", "currency"
    })
    require(plan["schema_version"] == manifest["phase_plan_schema_version"], "phase plan schema/version mismatch")
    require(plan["canonicalization_profile"] == JCS_PROFILE, "unsupported phase plan canonicalization profile")
    require(plan["operation_class_registry_version"] == OPERATION_CLASS_REGISTRY_VERSION, "operation class registry version mismatch")
    for field, manifest_field in (
        ("product_id", "product_id"), ("repository", "repository"),
        ("repository_commit_sha", "repository_commit_sha"), ("target_branch", "target_branch"),
        ("phase_id", "requested_phase"), ("operation_class", "operation_class"),
        ("allowed_actions", "allowed_actions"), ("permitted_paths", "requested_paths"),
        ("environment", "environment")
    ):
        expected = manifest["provider_policy"] if field == "provider_allowlist" else manifest[manifest_field] if manifest_field else None
        if field == "provider_allowlist":
            require(plan[field] == [], "phase plan cannot enable providers")
        else:
            require(plan[field] == expected, f"phase plan mismatch: {field}")
    require(plan["max_spend"] == 0 and type(plan["max_spend"]) is int, "phase plan spend must be integer zero")
    require(plan["currency"] == "USD", "phase plan currency must be USD")
    steps = plan["steps"]
    require(isinstance(steps, list) and 1 <= len(steps) <= 20, "phase plan steps must contain 1..20 entries")
    step_ids = []
    for step in steps:
        keys(step, {"step_id", "description", "depends_on", "expected_outputs"})
        require(isinstance(step["step_id"], str) and SAFE_ID.fullmatch(step["step_id"]), "invalid phase plan step_id")
        require(isinstance(step["description"], str) and 1 <= len(step["description"]) <= 500, "invalid phase plan step description")
        require(isinstance(step["depends_on"], list) and all(isinstance(item, str) for item in step["depends_on"]), "invalid step dependencies")
        require(isinstance(step["expected_outputs"], list) and all(isinstance(item, str) for item in step["expected_outputs"]), "invalid expected outputs")
        for output in step["expected_outputs"]:
            safe_relative_path(output)
        step_ids.append(step["step_id"])
    require(len(step_ids) == len(set(step_ids)), "duplicate phase plan step_id")
    seen = set()
    for step in steps:
        require(set(step["depends_on"]).issubset(seen), "phase plan dependencies must reference earlier steps")
        seen.add(step["step_id"])
    criteria = plan["acceptance_criteria"]
    require(isinstance(criteria, list) and 1 <= len(criteria) <= 30, "acceptance_criteria must contain 1..30 entries")
    require(all(isinstance(item, str) and 1 <= len(item) <= 500 for item in criteria), "invalid acceptance criterion")
    _validate_scope_paths(plan["permitted_paths"], {"allowed_path_prefixes": ["src/", "tests/", "docs/", "products/"]}, "phase plan permitted_paths")
    for step in steps:
        for output in step["expected_outputs"]:
            require(any(output.startswith(prefix) for prefix in plan["permitted_paths"]), "phase plan expected output is outside permitted paths")

def load_phase_plan_v2(manifest: dict[str, Any], root: Path) -> dict[str, Any]:
    target = resolve_file(root, manifest["phase_plan_path"])
    try:
        plan = json.loads(
            target.read_text(encoding="utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except (OSError, UnicodeError, ValueError) as exc:
        raise ValidationError(f"cannot read valid phase plan ({type(exc).__name__})") from exc
    require(isinstance(plan, dict), "phase plan top-level value must be an object")
    actual = hashlib.sha256(canonical_jcs(plan)).hexdigest()
    require(hmac.compare_digest(actual, manifest["phase_plan_sha256"]), "phase plan digest does not match manifest")
    validate_phase_plan_v2(plan, manifest)
    return plan

def verify_approval_v2(approval: dict[str, Any], manifest: dict[str, Any], now: datetime | None = None) -> None:
    keys(approval, {
        "schema_version", "approval_id", "product_id", "repository",
        "repository_commit_sha", "target_branch", "adr_sha256", "phase",
        "phase_plan_path", "phase_plan_schema_version", "phase_plan_sha256", "operation_class_registry_version",
        "operation_class", "allowed_actions", "permitted_paths", "environment",
        "provider_allowlist", "max_spend", "currency", "approver", "issued_at",
        "expires_at", "revoked", "nonce", "signature"
    })
    require(approval["schema_version"] == "2.0", "unsupported approval schema_version")
    require(isinstance(approval["approval_id"], str) and SAFE_ID.fullmatch(approval["approval_id"]), "invalid approval_id")
    require(isinstance(approval["nonce"], str) and NONCE.fullmatch(approval["nonce"]), "nonce must be 64 lowercase hexadecimal characters generated from a cryptographically secure random source")
    bindings = (
        ("product_id", "product_id"), ("repository", "repository"),
        ("repository_commit_sha", "repository_commit_sha"), ("target_branch", "target_branch"),
        ("adr_sha256", "adr_sha256"), ("phase", "requested_phase"),
        ("phase_plan_path", "phase_plan_path"),
        ("phase_plan_schema_version", "phase_plan_schema_version"),
        ("phase_plan_sha256", "phase_plan_sha256"),
        ("operation_class_registry_version", "operation_class_registry_version"),
        ("operation_class", "operation_class"), ("allowed_actions", "allowed_actions"),
        ("permitted_paths", "requested_paths"), ("environment", "environment"),
    )
    for approval_field, manifest_field in bindings:
        require(approval[approval_field] == manifest[manifest_field], f"approval mismatch: {approval_field}")
    require(approval["provider_allowlist"] == [], "approval cannot enable providers")
    require(type(approval["max_spend"]) is int and approval["max_spend"] == 0, "approval spend cap must be integer zero")
    require(approval["currency"] == "USD", "approval currency must be USD")
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
    expected_signature = hmac.new(key.encode("utf-8"), canonical_approval_v2(approval), hashlib.sha256).hexdigest()
    require(hmac.compare_digest(signature, expected_signature), "approval signature verification failed")


def verify_adr(manifest: dict[str, Any], root: Path) -> None:
    target = resolve_file(root, manifest["adr_path"])
    actual = hashlib.sha256(target.read_bytes()).hexdigest()
    require(hmac.compare_digest(actual, manifest["adr_sha256"]), "ADR file digest does not match manifest")

def canonical_approval(approval: dict[str, Any]) -> bytes:
    unsigned = {k: v for k, v in approval.items() if k != "signature"}
    return json.dumps(unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")

def verify_approval(approval: dict[str, Any], manifest: dict[str, Any], policy: dict[str, Any], now: datetime | None = None) -> None:
    keys(approval, {
        "schema_version", "approval_id", "product_id", "repository", "adr_sha256",
        "phase", "branch", "permitted_paths", "environment", "provider_allowlist",
        "max_spend_usd", "approver", "issued_at", "expires_at", "revoked", "nonce", "signature"
    })
    require(approval["schema_version"] == "1.0", "unsupported approval schema_version")
    require(isinstance(approval["approval_id"], str) and SAFE_ID.fullmatch(approval["approval_id"]), "invalid approval_id")
    require(isinstance(approval["nonce"], str) and NONCE.fullmatch(approval["nonce"]), "nonce must be 64 lowercase hexadecimal characters generated from a cryptographically secure random source")
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
    is_v2 = manifest.get("schema_version") == "2.0"
    if is_v2:
        validate_manifest_v2(manifest, policy)
        verify_adr(manifest, root)
        load_phase_plan_v2(manifest, root)
        if approval is None:
            return {
                "status": "BLOCKED_MISSING_APPROVAL",
                "mode": "read-only-dry-run",
                "product_id": manifest["product_id"],
                "requested_phase": manifest["requested_phase"],
                "repository_commit_sha": manifest["repository_commit_sha"],
                "revision_binding": "DECLARED_ONLY_NOT_CHECKED_OUT",
                "actions": [],
                "side_effects": False,
                "provider_calls": 0,
                "spend_usd": 0,
                "reason": "No signed v2 approval was supplied; checkout identity is not verified by this local validator."
            }
        verify_approval_v2(approval, manifest, now)
        return {
            "status": "PLAN_ONLY_APPROVAL_VALIDATED",
            "mode": "read-only-dry-run",
            "product_id": manifest["product_id"],
            "repository": manifest["repository"],
            "target_branch": manifest["target_branch"],
            "repository_commit_sha": manifest["repository_commit_sha"],
            "revision_binding": "DECLARED_ONLY_NOT_CHECKED_OUT",
            "phase_plan_sha256": manifest["phase_plan_sha256"],
            "operation_class": manifest["operation_class"],
            "allowed_actions": manifest["allowed_actions"],
            "requested_phase": manifest["requested_phase"],
            "permitted_paths": manifest["requested_paths"],
            "actions": ["validate inputs", "validate phase plan", "produce plan-only result"],
            "side_effects": False,
            "provider_calls": 0,
            "spend_usd": 0,
            "reason": "Version 2 signature and declared scope validated; actual checkout identity is unverified and this validator cannot execute the proposed work."
        }
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
