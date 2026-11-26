"""Deterministic, no-network mock for the future NLP adapter contract."""
from __future__ import annotations

import json
from typing import Any


class MockLanguageModelAdapter:
    """Return a fixed fixture; never calls a model or inspects external systems."""

    def __init__(self, fixture: dict[str, Any]):
        self._fixture_json = json.dumps(fixture, ensure_ascii=False, allow_nan=False)

    def generate_structured(
        self,
        *,
        task_id: str,
        system_policy: str,
        input_text: str,
        output_schema: dict[str, Any],
        limits: dict[str, Any],
    ) -> str:
        # Inputs are accepted to mirror the future adapter interface. The mock
        # deliberately does not interpret them or execute instructions in them.
        if not all(isinstance(value, str) for value in (task_id, system_policy, input_text)):
            raise TypeError("task_id, system_policy and input_text must be strings")
        if not isinstance(output_schema, dict) or not isinstance(limits, dict):
            raise TypeError("output_schema and limits must be dictionaries")
        return self._fixture_json
