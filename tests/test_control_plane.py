import copy
import hashlib
import hmac
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from control_plane.validator import (
    ValidationError, build_plan, canonical_approval, redact,
    validate_manifest, verify_approval,
)

KEY = "unit-test-key-with-at-least-thirty-two-bytes-long"
NOW = datetime(2026, 11, 25, 12, 0, tzinfo=timezone.utc)
ADR_TEXT = "# Example product ADR\n\nGeneric test fixture only.\n"
POLICY = {
    "allowed_repositories": ["example-owner/example-product"],
    "allowed_branches": ["main", "factory/phase-1"],
    "allowed_path_prefixes": ["src/", "tests/", "docs/", "products/"],
    "allowed_phases": ["discovery", "architecture", "foundation", "feature", "validation"],
}
MANIFEST = {
    "schema_version": "1.0",
    "product_id": "sample-product",
    "product_name": "Sample Product",
    "repository": "example-owner/example-product",
    "default_branch": "main",
    "adr_path": "docs/adr/001-example.md",
    "adr_sha256": hashlib.sha256(ADR_TEXT.encode()).hexdigest(),
    "requested_phase": "foundation",
    "requested_paths": ["src/", "tests/"],
    "provider_policy": {"enabled": False, "allowlist": [], "max_spend_usd": 0},
    "environment": "none",
    "intent": "dry-run",
}

def make_approval(**changes):
    value = {
        "schema_version": "1.0",
        "approval_id": "approval-001",
        "product_id": MANIFEST["product_id"],
        "repository": MANIFEST["repository"],
        "adr_sha256": MANIFEST["adr_sha256"],
        "phase": MANIFEST["requested_phase"],
        "branch": MANIFEST["default_branch"],
        "permitted_paths": list(MANIFEST["requested_paths"]),
        "environment": "none",
        "provider_allowlist": [],
        "max_spend_usd": 0,
        "approver": "owner",
        "issued_at": "2026-11-25T11:00:00Z",
        "expires_at": "2026-11-26T11:00:00Z",
        "revoked": False,
        "nonce": "nonce-unique-001",
    }
    value.update(changes)
    with patch.dict(os.environ, {"FACTORY_APPROVAL_HMAC_KEY": KEY}):
        value["signature"] = hmac.new(KEY.encode(), canonical_approval(value), hashlib.sha256).hexdigest()
    return value

class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        adr = self.root / MANIFEST["adr_path"]
        adr.parent.mkdir(parents=True)
        adr.write_text(ADR_TEXT, encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_valid_manifest(self):
        validate_manifest(copy.deepcopy(MANIFEST), POLICY)

    def test_missing_required_field_rejected(self):
        m = copy.deepcopy(MANIFEST)
        del m["repository"]
        with self.assertRaises(ValidationError):
            validate_manifest(m, POLICY)

    def test_unknown_field_rejected(self):
        m = copy.deepcopy(MANIFEST)
        m["tenant_key"] = "some_key"
        with self.assertRaises(ValidationError):
            validate_manifest(m, POLICY)

    def test_repository_not_allowlisted(self):
        m = copy.deepcopy(MANIFEST)
        m["repository"] = "attacker/other"
        with self.assertRaisesRegex(ValidationError, "not allowlisted"):
            validate_manifest(m, POLICY)

    def test_path_traversal_rejected(self):
        m = copy.deepcopy(MANIFEST)
        m["requested_paths"] = ["src/../../secrets.txt"]
        with self.assertRaises(ValidationError):
            validate_manifest(m, POLICY)

    def test_duplicate_paths_rejected(self):
        m = copy.deepcopy(MANIFEST)
        m["requested_paths"] = ["src/", "src/"]
        with self.assertRaisesRegex(ValidationError, "duplicate"):
            validate_manifest(m, POLICY)

    def test_path_outside_policy_rejected(self):
        m = copy.deepcopy(MANIFEST)
        m["requested_paths"] = [".github/workflows/deploy.yml"]
        with self.assertRaisesRegex(ValidationError, "outside policy"):
            validate_manifest(m, POLICY)

    def test_provider_enablement_rejected(self):
        m = copy.deepcopy(MANIFEST)
        m["provider_policy"]["enabled"] = True
        with self.assertRaises(ValidationError):
            validate_manifest(m, POLICY)

    def test_nonzero_spend_rejected(self):
        m = copy.deepcopy(MANIFEST)
        m["provider_policy"]["max_spend_usd"] = 0.01
        with self.assertRaises(ValidationError):
            validate_manifest(m, POLICY)

    def test_environment_or_execution_intent_rejected(self):
        m = copy.deepcopy(MANIFEST)
        m["intent"] = "execute"
        with self.assertRaises(ValidationError):
            validate_manifest(m, POLICY)

    def test_adr_tampering_rejected(self):
        (self.root / MANIFEST["adr_path"]).write_text("tampered", encoding="utf-8")
        with self.assertRaisesRegex(ValidationError, "digest"):
            build_plan(copy.deepcopy(MANIFEST), POLICY, self.root)

    def test_missing_approval_blocks_without_side_effects(self):
        plan = build_plan(copy.deepcopy(MANIFEST), POLICY, self.root, now=NOW)
        self.assertEqual(plan["status"], "BLOCKED_MISSING_APPROVAL")
        self.assertFalse(plan["side_effects"])
        self.assertEqual(plan["provider_calls"], 0)
        self.assertEqual(plan["spend_usd"], 0)

    def test_valid_signature_produces_plan_only(self):
        approval = make_approval()
        with patch.dict(os.environ, {"FACTORY_APPROVAL_HMAC_KEY": KEY}):
            plan = build_plan(copy.deepcopy(MANIFEST), POLICY, self.root, approval, NOW)
        self.assertEqual(plan["status"], "PLAN_ONLY_APPROVAL_VALIDATED")
        self.assertFalse(plan["side_effects"])
        self.assertEqual(plan["provider_calls"], 0)
        self.assertEqual(plan["spend_usd"], 0)

    def test_missing_verification_key_rejected(self):
        approval = make_approval()
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValidationError, "key unavailable"):
                verify_approval(approval, MANIFEST, POLICY, NOW)

    def test_tampered_signature_rejected(self):
        approval = make_approval()
        approval["signature"] = "0" * 64
        with patch.dict(os.environ, {"FACTORY_APPROVAL_HMAC_KEY": KEY}):
            with self.assertRaisesRegex(ValidationError, "signature"):
                verify_approval(approval, MANIFEST, POLICY, NOW)

    def test_expired_approval_rejected(self):
        approval = make_approval(expires_at="2026-11-25T11:59:00Z")
        with patch.dict(os.environ, {"FACTORY_APPROVAL_HMAC_KEY": KEY}):
            with self.assertRaisesRegex(ValidationError, "expired"):
                verify_approval(approval, MANIFEST, POLICY, NOW)

    def test_future_issued_approval_rejected(self):
        approval = make_approval(issued_at="2026-11-25T12:01:00Z")
        with patch.dict(os.environ, {"FACTORY_APPROVAL_HMAC_KEY": KEY}):
            with self.assertRaisesRegex(ValidationError, "future"):
                verify_approval(approval, MANIFEST, POLICY, NOW)

    def test_long_lived_approval_rejected(self):
        approval = make_approval(expires_at="2026-12-03T11:00:00Z")
        with patch.dict(os.environ, {"FACTORY_APPROVAL_HMAC_KEY": KEY}):
            with self.assertRaisesRegex(ValidationError, "seven days"):
                verify_approval(approval, MANIFEST, POLICY, NOW)

    def test_revoked_approval_rejected(self):
        approval = make_approval(revoked=True)
        with patch.dict(os.environ, {"FACTORY_APPROVAL_HMAC_KEY": KEY}):
            with self.assertRaisesRegex(ValidationError, "revoked"):
                verify_approval(approval, MANIFEST, POLICY, NOW)

    def test_branch_mismatch_rejected(self):
        approval = make_approval(branch="factory/phase-1")
        with patch.dict(os.environ, {"FACTORY_APPROVAL_HMAC_KEY": KEY}):
            with self.assertRaisesRegex(ValidationError, "branch"):
                verify_approval(approval, MANIFEST, POLICY, NOW)

    def test_approval_cannot_expand_path_scope(self):
        approval = make_approval(permitted_paths=["src/", "tests/", "docs/"])
        with patch.dict(os.environ, {"FACTORY_APPROVAL_HMAC_KEY": KEY}):
            with self.assertRaisesRegex(ValidationError, "exactly match"):
                verify_approval(approval, MANIFEST, POLICY, NOW)

    def test_approval_path_traversal_rejected(self):
        approval = make_approval(permitted_paths=["src/../../secrets"])
        with patch.dict(os.environ, {"FACTORY_APPROVAL_HMAC_KEY": KEY}):
            with self.assertRaises(ValidationError):
                verify_approval(approval, MANIFEST, POLICY, NOW)

    def test_redaction(self):
        result = redact({"api_key": "secret-value", "note": "ghp_abcdefghijklmnopqrstuv"})
        self.assertEqual(result["api_key"], "[REDACTED]")
        self.assertEqual(result["note"], "[REDACTED]")

    def test_empty_repository_allowlist_fails_closed(self):
        policy = copy.deepcopy(POLICY)
        policy["allowed_repositories"] = []
        with self.assertRaisesRegex(ValidationError, "empty"):
            build_plan(copy.deepcopy(MANIFEST), policy, self.root, now=NOW)

if __name__ == "__main__":
    unittest.main()
