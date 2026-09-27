import runpy
from pathlib import Path

import pytest

AUDIT = runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "scripts/audit_public_reconstruction.py")
)


def test_content_comparison_rejects_changed_answers_and_missing_extra_ids():
    result = AUDIT["compare_subset"](
        [{"id": "a", "expected": {"answer": "one"}}, {"id": "b", "expected": {}}],
        [{"id": "a", "expected": {"answer": "two"}}, {"id": "c", "expected": {}}],
        ["expected"],
    )
    assert not result["passed"]
    assert result["changed_ids"] == ["a"]
    assert result["missing_ids"] == ["b"]
    assert result["extra_ids"] == ["c"]


def test_duplicate_ids_fail_instead_of_being_silently_dropped():
    with pytest.raises(ValueError, match="Duplicate"):
        AUDIT["index_unique"]([{"id": "a"}, {"id": "a"}])
