"""Read-only, provider-independent scoring for fixed multilingual NLP evaluation cases."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from control_plane.ai_output_contract import AIOutputValidationError, parse_and_validate_output

SUPPORTED_LANGUAGES = {"en", "ar", "ur", "mixed"}


def _normalized_terms(value: str) -> str:
    return " ".join(value.casefold().split())


def evaluate_case(case: Mapping[str, Any], raw_output: str) -> dict[str, Any]:
    case_id = case.get("case_id")
    language = case.get("language")
    expected = case.get("expected_findings")
    sources = case.get("source_documents")
    if (not isinstance(case_id, str) or language not in SUPPORTED_LANGUAGES
            or not isinstance(expected, list) or not isinstance(sources, dict)):
        raise ValueError("evaluation case has an invalid structure or unsupported language")

    try:
        parsed = parse_and_validate_output(raw_output, sources)
    except AIOutputValidationError as exc:
        return {
            "case_id": case_id, "language": language, "valid": False,
            "validation_error": str(exc), "expected_count": len(expected),
            "matched_count": 0, "extra_count": 0, "category_accuracy": 0.0,
            "provenance_accuracy": 0.0, "term_coverage": 0.0,
        }

    actual_by_id = {item["item_id"]: item for item in parsed["findings"]}
    expected_ids = {item["item_id"] for item in expected}
    matched = category_hits = provenance_hits = term_hits = term_total = 0

    for gold in expected:
        actual = actual_by_id.get(gold["item_id"])
        terms = gold.get("statement_must_include", [])
        term_total += len(terms)
        if actual is None:
            continue
        matched += 1
        category_hits += actual["category"] == gold["category"]
        provenance_hits += (
            actual["source_document_id"] == gold["source_document_id"]
            and actual["supporting_excerpt"] == gold["supporting_excerpt"]
        )
        normalized_statement = _normalized_terms(actual["statement"])
        for term in terms:
            term_hits += _normalized_terms(term) in normalized_statement

    expected_count = len(expected)
    return {
        "case_id": case_id, "language": language, "valid": True,
        "expected_count": expected_count, "actual_count": len(parsed["findings"]),
        "matched_count": matched, "missing_count": expected_count - matched,
        "extra_count": len(set(actual_by_id) - expected_ids),
        "category_accuracy": round(category_hits / expected_count, 3) if expected_count else 0.0,
        "provenance_accuracy": round(provenance_hits / expected_count, 3) if expected_count else 0.0,
        "term_coverage": round(term_hits / term_total, 3) if term_total else 0.0,
    }


def evaluate_dataset(dataset: Mapping[str, Any], outputs: Mapping[str, str]) -> dict[str, Any]:
    if (dataset.get("dataset_version") != "1.1"
            or not isinstance(dataset.get("cases"), list)
            or not isinstance(dataset.get("languages"), list)
            or not set(dataset["languages"]).issubset(SUPPORTED_LANGUAGES)):
        raise ValueError("unsupported or malformed evaluation dataset")
    results = []
    for case in dataset["cases"]:
        case_id = case.get("case_id")
        raw = outputs.get(case_id) if isinstance(case_id, str) else None
        if raw is None:
            results.append({
                "case_id": case_id, "language": case.get("language"), "valid": False,
                "validation_error": "missing candidate output",
                "expected_count": len(case.get("expected_findings", [])),
                "matched_count": 0, "extra_count": 0, "category_accuracy": 0.0,
                "provenance_accuracy": 0.0, "term_coverage": 0.0,
            })
        else:
            results.append(evaluate_case(case, raw))

    language_summary = {}
    for language in dataset["languages"]:
        language_results = [r for r in results if r.get("language") == language]
        valid = [r for r in language_results if r["valid"]]
        language_summary[language] = {
            "case_count": len(language_results),
            "valid_case_count": len(valid),
            "average_category_accuracy": round(sum(r["category_accuracy"] for r in valid) / len(valid), 3) if valid else None,
            "average_provenance_accuracy": round(sum(r["provenance_accuracy"] for r in valid) / len(valid), 3) if valid else None,
            "average_term_coverage": round(sum(r["term_coverage"] for r in valid) / len(valid), 3) if valid else None,
        }

    valid_results = [result for result in results if result["valid"]]
    return {
        "dataset_version": dataset["dataset_version"],
        "case_count": len(results), "valid_case_count": len(valid_results),
        "language_summary": language_summary, "results": results,
        "limitations": [
            "This small hand-authored set is illustrative, not statistically representative.",
            "Arabic cases currently include Modern Standard Arabic and one synthetic Gulf/Emirati-style colloquial example; this is not broad dialect coverage.",
            "Term coverage is a lexical proxy, not semantic correctness; Arabic morphology and spelling variants need richer evaluation.",
            "A valid excerpt proves substring presence, not faithful interpretation.",
            "Scores do not verify factual truth, source quality, safety, or model confidence calibration.",
            "Human review by fluent speakers remains mandatory.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Score candidate NLP outputs against a local evaluation dataset.")
    parser.add_argument("--dataset", required=True, help="Path to the hand-authored evaluation dataset JSON")
    parser.add_argument("--outputs", required=True, help="Path to JSON object mapping case IDs to candidate output objects")
    args = parser.parse_args()
    dataset = json.loads(Path(args.dataset).read_text(encoding="utf-8"))
    output_objects = json.loads(Path(args.outputs).read_text(encoding="utf-8"))
    if not isinstance(output_objects, dict):
        parser.error("--outputs must contain a JSON object")
    outputs = {
        case_id: json.dumps(value, ensure_ascii=False, allow_nan=False)
        for case_id, value in output_objects.items()
    }
    report = evaluate_dataset(dataset, outputs)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["valid_case_count"] == report["case_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
