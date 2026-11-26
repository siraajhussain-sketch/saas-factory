import hashlib
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from control_plane.case_consistency import CaseConsistencyError, validate_case
from control_plane.lifecycle_manifest import validate_manifest as validate_manifest_real


BRIEF = """# Product Brief
## 1. Summary
Example product for a defined workflow.
## 2. Problem and customer
Buyer and user are identified.
## 3. Geography and operating context
Initial market and locale are stated.
## 4. Core workflows
Users complete the primary workflow.
## 5. Data and privacy
Data categories and retention are described.
## 6. Tenant and authorization model
Product-specific ownership is described.
## 7. Business model and cost constraints
Pricing is a hypothesis; spend is zero.
## 8. Non-functional requirements
Security and reliability needs are stated.
## 9. MVP boundaries
Included and excluded scope are listed.
## 10. Risks and open questions
Unknowns remain explicit.
## 11. Acceptance criteria
A human can review the discovery package.
"""

DISCOVERY = """# Discovery Report
## 1. Executive assessment
Assessment.
## 2. Buyer and user
Buyer.
## 3. Problem and workflows
Workflow.
## 4. Alternatives and competition
Alternatives.
## 5. Market and geography
Market.
## 6. Business model hypotheses
Hypotheses.
## 7. MVP boundary
Included and excluded.
## 8. Risks and unknowns
Risks.
## 9. Recommendation and next decision
Recommendation.
"""

ARCHITECTURE = """# Product Architecture Package
## 1. Context and quality attributes
Context.
## 2. Domain model
Entities.
## 3. Ownership and authorization
Ownership.
## 4. Data and privacy
Data.
## 5. Application and persistence design
Persistence.
## 6. Integrations and dependencies
Dependencies.
## 7. Localization and financial correctness
Localization.
## 8. Security and threat model
Threats.
## 9. Operations
Operations.
## 10. Test and acceptance strategy
Tests.
## 11. Architecture decisions
Decisions.
## 12. Open decisions and risks
Open items.
## 13. Implementation phase proposal
Bounded proposal.
"""

EVIDENCE = """# Evidence Register
| ID | Claim / question | Evidence type | Source / URL | Publisher / author | Published date | Access date | Geography | Confidence | Limitations | Decision informed |
|---|---|---|---|---|---|---|---|---|---|---|
| A1 | Example assumption is unverified | assumption | Owner hypothesis; unverified | Owner | unknown | 2026-11-26 | Initial market | Low | Not validated | Research plan |
## Evidence types
Types.
## Confidence guidance
Confidence.
## Rules
Record limitations.
"""


class CaseConsistencyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.documents = {
            "product_brief": ("brief-v1.md", BRIEF),
            "discovery_report": ("discovery-v1.md", DISCOVERY),
            "architecture_package": ("architecture-v1.md", ARCHITECTURE),
            "evidence_register": ("evidence-v1.md", EVIDENCE),
        }
        artifacts = []
        for kind, (filename, content) in self.documents.items():
            path = self.root / filename
            path.write_text(content, encoding="utf-8")
            artifacts.append({
                "id": kind.replace("_", "-") + "-v1",
                "kind": kind,
                "path": filename,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            })
        self.manifest = {
            "schema_version": "1.0",
            "case_id": "case-example-001",
            "product_id": "product-example",
            "lifecycle_state": "INTAKE",
            "created_at": "2026-11-26T10:00:00Z",
            "updated_at": "2026-11-26T10:00:00Z",
            "artifacts": artifacts,
            "validator_runs": [],
            "human_reviews": [],
            "state_history": [{
                "from": None,
                "to": "INTAKE",
                "recorded_at": "2026-11-26T10:00:00Z",
                "reason": "Synthetic test case",
            }],
        }

    def tearDown(self):
        self.temp.cleanup()

    def test_complete_case_passes_without_authorizing(self):
        result = validate_case(self.manifest, self.root)
        self.assertEqual(result["status"], "CASE_PACKAGE_READY_FOR_HUMAN_REVIEW")
        self.assertEqual(len(result["artifacts"]), 4)
        self.assertFalse(result["authorization_granted"])
        self.assertFalse(result["side_effects"])
        self.assertEqual(result["provider_calls"], 0)
        self.assertEqual(result["spend_usd"], 0)

    def test_missing_required_kind_blocks(self):
        self.manifest["artifacts"] = [
            item for item in self.manifest["artifacts"]
            if item["kind"] != "evidence_register"
        ]
        with self.assertRaisesRegex(CaseConsistencyError, "missing required artifact kinds"):
            validate_case(self.manifest, self.root)

    def test_duplicate_required_kind_blocks(self):
        duplicate = dict(self.manifest["artifacts"][0])
        duplicate["id"] = "brief-v2"
        self.manifest["artifacts"].append(duplicate)
        with self.assertRaisesRegex(CaseConsistencyError, "exactly one"):
            validate_case(self.manifest, self.root)

    def test_invalid_product_brief_blocks(self):
        path = self.root / self.documents["product_brief"][0]
        path.write_text("# Incomplete brief", encoding="utf-8")
        self.refresh_hash("product_brief")
        with self.assertRaisesRegex(CaseConsistencyError, "product_brief"):
            validate_case(self.manifest, self.root)

    def test_invalid_discovery_package_blocks(self):
        path = self.root / self.documents["discovery_report"][0]
        path.write_text("# Incomplete discovery", encoding="utf-8")
        self.refresh_hash("discovery_report")
        with self.assertRaisesRegex(CaseConsistencyError, "Phase 2 package"):
            validate_case(self.manifest, self.root)

    def test_hash_mismatch_blocks_before_content_checks(self):
        self.manifest["artifacts"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            validate_case(self.manifest, self.root)

    def test_same_snapshot_is_hashed_and_validated_if_file_changes_after_capture(self):
        brief_path = self.root / self.documents["product_brief"][0]

        def mutate_after_snapshot(manifest, root, *, artifact_snapshots):
            # Simulate a concurrent writer after the checker has captured bytes.
            brief_path.write_text("# Tampered after snapshot", encoding="utf-8")
            return validate_manifest_real(
                manifest, root, artifact_snapshots=artifact_snapshots
            )

        with patch(
            "control_plane.case_consistency.validate_manifest",
            side_effect=mutate_after_snapshot,
        ):
            result = validate_case(self.manifest, self.root)

        # The validated bytes are the original, hash-matched snapshot, not the
        # changed on-disk file. A second read would incorrectly reject this case.
        self.assertEqual(result["status"], "CASE_PACKAGE_READY_FOR_HUMAN_REVIEW")
        self.assertEqual(
            brief_path.read_text(encoding="utf-8"), "# Tampered after snapshot"
        )
        self.assertEqual(
            result["checks"]["artifact_snapshot_reuse"],
            "same_bytes_hashed_and_structurally_validated",
        )
        self.assertFalse(result["authorization_granted"])

    def test_validator_run_records_are_not_authorization(self):
        self.manifest["validator_runs"] = [{
            "id": "pretend-pass-1",
            "validator": "some_validator",
            "status": "passed",
            "recorded_at": "2026-11-26T10:01:00Z",
            "artifact_ids": [item["id"] for item in self.manifest["artifacts"]],
        }]
        result = validate_case(self.manifest, self.root)
        self.assertTrue(result["checks"]["recorded_validator_runs_are_historical_only"])
        self.assertFalse(result["authorization_granted"])

    def test_human_review_claim_does_not_authorize(self):
        self.manifest["human_reviews"] = [{
            "id": "review-1",
            "stage": "combined",
            "reviewer_label": "Owner",
            "decision": "accepted",
            "recorded_at": "2026-11-26T10:02:00Z",
            "notes": "Recorded review claim.",
        }]
        result = validate_case(self.manifest, self.root)
        self.assertFalse(result["authorization_granted"])


    def test_committed_synthetic_workshop_queue_fixture(self):
        from control_plane.lifecycle_manifest import read_manifest

        repository_root = Path(__file__).resolve().parents[1]
        fixture_root = repository_root / "examples" / "lifecycle"
        manifest_path = fixture_root / "sample-case.json"
        manifest = read_manifest(manifest_path)
        result = validate_case(manifest, fixture_root)
        self.assertEqual(result["case_id"], "workshop-queue-demo-001")
        self.assertEqual(result["status"], "CASE_PACKAGE_READY_FOR_HUMAN_REVIEW")
        self.assertEqual(len(result["artifacts"]), 4)
        self.assertFalse(result["authorization_granted"])

    def refresh_hash(self, kind):
        artifact = next(item for item in self.manifest["artifacts"] if item["kind"] == kind)
        path = self.root / artifact["path"]
        artifact["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    unittest.main()
