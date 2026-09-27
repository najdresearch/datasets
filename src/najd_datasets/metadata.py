"""Remove retired review annotations without altering evaluation content."""

from __future__ import annotations

from typing import Any

RETIRED_FIELDS = frozenset(
    {"review_status", "semantic_review", "bilingual_review_status", "islamic_expert_review_status"}
)


def without_review_metadata(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: without_review_metadata(item)
            for key, item in value.items()
            if key not in RETIRED_FIELDS
        }
    if isinstance(value, list):
        return [without_review_metadata(item) for item in value]
    return value
