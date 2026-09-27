import json
from pathlib import Path

import pytest

from najd_datasets.audit import audit_public_inputs
from najd_datasets.pipeline import PipelineError


def test_historical_inventory_does_not_claim_reconstruction():
    root = Path(__file__).resolve().parents[1]
    report = audit_public_inputs(root / "releases/2026.09.14/sources.json", root / "sources")
    assert report["case_count"] == 6089
    assert report["totals"] == {
        "public_input_declared_unverified": 5725,
        "no_public_pinned_raw_input": 31,
        "missing_source_manifest": 333,
    }
    assert report["public_reconstruction_complete"] is False


def test_inventory_rejects_inconsistent_release(tmp_path):
    release = tmp_path / "release.json"
    release.write_text(json.dumps({"case_count": 2, "sources": [
        {"source_id": "private", "case_count": 1}
    ]}))
    with pytest.raises(PipelineError, match="counts"):
        audit_public_inputs(release, tmp_path / "sources")


def test_reference_copy_is_not_a_public_source(tmp_path):
    sources = tmp_path / "sources"
    sources.mkdir()
    (sources / "a.json").write_text(json.dumps({
        "source_id": "a", "adapter": "copy", "reference_url": "https://example.org/cases",
        "reference_sha256": "a" * 64,
    }))
    release = tmp_path / "release.json"
    release.write_text(json.dumps({"case_count": 1, "sources": [
        {"source_id": "a", "case_count": 1}
    ]}))
    assert audit_public_inputs(release, sources)["totals"] == {"no_public_pinned_raw_input": 1}
