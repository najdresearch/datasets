#!/usr/bin/env python3
"""Compare a private authorized extract with historical quarantined rows.

The report contains only counts and hashes; row text stays in private storage.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def canonical_case(source: dict, source_row: int) -> dict:
    """Reapply the archived importer's field mapping without audit metadata."""
    source_id = source["source_id"]
    item_id = source["source_item_id"]
    return {
        "id": f"scraped-{source_id}-{item_id}",
        "track": source["category"],
        "language": "ar",
        "prompt": source["question_ar"],
        "expected": {"answer": source["answer_ar"]},
        "tags": [source["category"], source["subcategory"], source["content_type"]],
        "provenance": {
            "sourceId": source_id,
            "sourceItemId": item_id,
            "sourceFile": "private/authorized-source-extracts/authorized-items.jsonl",
            "sourceRow": source_row,
        },
        "review_status": "not_reviewed",
    }


def compare(extract_path: Path, quarantine_path: Path) -> dict:
    extracted = read_jsonl(extract_path)
    by_key = {
        (row["source_id"], row["source_item_id"]): canonical_case(row, position)
        for position, row in enumerate(extracted, 1)
    }
    if len(by_key) != len(extracted):
        raise ValueError("duplicate source ID and item ID in extract")
    historical = [
        row for row in read_jsonl(quarantine_path)
        if row.get("provenance", {}).get("sourceFile")
        == "private/authorized-source-extracts/authorized-items.jsonl"
    ]
    counts = defaultdict(lambda: {"exact": 0, "changed": 0, "missing": 0})
    for row in historical:
        provenance = row["provenance"]
        source_id = provenance["sourceId"]
        fresh = by_key.get((source_id, provenance["sourceItemId"]))
        if fresh is None:
            result = "missing"
        elif fresh == {key: value for key, value in row.items() if not key.startswith("audit_")}:
            result = "exact"
        else:
            result = "changed"
        counts[source_id][result] += 1
    totals = {
        key: sum(source[key] for source in counts.values())
        for key in ("exact", "changed", "missing")
    }
    return {
        "extract_sha256": hashlib.sha256(extract_path.read_bytes()).hexdigest(),
        "extract_rows": len(extracted),
        "historical_rows": len(historical),
        "totals": totals,
        "sources": dict(sorted(counts.items())),
        "scope": "Every published field except audit metadata; no rights decision",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("extract", type=Path)
    parser.add_argument("quarantine", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = compare(args.extract, args.quarantine)
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
