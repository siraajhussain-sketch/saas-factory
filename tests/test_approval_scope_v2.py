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
    ValidationError, build_plan, canonical_approval_v2, canonical_jcs,
)

KEY = "v2-test-key-that-is-at-least-thirty-two-bytes"
NOW = datetime(2026, 11, 25, 12, 0, tzinfo=timezone.utc)
ADR = "# Scope binding fixture\n"
POLICY = {
    "allowed_repositories": ["example-owner/example-product", "example-owner/other-product"],
    "allowed_branches": ["main", "factory/phase-1"],
    "allowed_path_prefixes": ["src/", "tests/", "docs/", "products/"],
    "allowed_phases": ["discovery", "architecture", "foundation", "feature", "validation"],
}

def make_case(root):
    adr_path = root / "docs/adr/001-example.md"
    adr_path.parent.mkdir(parents=True)
    adr_path.write_text(ADR, encoding="utf-8")
    plan_path = root / "docs/phase-plans/foundation.json"
    plan_path.parent.mkdir(parents=True)
    plan = {
        "schema_version": "1.0",
        "canonicalization_profile": "RFC8785_RESTRICTED_SAFE_INTEGER_V1",
        "operation_class_registry_version": "1.0",
        "product_id": "sample-product",
        "repository": "example-owner/example-product",
        "repository_commit_sha": "a" * 40,
        "target_branch": "main",
        "phase_id": "foundation",
        "steps": [
            {"step_id": "validate-inputs", "description": "Validate local inputs", "depends_on": [], "expected_outputs": ["tests/validation.md"]},
            {"step_id": "summarize-scope", "description": "Produce a plan-only scope summary", "depends_on": ["validate-inputs"], "expected_outputs": ["tests/scope.md"]},
        ],
        "acceptance_criteria": ["All request fields validate", "No external side effects occur"],
        "permitted_paths": ["src/", "tests/"],
        "operation_class": "read_only_validation",
        "allowed_actions": ["validate_inputs", "validate_phase_plan", "produce_plan_only_result"],
        "environment": "none",
        "provider_allowlist": [],
        "max_spend": 0,
        "currency": "USD",
    }
    digest = hashlib.sha256(canonical_jcs(plan)).hexdigest()
    plan_path.write_bytes(canonical_jcs(plan))
    manifest = {
        "schema_version": "2.0",
        "product_id": "sample-product",
        "product_name": "Sample Product",
        "repository": "example-owner/example-product",
        "repository_commit_sha": "a" * 40,
        "target_branch": "main",
        "adr_path": "docs/adr/001-example.md",
        "adr_sha256": hashlib.sha256(ADR.encode()).hexdigest(),
        "requested_phase": "foundation",
        "phase_plan_path": "docs/phase-plans/foundation.json",
        "phase_plan_schema_version": "1.0",
        "phase_plan_sha256": digest,
        "operation_class_registry_version": "1.0",
        "operation_class": "read_only_validation",
        "allowed_actions": ["validate_inputs", "validate_phase_plan", "produce_plan_only_result"],
        "requested_paths": ["src/", "tests/"],
        "provider_policy": {"enabled": False, "allowlist": [], "max_spend_usd": 0},
        "environment": "none",
        "intent": "dry-run",
    }
    return manifest, plan

def make_approval(manifest, **changes):
    value = {
        "schema_version": "2.0",
        "approval_id": "approval-v2-001",
        "product_id": manifest["product_id"],
        "repository": manifest["repository"],
        "repository_commit_sha": manifest["repository_commit_sha"],
        "target_branch": manifest["target_branch"],
        "adr_sha256": manifest["adr_sha256"],
        "phase": manifest["requested_phase"],
        "phase_plan_path": manifest["phase_plan_path"],
        "phase_plan_schema_version": manifest["phase_plan_schema_version"],
        "phase_plan_sha256": manifest["phase_plan_sha256"],
        "operation_class_registry_version": manifest["operation_class_registry_version"],
        "operation_class": manifest["operation_class"],
        "allowed_actions": list(manifest["allowed_actions"]),
        "permitted_paths": list(manifest["requested_paths"]),
        "environment": "none",
        "provider_allowlist": [],
        "max_spend": 0,
        "currency": "USD",
        "approver": "owner",
        "issued_at": "2026-11-25T11:00:00Z",
        "expires_at": "2026-11-26T11:00:00Z",
        "revoked": False,
        "nonce": "b" * 64,
    }
    value.update(changes)
    with patch.dict(os.environ, {"FACTORY_APPROVAL_HMAC_KEY": KEY}):
        value["signature"] = hmac.new(KEY.encode(), canonical_approval_v2(value), hashlib.sha256).hexdigest()
    return value

class ApprovalScopeV2Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.manifest, self.plan = make_case(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def signed(self):
        return make_approval(self.manifest)

    def run_plan(self, manifest=None, approval=None):
        with patch.dict(os.environ, {"FACTORY_APPROVAL_HMAC_KEY": KEY}):
            return build_plan(copy.deepcopy(manifest or self.manifest), copy.deepcopy(POLICY), self.root, approval or self.signed(), NOW)

    def test_valid_v2_scope_is_plan_only_and_does_not_claim_checkout_verification(self):
        result = self.run_plan()
        self.assertEqual(result["status"], "PLAN_ONLY_APPROVAL_VALIDATED")
        self.assertEqual(result["revision_binding"], "DECLARED_ONLY_NOT_CHECKED_OUT")
        self.assertFalse(result["side_effects"])
        self.assertEqual(result["provider_calls"], 0)
        self.assertEqual(result["spend_usd"], 0)

    def test_missing_v2_approval_blocks(self):
        with patch.dict(os.environ, {"FACTORY_APPROVAL_HMAC_KEY": KEY}):
            result = build_plan(copy.deepcopy(self.manifest), copy.deepcopy(POLICY), self.root, None, NOW)
        self.assertEqual(result["status"], "BLOCKED_MISSING_APPROVAL")
        self.assertEqual(result["revision_binding"], "DECLARED_ONLY_NOT_CHECKED_OUT")
        self.assertFalse(result["side_effects"])

    def test_t01_changed_manifest_commit_rejected(self):
        approval = self.signed()
        changed = copy.deepcopy(self.manifest)
        changed["repository_commit_sha"] = "c" * 40
        with self.assertRaisesRegex(ValidationError, "approval mismatch: repository_commit_sha"):
            self.run_plan(changed, approval)

    def test_t02_changed_approval_commit_rejected(self):
        approval = self.signed()
        approval["repository_commit_sha"] = "c" * 40
        with self.assertRaisesRegex(ValidationError, "approval mismatch: repository_commit_sha"):
            self.run_plan(approval=approval)

    def test_t03_non_full_commit_sha_rejected(self):
        for value in ("main", "v1.0.0", "a" * 39, "A" * 40, "g" * 40):
            changed = copy.deepcopy(self.manifest)
            changed["repository_commit_sha"] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValidationError, "full 40-character"):
                self.run_plan(changed)

    def test_t04_phase_plan_byte_tampering_rejected(self):
        path = self.root / self.manifest["phase_plan_path"]
        path.write_text('{"tampered":true}', encoding="utf-8")
        with self.assertRaisesRegex(ValidationError, "phase plan digest"):
            self.run_plan()

    def test_t05_manifest_plan_digest_change_rejected(self):
        changed = copy.deepcopy(self.manifest)
        changed["phase_plan_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValidationError, "phase plan digest"):
            self.run_plan(changed)

    def test_t06_phase_plan_schema_version_change_rejected(self):
        changed = copy.deepcopy(self.manifest)
        changed["phase_plan_schema_version"] = "2.0"
        with self.assertRaisesRegex(ValidationError, "unsupported phase plan schema"):
            self.run_plan(changed)

    def test_t07_step_or_acceptance_change_invalidates_digest(self):
        path = self.root / self.manifest["phase_plan_path"]
        changed_plan = copy.deepcopy(self.plan)
        changed_plan["steps"][0]["description"] = "Different operation"
        path.write_bytes(canonical_jcs(changed_plan))
        with self.assertRaisesRegex(ValidationError, "phase plan digest"):
            self.run_plan()

    def test_t08_path_scope_expansion_rejected(self):
        changed = copy.deepcopy(self.manifest)
        changed["requested_paths"] = ["src/", "tests/", "docs/"]
        with self.assertRaisesRegex(ValidationError, "phase plan mismatch: permitted_paths"):
            self.run_plan(changed)

    def test_t09_repository_write_operation_is_disabled(self):
        changed = copy.deepcopy(self.manifest)
        changed["operation_class"] = "repository_write"
        with self.assertRaisesRegex(ValidationError, "disabled"):
            self.run_plan(changed)

    def test_t10_unknown_operation_class_rejected(self):
        changed = copy.deepcopy(self.manifest)
        changed["operation_class"] = "unknown-operation"
        with self.assertRaisesRegex(ValidationError, "unknown operation class"):
            self.run_plan(changed)

    def test_t11_action_expansion_rejected(self):
        changed = copy.deepcopy(self.manifest)
        changed["allowed_actions"].append("write_repository_file")
        with self.assertRaisesRegex(ValidationError, "exactly match"):
            self.run_plan(changed)

    def test_t12_repository_identity_change_rejected(self):
        approval = self.signed()
        approval["repository"] = "example-owner/other-product"
        with self.assertRaisesRegex(ValidationError, "approval mismatch: repository"):
            self.run_plan(approval=approval)

    def test_t13_target_branch_change_rejected(self):
        approval = self.signed()
        approval["target_branch"] = "factory/phase-1"
        with self.assertRaisesRegex(ValidationError, "approval mismatch: target_branch"):
            self.run_plan(approval=approval)

    def test_t14_adr_content_tampering_rejected(self):
        (self.root / self.manifest["adr_path"]).write_text("changed ADR", encoding="utf-8")
        with self.assertRaisesRegex(ValidationError, "ADR file digest"):
            self.run_plan()

    def test_t15_phase_plan_product_mismatch_rejected(self):
        path = self.root / self.manifest["phase_plan_path"]
        changed_plan = copy.deepcopy(self.plan)
        changed_plan["product_id"] = "other-product"
        self.manifest["phase_plan_sha256"] = hashlib.sha256(canonical_jcs(changed_plan)).hexdigest()
        path.write_bytes(canonical_jcs(changed_plan))
        with self.assertRaisesRegex(ValidationError, "phase plan mismatch: product_id"):
            self.run_plan()

    def test_t16_casefold_path_collision_rejected(self):
        changed = copy.deepcopy(self.manifest)
        changed["requested_paths"] = ["src/Foo/", "src/foo/"]
        with self.assertRaisesRegex(ValidationError, "case-folding collisions"):
            self.run_plan(changed)

    def test_t17_declared_commit_is_never_reported_as_checkout_verified(self):
        result = self.run_plan()
        self.assertEqual(result["revision_binding"], "DECLARED_ONLY_NOT_CHECKED_OUT")
        self.assertIn("actual checkout identity is unverified", result["reason"])

    def test_legacy_v1_approval_is_not_accepted_for_v2_manifest(self):
        approval = {"schema_version": "1.0"}
        with self.assertRaisesRegex(ValidationError, "missing fields"):
            self.run_plan(approval=approval)

    def test_jcs_sorts_object_keys_and_uses_utf8(self):
        self.assertEqual(canonical_jcs({"b": 2, "a": 1}), b'{"a":1,"b":2}')
        self.assertEqual(canonical_jcs({"é": "café"}), '{"é":"café"}'.encode("utf-8"))

    def test_jcs_uses_utf16_code_unit_key_order(self):
        # U+10000 sorts before U+E000 under UTF-16 code-unit ordering.
        value = {"\ue000": 1, "\U00010000": 2}
        self.assertEqual(canonical_jcs(value), '{"𐀀":2,"":1}'.encode("utf-8"))

    def test_jcs_rejects_floats_and_unsafe_integers(self):
        for value in ({"n": 1.5}, {"n": 2 ** 53}):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                canonical_jcs(value)

    def test_jcs_rejects_surrogate_strings(self):
        with self.assertRaises(ValidationError):
            canonical_jcs({"bad": "\ud800"})

if __name__ == "__main__":
    unittest.main()
