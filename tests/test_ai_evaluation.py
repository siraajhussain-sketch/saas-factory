import json
import unittest

from control_plane.ai_evaluation import evaluate_case, evaluate_dataset

CASE = {
    "case_id": "test-case-001",
    "language": "en",
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
        report = evaluate_dataset({"dataset_version": "1.1", "languages": ["en"], "cases": [CASE]}, {})
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

    def test_language_breakdown_is_reported(self):
        report = evaluate_dataset({"dataset_version": "1.1", "languages": ["en"], "cases": [CASE]}, {})
        self.assertEqual(report["language_summary"]["en"]["case_count"], 1)

    def test_unsupported_language_is_rejected(self):
        changed = dict(CASE)
        changed["language"] = "xx"
        with self.assertRaisesRegex(ValueError, "unsupported language"):
            evaluate_case(changed, json.dumps(GOOD))

    def test_unicode_arabic_and_urdu_terms_are_matched(self):
        arabic_case = {
            "case_id": "arabic-test-001", "language": "ar",
            "source_documents": {"brief-ar": "السوق المستهدف هو صالونات دبي."},
            "expected_findings": [{
                "item_id": "finding-ar-001", "category": "owner_fact",
                "source_document_id": "brief-ar",
                "supporting_excerpt": "السوق المستهدف هو صالونات دبي.",
                "statement_must_include": ["صالونات دبي"],
            }],
        }
        arabic_output = {"schema_version": "1.0", "findings": [{
            "item_id": "finding-ar-001", "category": "owner_fact",
            "statement": "السوق المستهدف هو صالونات دبي.",
            "source_document_id": "brief-ar", "source_location": None,
            "supporting_excerpt": "السوق المستهدف هو صالونات دبي.",
            "model_confidence": None, "reviewer_status": "unreviewed",
            "reviewer_note": None, "reviewed_at": None,
        }]}
        result = evaluate_case(arabic_case, json.dumps(arabic_output, ensure_ascii=False))
        self.assertEqual(result["term_coverage"], 1.0)

        urdu_case = {
            "case_id": "urdu-test-001", "language": "ur",
            "source_documents": {"brief-ur": "ہمارے صارفین چھوٹے سیلون ہیں۔"},
            "expected_findings": [{
                "item_id": "finding-ur-001", "category": "owner_fact",
                "source_document_id": "brief-ur",
                "supporting_excerpt": "ہمارے صارفین چھوٹے سیلون ہیں۔",
                "statement_must_include": ["چھوٹے سیلون"],
            }],
        }
        urdu_output = {"schema_version": "1.0", "findings": [{
            "item_id": "finding-ur-001", "category": "owner_fact",
            "statement": "ہمارے صارفین چھوٹے سیلون ہیں۔",
            "source_document_id": "brief-ur", "source_location": None,
            "supporting_excerpt": "ہمارے صارفین چھوٹے سیلون ہیں۔",
            "model_confidence": None, "reviewer_status": "unreviewed",
            "reviewer_note": None, "reviewed_at": None,
        }]}
        result = evaluate_case(urdu_case, json.dumps(urdu_output, ensure_ascii=False))
        self.assertEqual(result["term_coverage"], 1.0)


if __name__ == "__main__":
    unittest.main()
