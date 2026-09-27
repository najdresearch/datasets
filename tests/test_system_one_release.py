import copy
import json
from collections import Counter, defaultdict
from pathlib import Path

import pytest

from najd_datasets.system_one_audit import audit
from najd_datasets.system_one_references import stratified
from najd_datasets.system_one_release import build, synthesize

ROOT = Path(__file__).parents[1]


def test_controlled_rules_and_split_groups():
    rows = synthesize(json.loads((ROOT / "fixtures/system-one-v1/policies.json").read_text()))
    assert len(rows) == 2400
    assert Counter(r["split"] for r in rows) == {
        "development": 600,
        "validation": 600,
        "reserved_evaluation": 1200,
    }
    groups = defaultdict(set)
    for r in rows:
        groups[r["template_group"]].add(r["split"])
        pattern = r["provenance"]["pattern"]
        kind = r["questions"]["action"]["type"]
        gold = r["expected"]["action"]
        if pattern == 0:
            assert gold == (True if kind == "noul" else "proceed" if kind == "choice" else 0)
        if pattern == 8:  # unknown requirement: clarify; inverted Boolean means hold.
            assert gold == (True if kind == "noul" else "clarify" if kind == "choice" else 1)
        if pattern == 9:  # false takes precedence over unknown.
            assert gold == (False if kind == "noul" else "block" if kind == "choice" else 2)
    assert len(groups) == 80 and all(len(v) == 1 for v in groups.values())


def test_deterministic_build_and_tamper_detection(tmp_path):
    build(ROOT, tmp_path / "first")
    build(ROOT, tmp_path / "second")
    first = audit(tmp_path / "first")
    second = audit(tmp_path / "second")
    assert first == second
    assert first["cases"] == 2616
    path = tmp_path / "first/controlled-development/cases.jsonl"
    path.write_text(path.read_text() + "\n")
    with pytest.raises(ValueError, match="Hash mismatch"):
        audit(tmp_path / "first")


def test_stratified_selection_stable_and_capped():
    rows = [{"id": str(i), "label": i % 3} for i in range(30)]
    selected = stratified(rows, lambda r: r["label"], lambda r: r["id"], 4)
    assert selected == stratified(list(reversed(rows)), lambda r: r["label"], lambda r: r["id"], 4)
    assert Counter(r["label"] for r in selected) == {0: 4, 1: 4, 2: 4}


def test_catalog_identity_guard():
    data = json.loads((ROOT / "fixtures/system-one-v1/policies.json").read_text())
    data[1] = copy.deepcopy(data[0])
    with pytest.raises(ValueError, match="80 unique"):
        synthesize(data)
