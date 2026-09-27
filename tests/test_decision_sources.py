import hashlib

import pytest

from najd_datasets.decision_sources import checked, row


def test_source_hash_guard(tmp_path):
    path = tmp_path / "data"
    path.write_bytes(b"original")
    digest = hashlib.sha256(b"original").hexdigest()
    assert checked(path, digest) == b"original"
    path.write_bytes(b"modified")
    with pytest.raises(ValueError, match="hash mismatch"):
        checked(path, digest)


def test_source_lane_and_unknown_gold():
    provenance = {"source": "sample", "upstream_split": "test"}
    result = row("x", "x", "ar-SA", {}, {"a": "Action"}, "a", provenance)
    assert result["split"] == "public_reference"
    assert result["provenance"]["upstream_split"] == "test"
    with pytest.raises(ValueError, match="Unknown source gold"):
        row("x", "x", "ar-SA", {}, {"a": "Action"}, "b", provenance)
