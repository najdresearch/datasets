import json
from pathlib import Path

import pytest

from najd_datasets.saudi_decisions import build

SOURCE = Path(__file__).parents[1] / "fixtures/saudi-decisions/families.json"


def test_aligned_reproducible_drafts(tmp_path):
    first = build(SOURCE, tmp_path / "a")
    second = build(SOURCE, tmp_path / "b")
    assert first == second
    assert first["cases"] == 120 and first["families"] == 40
    assert set(first["domains"].values()) == {5}
    assert not first["publication_eligible"]
    rows = [json.loads(x) for x in (tmp_path / "a/cases.jsonl").read_text().splitlines()]
    assert len({r["id"] for r in rows}) == 120
    for start in range(0, 120, 3):
        group = rows[start : start + 3]
        assert {r["register"] for r in group} == {"en", "ar-MSA", "ar-SA"}
        assert len({r["expected"]["action"] for r in group}) == 1
        assert all(r["split"] == "development" and r["reviewer"] is None for r in group)
    with pytest.raises(FileExistsError):
        build(SOURCE, tmp_path / "a")


def test_reject_invalid_alignment_and_gold(tmp_path):
    original = json.loads(SOURCE.read_text())
    for mutation in ("variant", "gold", "duplicate", "split"):
        data = json.loads(json.dumps(original))
        if mutation == "variant":
            del data[0]["requests"]["ar-SA"]
        elif mutation == "gold":
            data[0]["expected"] = "not-an-option"
        elif mutation == "duplicate":
            data.append(data[0])
        else:
            data[0]["split"] = "test"
        source = tmp_path / (mutation + ".json")
        source.write_text(json.dumps(data))
        with pytest.raises(ValueError):
            build(source, tmp_path / mutation)


def test_typed_extension_and_safety(tmp_path):
    source = SOURCE.with_name("families-v0.3.json")
    manifest = build(source, tmp_path / "typed")
    assert manifest["cases"] == 144
    assert manifest["question_types"] == {"choice": 40, "noul": 4, "score": 4}
    rows = [json.loads(x) for x in (tmp_path / "typed/cases.jsonl").read_text().splitlines()]
    booleans = [r for r in rows if r["questions"]["action"]["type"] == "noul"]
    assert sum(r["expected"]["action"] for r in booleans) == 6
    assert all(type(r["expected"]["action"]) is bool for r in booleans)
    assert any(r["unsafe_values"]["action"] == [True] for r in booleans)
    scores = [r for r in rows if r["questions"]["action"]["type"] == "score"]
    assert {r["expected"]["action"] for r in scores} == {0, 1, 2, 3}
    for r in rows:
        assert r["expected"]["action"] not in r["unsafe_values"]["action"]


def test_reviewed_revision_preserves_gold_and_covers_unauthorized_actions(tmp_path):
    source = SOURCE.with_name("families-v0.4.json")
    manifest = build(source, tmp_path / "reviewed")
    assert manifest["task_pack"] == "saudi-decisions-draft-v0.4"
    old = {f["id"]: f for f in json.loads(SOURCE.with_name("families-v0.3.json").read_text())}
    new = {f["id"]: f for f in json.loads(source.read_text())}
    assert {k: v["expected"] for k, v in old.items()} == {k: v["expected"] for k, v in new.items()}
    assert "withdraw" in new["N0301"]["unsafe"]
    assert "cancel" in new["N0501"]["unsafe"]
    assert "submit" in new["N0304"]["unsafe"]
    assert not manifest["publication_eligible"]
    for f in new.values():
        values = f.get("unsafe_values", f.get("unsafe", []))
        assert not any(type(v) is type(f["expected"]) and v == f["expected"] for v in values)


def test_expanded_policies_and_provisional_acceptance(tmp_path):
    source = SOURCE.with_name("families-v0.5.json")
    manifest = build(source, tmp_path / "expanded")
    assert manifest["families"] == 72 and manifest["cases"] == 216
    assert manifest["policy_groups"] == 15
    assert manifest["question_types"] == {"choice": 40, "noul": 16, "score": 16}
    assert manifest["acceptance_status_counts"] == {
        "user_provisionally_accepted": 48,
        "new_draft": 24,
    }
    families = json.loads(source.read_text())
    booleans = [f["expected"] for f in families if f.get("question_type") == "noul"]
    assert booleans.count(True) == booleans.count(False) == 8
    scores = [f["expected"] for f in families if f.get("question_type") == "score"]
    assert all(scores.count(level) == 4 for level in range(4))
    rows = [json.loads(x) for x in (tmp_path / "expanded/cases.jsonl").read_text().splitlines()]
    assert all(r["independent_review"] == "pending" for r in rows)
    assert not manifest["publication_eligible"]


def test_reject_misaligned_scales_and_unsafe_gold(tmp_path):
    source = SOURCE.with_name("families-v0.5.json")
    data = json.loads(source.read_text())
    ordinal = next(f for f in data if f.get("question_type") == "score")
    ordinal["score_criteria"]["ar"].pop()
    broken = tmp_path / "broken.json"
    broken.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="scales must align"):
        build(broken, tmp_path / "bad-scale")
    data = json.loads(source.read_text())
    data[0]["unsafe_values"] = [data[0]["expected"]]
    broken.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="cannot also be unsafe"):
        build(broken, tmp_path / "bad-safety")
