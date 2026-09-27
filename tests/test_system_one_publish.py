import json

import pytest

from najd_datasets.system_one_publish import sha, stage


def test_publication_gate_hash_and_review_status(tmp_path):
    source = tmp_path / "source"
    pack = source / "natural-development"
    pack.mkdir(parents=True)
    row = {
        "id": "x",
        "family_id": "x",
        "task": "route",
        "language": "en",
        "register": "en",
        "split": "development",
        "state": {"request": "fictional"},
        "questions": {"a": {"type": "noul", "instructions": "yes?"}},
        "expected": {"a": True},
        "provenance": {"license": "pending"},
    }
    data = (json.dumps(row) + "\n").encode()
    (pack / "cases.jsonl").write_bytes(data)
    (pack / "manifest.json").write_text(
        json.dumps({"cases": 1, "cases_sha256": sha(data), "split": "development"})
    )
    (source / "suite.json").write_text(json.dumps({"pack_paths": ["natural-development"]}))
    clearance = {
        "publication_authorized": False,
        "packs": {
            "natural-development": {
                "status": "cleared",
                "license": "CC-BY-4.0",
                "basis": "author",
                "privacy_review": "checked",
            }
        },
    }
    with pytest.raises(ValueError, match="authorization"):
        stage(source, tmp_path / "blocked", clearance)
    clearance["publication_authorized"] = True
    stage(source, tmp_path / "release", clearance)
    published = json.loads((tmp_path / "release/natural-development/cases.jsonl").read_text())
    assert published["publication_eligible"] is True
    assert published["evaluation_claim_eligible"] is False
    assert published["independent_review"] == "pending"
    assert (pack / "cases.jsonl").read_bytes() == data
    (pack / "cases.jsonl").write_bytes(data + b" ")
    with pytest.raises(ValueError, match="hash mismatch"):
        stage(source, tmp_path / "tampered", clearance)
