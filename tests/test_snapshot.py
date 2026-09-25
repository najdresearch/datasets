import csv
import json
from pathlib import Path

import pytest

from najd_datasets.pipeline import PipelineError
from najd_datasets.snapshot import _coverage


def test_coverage_accounts_for_every_case_and_detects_duplicate_ids(tmp_path: Path):
    source = {
        "source_id": "arabic-agent-eval",
        "source_files": ["sources/github/arabic-agent-eval/data/all.jsonl"],
        "certified_case_count": 1,
        "quarantine_case_count": 1,
    }
    (tmp_path / "sources.json").write_text(json.dumps({
        "sources": [source], "certified_case_count": 1, "quarantine_case_count": 1,
    }))
    case = {
        "id": "one", "audit_status": "certified",
        "provenance": {"sourceId": "arabic-agent-eval", "sourceFile": "data/all.jsonl"},
    }
    quarantine = {**case, "id": "two", "audit_status": "quarantined"}
    (tmp_path / "cases.jsonl").write_text(json.dumps(case) + "\n")
    (tmp_path / "quarantine.jsonl").write_text(json.dumps(quarantine) + "\n")
    report = _coverage(tmp_path, tmp_path / "case-index.csv")
    assert report["total_rows"] == 2
    assert report["missing_source_row"] == 2
    assert report["upstream_rebuild_row_counts"]["upstream_reproduced"] == 2
    with (tmp_path / "case-index.csv").open() as handle:
        assert len(list(csv.DictReader(handle))) == 2
    quarantine["id"] = "one"
    (tmp_path / "quarantine.jsonl").write_text(json.dumps(quarantine) + "\n")
    with pytest.raises(PipelineError, match="duplicate case ID"):
        _coverage(tmp_path, tmp_path / "case-index.csv")


def test_pinned_release_coverage_has_no_adapter_gap():
    from najd_datasets.snapshot import UPSTREAM_REPRODUCED_SOURCES

    ledger = json.loads(Path("releases/2026.09.14/sources.json").read_text())
    source_ids = {item["source_id"] for item in ledger["sources"]}
    private_extract_ids = {
        item["source_id"] for item in ledger["sources"]
        if any(
            path.startswith("private/authorized-source-extracts/")
            for path in item["source_files"]
        )
    }
    assert source_ids == (
        UPSTREAM_REPRODUCED_SOURCES | private_extract_ids | {"najd-benchmark-v1"}
    )
    assert len(UPSTREAM_REPRODUCED_SOURCES) == 29
