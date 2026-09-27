"""Run every public adapter and check the newly published standalone source subsets.

Uses anonymous HTTP only. Requires the parquet and excel extras. Output is an evidence
report, not a certification of original generation, redistribution rights or full artifact replay.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import urlopen

from najd_datasets.adapters import reproduce_source
from najd_datasets.metadata import without_review_metadata

BENCHMARK_REVISION = "43674ef228c1461d6fd34e20c20f51efcbdce56d"
LEGACY_REVISION = "ccbf837af54611fa8106e4355302fa2b4d4660f9"
RIDDLES_REVISION = "96dd7b99b31233f83325307c778e756501afb8fc"


def fetch(repo, revision, name, output):
    url = f"https://huggingface.co/datasets/najdresearch/{repo}/resolve/{revision}/{name}"
    with urlopen(url, timeout=90) as response:
        data = response.read()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(data)
    return data


def rows(data):
    return [json.loads(line) for line in data.decode().splitlines() if line]


def index_unique(data):
    result = {row["id"]: row for row in data}
    if len(result) != len(data):
        raise ValueError("Duplicate case IDs")
    return result


def compare_subset(reference, actual, fields):
    target, source = index_unique(reference), index_unique(actual)
    missing = sorted(set(target) - set(source))
    extra = sorted(set(source) - set(target))
    changed = [
        key
        for key in sorted(set(target) & set(source))
        if any(target[key].get(field) != source[key].get(field) for field in fields)
    ]
    return {
        "expected_rows": len(target),
        "actual_rows": len(source),
        "fields": fields,
        "missing_ids": missing,
        "extra_ids": extra,
        "changed_ids": changed,
        "passed": not (missing or extra or changed),
    }


def run(root, output, workers=3):
    if output.exists():
        raise ValueError("Use a new empty output directory")
    output.mkdir(parents=True)
    ledger = json.loads((root / "releases/2026.09.14/sources.json").read_text())
    manifests = {}
    for path in sorted((root / "sources").glob("*.json")):
        value = json.loads(path.read_text())
        if value.get("source_id"):
            manifests[value["source_id"]] = (path, value)
    prefix = "datasets/najd-benchmark/2026.09.14/"
    expected = []
    downloaded = {}
    checksums = json.loads(
        fetch(
            "najd-benchmark",
            BENCHMARK_REVISION,
            prefix + "checksums.json",
            output / "reference/checksums.json",
        )
    )["files"]
    for name in ["cases.jsonl", "quarantine.jsonl"]:
        data = fetch(
            "najd-benchmark", BENCHMARK_REVISION, prefix + name, output / "reference" / name
        )
        checksum = hashlib.sha256(data).hexdigest()
        if checksum != checksums[name]:
            raise ValueError("Reference checksum mismatch")
        downloaded[name] = checksum
        expected.extend(rows(data))
    if len(index_unique(expected)) != 6089:
        raise ValueError("Unexpected benchmark inventory")

    def execute(entry):
        sid, count = entry["source_id"], entry["case_count"]
        path, manifest = manifests[sid]
        try:
            result = reproduce_source(path, output / "adapters" / path.stem)
            passed = result["published_rows_matched"] == count
            return {
                "source_id": sid,
                "rows": count,
                "status": "verified" if passed else "failed",
                "scope": "historical adapter output and selected non-audit fields",
                "manifest_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "evidence": result,
            }
        except Exception as exc:
            return {
                "source_id": sid,
                "rows": count,
                "status": "failed",
                "error": f"{type(exc).__name__}: {exc}",
            }

    results = []
    public = [
        s
        for s in ledger["sources"]
        if s["source_id"] in manifests
        and (
            manifests[s["source_id"]][1].get("raw_url")
            or manifests[s["source_id"]][1].get("raw_files")
        )
    ]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for future in as_completed([pool.submit(execute, s) for s in public]):
            result = future.result()
            results.append(result)
            print(result["source_id"], result["status"], flush=True)
            (output / "progress.json").write_text(json.dumps(results, indent=2) + "\n")

    data = fetch(
        "najd-legacy-31", LEGACY_REVISION, "original/cases.jsonl", output / "legacy/original.jsonl"
    )
    legacy = rows(data)
    manifest = json.loads(
        fetch("najd-legacy-31", LEGACY_REVISION, "manifest.json", output / "legacy/manifest.json")
    )
    if hashlib.sha256(data).hexdigest() != manifest["files"]["original/cases.jsonl"]:
        raise ValueError("Legacy source checksum mismatch")
    positions = {r["id"]: r["original_source_row"] for r in manifest["selection"]}
    generated = []
    for row in legacy:
        row = without_review_metadata(row)
        row["provenance"] = {
            "sourceId": "najd-benchmark-v1",
            "sourceRevision": "1.0.0",
            "sourceFile": "datasets/najd-benchmark-v1/cases.jsonl",
            "sourceRow": positions[row["id"]],
            "repair": "legacy_contract_v1",
        }
        generated.append(row)
    legacy_ref = [
        {k: v for k, v in r.items() if not k.startswith("audit_")}
        for r in expected
        if r["provenance"]["sourceId"] == "najd-benchmark-v1"
    ]
    fields = sorted({k for r in legacy_ref + generated for k in r})
    result = compare_subset(legacy_ref, generated, fields)
    results.append(
        {
            "source_id": "najd-benchmark-v1",
            "rows": 31,
            "status": "verified" if result["passed"] else "failed",
            "scope": "public archived subset, not original authoring procedure",
            "revision": LEGACY_REVISION,
            "evidence": result,
        }
    )

    data = fetch(
        "arabic-riddles",
        RIDDLES_REVISION,
        "data/questions.jsonl",
        output / "riddles/questions.jsonl",
    )
    manifest = json.loads(
        fetch("arabic-riddles", RIDDLES_REVISION, "manifest.json", output / "riddles/manifest.json")
    )
    if hashlib.sha256(data).hexdigest() != manifest["publication_sha256"]:
        raise ValueError("Riddle source checksum mismatch")
    riddles = rows(data)
    for sid in sorted({r["source_id"] for r in riddles}):
        generated = [
            {"id": r["id"], "prompt": r["question_ar"], "expected": {"answer": r["answer_ar"]}}
            for r in riddles
            if r["source_id"] == sid
        ]
        result = compare_subset(
            [r for r in expected if r["provenance"]["sourceId"] == sid],
            generated,
            ["prompt", "expected"],
        )
        results.append(
            {
                "source_id": sid,
                "rows": result["expected_rows"],
                "status": "verified" if result["passed"] else "failed",
                "scope": "fresh public question/answer snapshot; not original extract bytes",
                "revision": RIDDLES_REVISION,
                "evidence": result,
            }
        )
    if {r["source_id"] for r in results} != {s["source_id"] for s in ledger["sources"]}:
        raise ValueError("Incomplete source inventory")
    report = {
        "schema_version": 1,
        "recorded_at": datetime.now(UTC).isoformat(),
        "benchmark_revision": BENCHMARK_REVISION,
        "reference_checksums": downloaded,
        "sources": sorted(results, key=lambda r: r["source_id"]),
        "verified_rows": sum(r["rows"] for r in results if r["status"] == "verified"),
        "total_rows": 6089,
        "source_count": 39,
        "public_reconstruction_complete": False,
        "limitations": [
            "Checks have different scopes; inspect each source.",
            "Published reference is still used for selection in historical adapters.",
            "Original authoring and original 333-row extract bytes are unavailable.",
            "Full release metadata/Parquet assembly and rights evidence are separate gates.",
        ],
    }
    (output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=3, choices=range(1, 5))
    args = parser.parse_args()
    report = run(Path(__file__).resolve().parents[1], args.output, args.workers)
    print(json.dumps({"verified_rows": report["verified_rows"], "total_rows": 6089}))
    raise SystemExit(0 if report["verified_rows"] == 6089 else 1)
