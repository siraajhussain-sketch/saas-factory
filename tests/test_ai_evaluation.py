import json
import unittest

from control_plane.ai_evaluation import evaluate_case, evaluate_dataset

CASE = {
    "case_id": "test-case-001",
    "source_documents": {"brief-test": "Target customers are local salons."},
    "expected_findings": [{
        "item_id": "finding-target-001",
        "category": "owner_fact",
        "source_document_id": "brief-test",
        "supporting_excerpt": "Target customers are local salons.",
        "statement_must_include": ["local salons"],
    }],
}
GOOD = {
    "schema_version": "1.0",
    "findings": [{
        "item_id": "finding-target-001",
        "category": "owner_fact",
        "statement": "The brief identifies local salons as target customers.",
        "source_document_id": "brief-test",
        "source_location": "Brief",
        "supporting_excerpt": "Target customers are local salons.",
        "model_confidence": 0.7,
        "reviewer_status": "unreviewed",
        "reviewer_note": None,
        "reviewed_at": None,
    }],
}


class AIEvaluationTests(unittest.TestCase):
    def test_exact_candidate_scores_full_credit(self):
        result = evaluate_case(CASE, json.dumps(GOOD))
        self.assertTrue(result["valid"])
        self.assertEqual(result["category_accuracy"], 1.0)
        self.assertEqual(result["provenance_accuracy"], 1.0)
        self.assertEqual(result["term_coverage"], 1.0)
        self.assertEqual(result["extra_count"], 0)

    def test_missing_output_is_reported_not_fabricated(self):
        report = evaluate_dataset({"dataset_version": "1.0", "cases": [CASE]}, {})
        self.assertEqual(report["valid_case_count"], 0)
        self.assertEqual(report["results"][0]["validation_error"], "missing candidate output")

    def test_extra_findings_are_counted(self):
        changed = json.loads(json.dumps(GOOD))
        extra = dict(changed["findings"][0])
        extra["item_id"] = "finding-extra-001"
        changed["findings"].append(extra)
        result = evaluate_case(CASE, json.dumps(changed))
        self.assertEqual(result["extra_count"], 1)

    def test_wrong_category_lowers_category_score(self):
        changed = json.loads(json.dumps(GOOD))
        changed["findings"][0]["category"] = "hypothesis"
        result = evaluate_case(CASE, json.dumps(changed))
        self.assertEqual(result["category_accuracy"], 0.0)

    def test_bad_provenance_is_invalid(self):
        changed = json.loads(json.dumps(GOOD))
        changed["findings"][0]["supporting_excerpt"] = "not in source"
        result = evaluate_case(CASE, json.dumps(changed))
        self.assertFalse(result["valid"])


if __name__ == "__main__":
    unittest.main()
