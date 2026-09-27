import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from reconstruct_public_release import assemble  # noqa: E402

from najd_datasets import adapters  # noqa: E402


def entry():
    return {
        "id": "a",
        "source_id": "web",
        "split": "quarantine",
        "audit": {},
        "historical_metadata": {"provenance": {"sourceId": "web"}},
    }


def test_answers_come_from_source_and_target_content_is_forbidden():
    source = {"a": {"id": "a", "source_id": "web", "question_ar": "Q", "answer_ar": "A"}}
    result = assemble([entry()], {}, {}, {}, {}, source)
    assert result["quarantine"][0]["expected"] == {"answer": "A"}
    bad = entry()
    bad["historical_metadata"]["expected"] = {"answer": "target"}
    with pytest.raises(ValueError, match="forbidden"):
        assemble([bad], {}, {}, {}, {}, source)
    with pytest.raises(ValueError, match="Duplicate"):
        assemble([entry(), entry()], {}, {}, {}, {}, source)


def test_selection_contains_no_target_question_or_answer():
    selection = json.loads((ROOT / "releases/2026.09.14/public-selection.json").read_text())
    assert len(selection["rows"]) == 6089
    assert len({r["id"] for r in selection["rows"]}) == 6089
    for row in selection["rows"]:
        assert not {"prompt", "expected"} & row.keys()
        assert not {"prompt", "expected"} & row.get("historical_metadata", {}).keys()


def test_candidate_mode_never_fetches_published_reference(tmp_path, monkeypatch):
    # Use a real tiny adapter with its real validation hashes.
    raw = b'{"id":"a","prompt":"q","expected":{"answer":"a"}}\n'
    raw_path = tmp_path / "raw.jsonl"
    raw_path.write_bytes(raw)
    initial = tmp_path / "initial.jsonl"
    result = adapters.najd_v1_copy(raw_path, initial, "1.0.0")
    manifest = {
        "adapter": "najd-benchmark-v1-copy",
        "revision": "1.0.0",
        "raw_url": "https://example.org/1.0.0/raw.jsonl",
        "raw_sha256": adapters.digest(raw),
        "expected_rows": result["rows"],
        "expected_sha256": result["sha256"],
        "reference_url": "https://forbidden.invalid/target",
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))

    def fetch(url):
        assert url == manifest["raw_url"]
        return raw

    monkeypatch.setattr(adapters, "_fetch", fetch)
    assert adapters.reproduce_source(path, tmp_path / "out", candidates_only=True)["rows"] == 1


@pytest.mark.skipif(importlib.util.find_spec("pyarrow") is None, reason="parquet extra")
def test_parquet_roundtrip(tmp_path):
    import pyarrow.parquet as pq
    from reconstruct_public_release import export_parquet

    path = tmp_path / "cases.parquet"
    export_parquet([{"id": "x", "prompt": "سؤال", "expected": {"answer": "جواب"}}], path)
    row = pq.read_table(path).to_pylist()[0]
    assert row["prompt"] == "سؤال"
    assert json.loads(row["expected"]) == {"answer": "جواب"}
