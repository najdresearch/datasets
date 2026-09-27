import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_unified_release import unify  # noqa: E402


def test_only_status_is_removed_and_all_cases_are_kept():
    records = [
        {"id": "a", "audit_status": "certified", "prompt": "A", "expected": {"answer": 0}},
        {"id": "b", "audit_status": "quarantined", "audit_issues": ["missing_expected_answer"]},
    ]
    result = unify(records)
    assert result == [{k: v for k, v in r.items() if k != "audit_status"} for r in records]
    assert len(result) == 2
    assert records[0]["audit_status"] == "certified"
    with pytest.raises(ValueError, match="Duplicate"):
        unify(records + records[:1])
