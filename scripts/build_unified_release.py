"""Combine historical cases into one current collection without audit-status labels."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from reconstruct_public_release import export_parquet, rows, write_rows

VERSION = "2026.09.27"


def unify(records):
    seen = set()
    result = []
    for record in records:
        if record["id"] in seen:
            raise ValueError("Duplicate case ID")
        seen.add(record["id"])
        result.append({k: v for k, v in record.items() if k != "audit_status"})
    return result


def build(source, output, root):
    import pyarrow.parquet as pq

    if output.exists():
        raise ValueError("Use a new output directory")
    expected = json.loads((root / "releases/2026.09.14/public-checksums.json").read_text())["files"]
    for name in ["cases.jsonl", "quarantine.jsonl", "case.schema.json"]:
        if hashlib.sha256((source / name).read_bytes()).hexdigest() != expected[name]:
            raise ValueError(f"Historical input checksum mismatch: {name}")
    records = unify(
        rows((source / "cases.jsonl").read_bytes())
        + rows((source / "quarantine.jsonl").read_bytes())
    )
    if len(records) != 6089:
        raise ValueError("Expected all 6089 historical cases")
    output.mkdir(parents=True)
    write_rows(output / "cases.jsonl", records)
    export_parquet(records, output / "viewer.parquet")
    table = pq.read_table(output / "viewer.parquet").drop(["audit_status"])
    pq.write_table(table, output / "viewer.parquet")
    schema = json.loads((source / "case.schema.json").read_text())
    schema["properties"].pop("audit_status", None)
    schema["required"] = [k for k in schema.get("required", []) if k != "audit_status"]
    schema["$id"] = schema["$id"].replace("2026.09.14", VERSION)
    docs = {
        "case.schema.json": schema,
        "manifest.json": {
            "id": "najd-benchmark",
            "version": VERSION,
            "case_count": len(records),
            "source_count": len({r["provenance"]["sourceId"] for r in records}),
            "configuration": "default",
            "split": "test",
            "transformation": "Combine historical case files and remove audit_status only.",
            "input_revision": "43674ef228c1461d6fd34e20c20f51efcbdce56d",
            "category_counts": dict(
                Counter(r.get("category") or r.get("track", "other") for r in records)
            ),
            "language_counts": dict(Counter(r.get("language", "unknown") for r in records)),
        },
        "suite.json": {
            "id": "najd-benchmark",
            "version": VERSION,
            "schema_version": "1",
            "cases_file": "cases.jsonl",
            "schema_file": "case.schema.json",
            "license": "other",
        },
        "sources.json": json.loads((root / "releases/source-rights-evidence.json").read_text()),
    }
    for name, value in docs.items():
        (output / name).write_text(
            json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        )
    checks = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir())}
    (output / "checksums.json").write_text(
        json.dumps({"algorithm": "sha256", "files": checks}, indent=2, sort_keys=True) + "\n"
    )
    return checks


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Reconstructed historical release directory")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(build(args.source, args.output, Path(__file__).resolve().parents[1]), indent=2)
    )
