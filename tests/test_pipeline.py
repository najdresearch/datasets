import hashlib
import json
from pathlib import Path

import pytest

from najd_datasets.pipeline import PipelineError, clean, collect, generate, validate
from najd_datasets.release import check_approval, package


def test_collect_clean_and_package_preserves_provenance(tmp_path: Path):
    source_dir = tmp_path / "sources"
    source_dir.mkdir()
    rows = [
        {
            "id": "one",
            "track": "tool",
            "language": "ar",
            "prompt": "  ذكرني   غدًا ",
            "expected": {"tool": "remind"},
        },
        {
            "id": "two",
            "track": "tool",
            "language": "ar",
            "prompt": "ذكرني غدًا",
            "expected": {"tool": "remind"},
        },
    ]
    raw = source_dir / "raw.jsonl"
    raw.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    source = source_dir / "source.json"
    source.write_text(
        json.dumps(
            {
                "id": "own",
                "kind": "local",
                "path": "raw.jsonl",
                "origin": "original",
                "license": "CC-BY-4.0",
                "redistribution_basis": "owned",
                "rights_status": "approved",
                "split": "development",
                "revision": "v1",
                "schema_version": "1",
                "collection_method": "local_jsonl",
                "sha256": hashlib.sha256(raw.read_bytes()).hexdigest(),
                "review_status": "not_reviewed",
                "transformations": [],
            }
        )
    )
    collected = tmp_path / "collected.jsonl"
    collect(source, collected)
    cleaned = tmp_path / "cleaned.jsonl"
    report = clean([collected], cleaned)
    assert report["exact_duplicates_removed"] == 1
    assert validate(cleaned)["passed"]
    release = tmp_path / "release"
    manifest = package(cleaned, release, "demo", "v1")
    assert manifest["case_count"] == 1
    assert "source_row" in (release / "cases.jsonl").read_text()
    approval = tmp_path / "approval.json"
    approval.write_text(
        json.dumps(
            {
                "reviewer": "tester",
                "reviewed_at": "2026-09-25",
                "rights_approved": True,
                "privacy_approved": True,
                "semantic_review_approved": False,
                "target_repo": "najdresearch/najd-benchmark",
                "dataset_id": "demo",
                "version": "v1",
                "cases_sha256": manifest["cases_sha256"],
            }
        )
    )
    with pytest.raises(PipelineError):
        check_approval(release, approval, "najdresearch/najd-benchmark")
    data = json.loads(approval.read_text())
    data["semantic_review_approved"] = True
    approval.write_text(json.dumps(data))
    assert check_approval(release, approval, "najdresearch/najd-benchmark")["id"] == "demo"
    data["version"] = "v2"
    approval.write_text(json.dumps(data))
    with pytest.raises(PipelineError):
        check_approval(release, approval, "najdresearch/najd-benchmark")


def test_template_generation_is_deterministic(tmp_path: Path):
    spec = Path("fixtures/specs/reminder-variants.json")
    a, b = tmp_path / "a.jsonl", tmp_path / "b.jsonl"
    generate(spec, a)
    generate(spec, b)
    assert a.read_bytes() == b.read_bytes()
    assert validate(a)["passed"]


def test_pending_source_cannot_be_approved(tmp_path: Path):
    source_dir = tmp_path / "sources"
    source_dir.mkdir()
    raw = source_dir / "raw.jsonl"
    raw.write_text(
        json.dumps(
            {
                "id": "x",
                "track": "tool",
                "language": "en",
                "prompt": "Find a note",
                "expected": {"tool": "find_note"},
            }
        )
        + "\n"
    )
    source = source_dir / "source.json"
    source.write_text(
        json.dumps(
            {
                "id": "third-party",
                "kind": "local",
                "path": "raw.jsonl",
                "origin": "external",
                "license": "other",
                "redistribution_basis": "unverified",
                "rights_status": "pending",
                "split": "test",
                "revision": "v1",
                "schema_version": "1",
                "collection_method": "local_jsonl",
                "sha256": hashlib.sha256(raw.read_bytes()).hexdigest(),
                "review_status": "not_reviewed",
                "transformations": [],
            }
        )
    )
    collected, cleaned = tmp_path / "collected.jsonl", tmp_path / "cleaned.jsonl"
    collect(source, collected)
    clean([collected], cleaned)
    release = tmp_path / "release"
    manifest = package(cleaned, release, "demo", "v1")
    approval = tmp_path / "approval.json"
    approval.write_text(
        json.dumps(
            {
                "reviewer": "tester",
                "reviewed_at": "2026-09-25",
                "rights_approved": True,
                "privacy_approved": True,
                "semantic_review_approved": True,
                "target_repo": "najdresearch/najd-benchmark",
                "dataset_id": "demo",
                "version": "v1",
                "cases_sha256": manifest["cases_sha256"],
            }
        )
    )
    with pytest.raises(PipelineError, match="source or generation rights"):
        check_approval(release, approval, "najdresearch/najd-benchmark")
