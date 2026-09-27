import hashlib
import json
from pathlib import Path

import pytest

from najd_datasets.decision_pilot import build


def test_frozen_pilot_is_bilingual_development_only(tmp_path):
    source = Path(__file__).parents[1] / "fixtures/decision-pilot"
    manifest = build(source, tmp_path / "pack")
    data = (tmp_path / "pack/cases.jsonl").read_bytes()
    rows = [json.loads(line) for line in data.splitlines()]
    assert len(rows) == 48
    assert len({r["family_id"] for r in rows}) == 24
    assert {r["language"] for r in rows} == {"en", "ar"}
    assert all(r["split"] == "development" for r in rows)
    assert not manifest["publication_eligible"]
    assert hashlib.sha256(data).hexdigest() == manifest["cases_sha256"]
    assert b'\\u' not in data
    with pytest.raises(FileExistsError):
        build(source, tmp_path / "pack")
