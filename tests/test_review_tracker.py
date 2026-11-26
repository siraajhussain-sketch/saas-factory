import copy
import unittest
from pathlib import Path

from control_plane.lifecycle_manifest import read_manifest
from control_plane.review_tracker import (
    ReviewTrackerError,
    read_review_record,
    validate_review_record,
)


class ReviewTrackerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = Path(__file__).resolve().parents[1]
        cls.root = cls.repo / "examples" / "lifecycle"
        cls.manifest = read_manifest(cls.root / "sample-case.json")
        cls.record = read_review_record(
            cls.root / "workshop-queue" / "review-tracker.json"
        )

    def test_committed_assessment_passes_but_is_not_human_review(self):
        result = validate_review_record(self.record, self.manifest, self.root)
        self.assertEqual(
            result["status"],
            "REVIEW_TRACKER_STRUCTURALLY_VALID_FOR_FOLLOW_UP",
        )
        self.assertEqual(result["finding_count"], 6)
        self.assertFalse(result["human_review_completed"])
        self.assertFalse(result["authorization_granted"])
        self.assertFalse(result["side_effects"])
        self.assertEqual(result["provider_calls"], 0)
        self.assertEqual(result["spend_usd"], 0)

    def test_stale_artifact_digest_blocks(self):
        record = copy.deepcopy(self.record)
        record["reviewed_artifacts"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ReviewTrackerError, "stale/incomplete"):
            validate_review_record(record, self.manifest, self.root)

    def test_wrong_case_id_blocks(self):
        record = copy.deepcopy(self.record)
        record["case_id"] = "different-case"
        with self.assertRaisesRegex(ReviewTrackerError, "case_id"):
            validate_review_record(record, self.manifest, self.root)

    def test_human_review_claim_is_not_accepted_for_assistant_fixture(self):
        record = copy.deepcopy(self.record)
        record["human_review_completed"] = True
        with self.assertRaisesRegex(ReviewTrackerError, "must be false"):
            validate_review_record(record, self.manifest, self.root)

    def test_authorization_claim_blocks(self):
        record = copy.deepcopy(self.record)
        record["authorization_granted"] = True
        with self.assertRaisesRegex(ReviewTrackerError, "must be false"):
            validate_review_record(record, self.manifest, self.root)

    def test_unknown_review_record_field_blocks(self):
        record = copy.deepcopy(self.record)
        record["unexpected"] = "ignored?"
        with self.assertRaisesRegex(ReviewTrackerError, "unknown fields"):
            validate_review_record(record, self.manifest, self.root)

    def test_unknown_reviewed_artifact_field_blocks(self):
        record = copy.deepcopy(self.record)
        record["reviewed_artifacts"][0]["unexpected"] = "value"
        with self.assertRaisesRegex(ReviewTrackerError, "unknown fields"):
            validate_review_record(record, self.manifest, self.root)

    def test_unknown_finding_field_blocks(self):
        record = copy.deepcopy(self.record)
        record["findings"][0]["unexpected"] = "value"
        with self.assertRaisesRegex(ReviewTrackerError, "unknown fields"):
            validate_review_record(record, self.manifest, self.root)

    def test_review_timestamp_cannot_predate_case(self):
        record = copy.deepcopy(self.record)
        record["created_at"] = "2026-11-26T05:59:59Z"
        with self.assertRaisesRegex(ReviewTrackerError, "must not predate"):
            validate_review_record(record, self.manifest, self.root)

    def test_duplicate_finding_id_blocks(self):
        record = copy.deepcopy(self.record)
        record["findings"].append(copy.deepcopy(record["findings"][0]))
        with self.assertRaisesRegex(ReviewTrackerError, "duplicate id"):
            validate_review_record(record, self.manifest, self.root)

    def test_unsupported_status_blocks(self):
        record = copy.deepcopy(self.record)
        record["findings"][0]["status"] = "verified"
        with self.assertRaisesRegex(ReviewTrackerError, "unsupported status"):
            validate_review_record(record, self.manifest, self.root)

    def test_claimed_resolved_requires_resolution_note(self):
        record = copy.deepcopy(self.record)
        record["findings"][0]["status"] = "claimed_resolved"
        with self.assertRaisesRegex(ReviewTrackerError, "resolution_note"):
            validate_review_record(record, self.manifest, self.root)

    def test_critical_finding_prevents_ready_for_owner_decision(self):
        record = copy.deepcopy(self.record)
        record["recommendation"] = "ready_for_owner_decision"
        with self.assertRaisesRegex(ReviewTrackerError, "critical findings"):
            validate_review_record(record, self.manifest, self.root)


    def test_non_string_enum_values_block_cleanly(self):
        record = copy.deepcopy(self.record)
        record["findings"][0]["category"] = []
        with self.assertRaisesRegex(ReviewTrackerError, "unsupported category"):
            validate_review_record(record, self.manifest, self.root)

    def test_non_object_finding_blocks_cleanly(self):
        record = copy.deepcopy(self.record)
        record["findings"][0] = []
        with self.assertRaisesRegex(ReviewTrackerError, "must be an object"):
            validate_review_record(record, self.manifest, self.root)


if __name__ == "__main__":
    unittest.main()
