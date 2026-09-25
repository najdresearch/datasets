import csv
import json
from pathlib import Path

from najd_datasets.review import prepare_review


def test_review_packet_uses_row_provenance_and_does_not_invent_a_source(tmp_path: Path):
    rows = [
        {
            "id": "one", "track": "classification", "prompt": "First",
            "expected": {"label": "yes"}, "tags": [],
            "provenance": {
                "sourceId": "first", "dialect": "saudi",
                "sourceUrl": "https://example.org/first",
            },
        },
        {
            "id": "two", "track": "tool", "prompt": "Second",
            "expected": {"action": "wait"}, "tags": [], "provenance": {"source_id": "second"},
        },
    ]
    source = tmp_path / "cases.jsonl"
    source.write_text("".join(json.dumps(row) + "\n" for row in rows))
    output = tmp_path / "review.csv"
    prepare_review(source, output)
    with output.open(newline="") as handle:
        by_id = {row["case_id"]: row for row in csv.DictReader(handle)}
    assert by_id["one"]["source_id"] == "first"
    assert by_id["one"]["dialect"] == "saudi"
    assert by_id["one"]["source_url"] == "https://example.org/first"
    assert by_id["two"]["source_id"] == "second"
    assert by_id["two"]["dialect"] == ""
    assert by_id["two"]["source_url"] == ""
