import json
from pathlib import Path

import pytest

from najd_datasets.adapters import (
    _selected_candidate,
    _with_correction,
    arabic_agent_eval,
    arabic_ragb,
    islamic_faith_qa,
    paired_tool_use,
    reproduce_source,
)
from najd_datasets.pipeline import PipelineError, digest


def test_arabic_agent_adapter_matches_reference_and_detects_drift(tmp_path: Path, monkeypatch):
    raw = (
        json.dumps(
            {
                "id": "simple_001",
                "instruction": "ابحث عن رحلة",
                "category": "simple_function_calling",
                "dialect": "msa",
                "expected_calls": [{"function": "search_flights", "arguments": {}}],
                "difficulty": "easy",
            },
            ensure_ascii=False,
        ) + "\n"
    ).encode()
    revision = "a" * 40
    original = tmp_path / "original.jsonl"
    original.write_bytes(raw)
    expected = tmp_path / "expected.jsonl"
    report = arabic_agent_eval(original, expected, revision)
    assert report["rows"] == 1
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "adapter": "arabic-agent-eval-v1",
                "revision": revision,
                "raw_url": f"https://example.org/{revision}/all.jsonl",
                "raw_sha256": digest(raw),
                "expected_rows": 1,
                "expected_sha256": report["sha256"],
                "reference_sha256": digest(expected.read_bytes()),
            }
        )
    )

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return None

        def read(self):
            return raw

    monkeypatch.setattr("najd_datasets.adapters.urlopen", lambda *_args, **_kwargs: Response())
    result = reproduce_source(manifest, tmp_path / "run", expected)
    assert result["published_rows_matched"] == 1
    assert reproduce_source(manifest, tmp_path / "local", expected, original)[
        "published_rows_matched"
    ] == 1
    wrong_raw = tmp_path / "wrong.jsonl"
    wrong_raw.write_bytes(raw + b"\n")
    with pytest.raises(PipelineError, match="upstream source SHA-256 mismatch"):
        reproduce_source(manifest, tmp_path / "wrong-raw", expected, wrong_raw)
    reference = json.loads(expected.read_text())
    reference["expected"]["tool_calls"] = []
    expected.write_text(json.dumps(reference, ensure_ascii=False) + "\n")
    with pytest.raises(PipelineError, match="published reference SHA-256 mismatch"):
        reproduce_source(manifest, tmp_path / "drift", expected)


def test_paired_adapter_preserves_variant_and_expected_action(tmp_path: Path):
    raw = tmp_path / "source.jsonl"
    raw.write_text(json.dumps({
        "variant_id": "pair_1_msa", "scenario_id": "scn_1",
        "user_request": "ما حالة الطقس؟", "language": "ar", "variety": "msa",
        "expected": {"action": "ask_clarification", "tool_name": "get_weather"},
    }, ensure_ascii=False) + "\n")
    output = tmp_path / "cases.jsonl"
    report = paired_tool_use(raw, output, "a" * 40)
    row = json.loads(output.read_text())
    assert report["rows"] == 1
    assert row["id"] == "tool-use-pair_1_msa"
    assert row["expected"]["action"] == "ask_clarification"
    assert row["provenance"]["scenarioId"] == "scn_1"


def test_faith_adapter_preserves_original_row_numbers_when_skipping_empty_prompt(tmp_path: Path):
    raw = tmp_path / "source.jsonl"
    raw.write_text(
        json.dumps({"question": "", "gold_answer": ""}) + "\n"
        + json.dumps({
            "question": "ما السؤال؟", "gold_answer": "هذا الجواب", "category_type": "faith",
        }, ensure_ascii=False) + "\n"
    )
    output = tmp_path / "cases.jsonl"
    report = islamic_faith_qa(raw, output, "a" * 40)
    row = json.loads(output.read_text())
    assert report["rows"] == 1
    assert row["id"] == "islamicfaithqa-ar-00002"
    assert row["provenance"]["sourceRow"] == 2
    assert "audit_status" not in row


def test_ragb_review_copy_is_checked_against_upstream_candidate(tmp_path: Path, monkeypatch):
    revision = "b" * 40
    raw = (json.dumps({
        "id": "r_1", "query": "ما السؤال؟", "passage_text": "هذا السياق",
        "passage_id": "p_1", "query_dialect": "msa",
    }, ensure_ascii=False) + "\n").encode()
    raw_path = tmp_path / "raw.jsonl"
    raw_path.write_bytes(raw)
    candidates = tmp_path / "candidates.jsonl"
    result = arabic_ragb(raw_path, candidates, revision)
    base = json.loads(candidates.read_text())
    published = {
        **base,
        "id": base["id"] + "-review-copy",
        "derived_from_candidate_id": base["id"],
        "provenance": {**base["provenance"], "derived_from_candidate": True},
        "audit_status": "certified",
        "audit_issues": [],
    }
    reference = (json.dumps(published, ensure_ascii=False) + "\n").encode()
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({
        "adapter": "arabic-ragb-v1", "revision": revision,
        "raw_url": f"https://example.org/{revision}/raw.jsonl",
        "raw_sha256": digest(raw), "expected_rows": 1,
        "expected_sha256": result["sha256"],
        "selection_mode": "derived_review_copy", "expected_published_rows": 1,
        "reference_url": "https://example.org/reference.jsonl",
        "reference_sha256": digest(reference),
    }))

    class Response:
        def __init__(self, data):
            self.data = data

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return None

        def read(self):
            return self.data

    monkeypatch.setattr(
        "najd_datasets.adapters.urlopen",
        lambda url, **_: Response(raw if "raw.jsonl" in url else reference),
    )
    assert reproduce_source(manifest, tmp_path / "run")["published_rows_matched"] == 1


def test_recorded_correction_changes_only_prompt_and_options():
    raw = {"id": "case", "prompt": "old", "expected": {"answerIndex": 3, "options": ["M1"]}}
    repaired = _with_correction(raw, {"prompt": "new", "expected_options": ["first"]})
    assert repaired == {
        "id": "case", "prompt": "new",
        "expected": {"answerIndex": 3, "options": ["first"]},
    }
    assert raw["prompt"] == "old"


def test_selected_case_metadata_and_repairs_are_explicit():
    candidate = {
        "id": "case", "prompt": "old", "expected": {"answer": None},
        "tags": ["arabic", ""],
    }
    manifest = {
        "selected_metadata": {"derived_from_candidate": True},
        "selected_metadata_except_ids": ["other"],
        "selected_remove_empty_tags": True,
        "case_overrides": {"case": {"prompt": "clean", "expected": {"answer": "A"}}},
    }
    assert _selected_candidate(candidate, "case", manifest) == {
        "id": "case", "prompt": "clean", "expected": {"answer": "A"},
        "tags": ["arabic"], "derived_from_candidate": True,
    }
    assert candidate["prompt"] == "old"
    assert "derived_from_candidate" not in _selected_candidate(
        candidate, "other", manifest,
    )
