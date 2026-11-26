"""Strict, provenance-aware validation for untrusted NLP model output.

This module is deliberately provider-independent and has no I/O or side effects.
It validates structure and source-span provenance; it does not verify truth.
"""
from __future__ import annotations

import json
import math
import re
from typing import Any, Mapping

SCHEMA_VERSION = "1.0"
CATEGORIES = {
    "owner_fact", "sourced_fact_candidate", "assumption",
    "hypothesis", "recommendation", "unknown",
}
REVIEWER_STATUS = "unreviewed"
MAX_PAYLOAD_BYTES = 256_000
MAX_FINDINGS = 100
MAX_STATEMENT = 4_000
MAX_EXCERPT = 2_000
MAX_LOCATION = 500
MAX_DOCUMENTS = 50
MAX_DOCUMENT_CHARS = 100_000
ID_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{2,63}$")
FINDING_FIELDS = {
    "item_id", "category", "statement", "source_document_id",
    "source_location", "supporting_excerpt", "model_confidence",
    "reviewer_status", "reviewer_note", "reviewed_at",
}
ROOT_FIELDS = {"schema_version", "findings"}


class AIOutputValidationError(ValueError):
    """Raised when untrusted structured output violates the contract."""


def _reject_constant(value: str) -> None:
    raise AIOutputValidationError(f"non-finite JSON number is not allowed: {value}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AIOutputValidationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _is_optional_string(value: Any, maximum: int, field: str) -> bool:
    if value is None:
        return True
    if not isinstance(value, str) or len(value) > maximum:
        raise AIOutputValidationError(f"{field} must be null or a string of at most {maximum} characters")
    return True


def parse_and_validate_output(
    raw_json: str,
    source_documents: Mapping[str, str],
) -> dict[str, Any]:
    """Parse strict JSON and validate findings against supplied source documents."""
    if not isinstance(raw_json, str):
        raise AIOutputValidationError("model output must be a JSON string")
    if len(raw_json.encode("utf-8")) > MAX_PAYLOAD_BYTES:
        raise AIOutputValidationError("model output exceeds the byte limit")
    if not isinstance(source_documents, Mapping) or len(source_documents) > MAX_DOCUMENTS:
        raise AIOutputValidationError("source_documents must be a mapping of at most 50 documents")
    for doc_id, text in source_documents.items():
        if not isinstance(doc_id, str) or not ID_PATTERN.fullmatch(doc_id):
            raise AIOutputValidationError("source document ID is invalid")
        if not isinstance(text, str) or len(text) > MAX_DOCUMENT_CHARS:
            raise AIOutputValidationError(f"source document {doc_id} is invalid or too large")

    try:
        payload = json.loads(
            raw_json,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except AIOutputValidationError:
        raise
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise AIOutputValidationError("model output is not valid JSON") from exc

    if not isinstance(payload, dict) or set(payload) != ROOT_FIELDS:
        raise AIOutputValidationError("root must contain exactly schema_version and findings")
    if payload["schema_version"] != SCHEMA_VERSION:
        raise AIOutputValidationError("unsupported schema_version")
    findings = payload["findings"]
    if not isinstance(findings, list) or not findings or len(findings) > MAX_FINDINGS:
        raise AIOutputValidationError("findings must contain between 1 and 100 items")

    seen_ids: set[str] = set()
    for index, finding in enumerate(findings):
        prefix = f"findings[{index}]"
        if not isinstance(finding, dict) or set(finding) != FINDING_FIELDS:
            raise AIOutputValidationError(f"{prefix} must contain exactly the defined fields")

        item_id = finding["item_id"]
        if not isinstance(item_id, str) or not ID_PATTERN.fullmatch(item_id):
            raise AIOutputValidationError(f"{prefix}.item_id is invalid")
        if item_id in seen_ids:
            raise AIOutputValidationError(f"{prefix}.item_id is duplicated")
        seen_ids.add(item_id)

        if not isinstance(finding["category"], str) or finding["category"] not in CATEGORIES:
            raise AIOutputValidationError(f"{prefix}.category is unsupported")
        statement = finding["statement"]
        if not isinstance(statement, str) or not statement.strip() or len(statement) > MAX_STATEMENT:
            raise AIOutputValidationError(f"{prefix}.statement is empty or too long")

        doc_id = finding["source_document_id"]
        location = finding["source_location"]
        excerpt = finding["supporting_excerpt"]
        _is_optional_string(location, MAX_LOCATION, f"{prefix}.source_location")
        _is_optional_string(excerpt, MAX_EXCERPT, f"{prefix}.supporting_excerpt")

        if doc_id is not None:
            if not isinstance(doc_id, str) or doc_id not in source_documents:
                raise AIOutputValidationError(f"{prefix}.source_document_id is not in supplied sources")
            if not isinstance(excerpt, str) or not excerpt:
                raise AIOutputValidationError(f"{prefix} needs an exact excerpt when a source is named")
            if excerpt not in source_documents[doc_id]:
                raise AIOutputValidationError(f"{prefix}.supporting_excerpt is not an exact source substring")
        elif location is not None or excerpt is not None:
            raise AIOutputValidationError(f"{prefix} cannot include a location or excerpt without a source document")

        if finding["category"] in {"owner_fact", "sourced_fact_candidate"} and doc_id is None:
            raise AIOutputValidationError(f"{prefix} requires source provenance for this category")

        confidence = finding["model_confidence"]
        if confidence is not None:
            if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
                raise AIOutputValidationError(f"{prefix}.model_confidence must be a number or null")
            if not math.isfinite(confidence) or not 0 <= confidence <= 1:
                raise AIOutputValidationError(f"{prefix}.model_confidence must be between 0 and 1")

        if finding["reviewer_status"] != REVIEWER_STATUS:
            raise AIOutputValidationError(f"{prefix}.reviewer_status must remain unreviewed")
        if finding["reviewer_note"] is not None or finding["reviewed_at"] is not None:
            raise AIOutputValidationError(f"{prefix} cannot contain human review metadata")

    return payload
