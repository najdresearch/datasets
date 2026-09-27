import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def test_rights_register_covers_release_and_has_real_evidence_links():
    register = json.loads((ROOT / "releases/source-rights-evidence.json").read_text())
    historical = json.loads((ROOT / "releases/2026.09.14/sources.json").read_text())
    expected = {r["source_id"]: r["case_count"] for r in historical["sources"]}
    assert {r["source_id"]: r["rows"] for r in register["sources"]} == expected
    assert len(register["sources"]) == 39
    assert sum(r["rows"] for r in register["sources"]) == 6089
    for row in register["sources"]:
        assert urlparse(row["source_url"]).scheme == "https"
        if row["status"] == "public_license_evidence":
            assert row["license"] != "not-declared"
            assert row["evidence"]
        for evidence in row["evidence"]:
            assert len(evidence["sha256"]) == 64
            assert urlparse(evidence["url"]).scheme == "https"
    for status, summary in register["summary"].items():
        rows = [r for r in register["sources"] if r["status"] == status]
        assert summary == {"sources": len(rows), "rows": sum(r["rows"] for r in rows)}
