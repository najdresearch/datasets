"""Rebuild release rows from public sources, without downloading target case data."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from audit_public_reconstruction import (
    BENCHMARK_REVISION,
    LEGACY_REVISION,
    RIDDLES_REVISION,
    fetch,
    index_unique,
    rows,
)

from najd_datasets.adapters import _selected_candidate, reproduce_source
from najd_datasets.metadata import without_review_metadata


def write_rows(path, records):
    path.write_text(
        "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records)
    )


def assemble(selection, candidates, manifests, legacy, positions, riddles):
    """Selection contains IDs and historical annotations, never target answers."""
    output = {"cases": [], "quarantine": []}
    seen = set()
    for entry in selection:
        key, sid = entry["id"], entry["source_id"]
        if key in seen:
            raise ValueError(f"Duplicate selection ID: {key}")
        seen.add(key)
        if sid == "najd-benchmark-v1":
            row = dict(legacy[key])
            row["provenance"] = {
                "sourceId": sid,
                "sourceRevision": "1.0.0",
                "sourceFile": "datasets/najd-benchmark-v1/cases.jsonl",
                "sourceRow": positions[key],
                "repair": "legacy_contract_v1",
            }
        elif key in riddles:
            item = riddles[key]
            if item["source_id"] != sid:
                raise ValueError("Riddle source mismatch")
            metadata = entry["historical_metadata"]
            if set(metadata) & {"id", "prompt", "expected"}:
                raise ValueError("Target content is forbidden in historical metadata")
            row = {
                **metadata,
                "id": key,
                "prompt": item["question_ar"],
                "expected": {"answer": item["answer_ar"]},
            }
        else:
            manifest = manifests[sid]
            base = key.removesuffix("-review-copy")
            if manifest.get("selection_mode") == "derived_review_copy":
                row = dict(candidates[sid][base])
                if base != key:
                    row.update(id=key, derived_from_candidate_id=base)
                    row["provenance"] = {**row["provenance"], "derived_from_candidate": True}
            else:
                row = _selected_candidate(candidates[sid].get(key), key, manifest)
                if row is None:
                    raise ValueError(f"Missing upstream candidate: {key}")
        if row["id"] != key or row["provenance"]["sourceId"] != sid:
            raise ValueError("Candidate identity mismatch")
        if any(not k.startswith("audit_") for k in entry["audit"]):
            raise ValueError("Only audit metadata may be overlaid")
        output[entry["split"]].append(without_review_metadata({**row, **entry["audit"]}))
    return output


def export_parquet(records, path):
    import pyarrow as pa
    import pyarrow.parquet as pq

    fields = [
        ("id", pa.string()),
        ("category", pa.string()),
        ("language", pa.string()),
        ("prompt", pa.string()),
        ("tags", pa.list_(pa.string())),
        ("fixture", pa.string()),
        ("expected", pa.string()),
        ("judge_dimensions", pa.list_(pa.string())),
        ("track", pa.string()),
        ("provenance", pa.string()),
        ("derived_from_candidate_id", pa.string()),
        ("derived_from_candidate", pa.bool_()),
        ("system_prompt", pa.string()),
        ("dialect", pa.string()),
        ("answer_recovery_status", pa.string()),
        ("answer_recovery_evidence", pa.string()),
        ("prompt_cleaned", pa.bool_()),
        ("audit_status", pa.string()),
        ("audit_issues", pa.list_(pa.string())),
    ]
    converted = []
    for record in records:
        row = dict(record)
        for key in ["expected", "provenance", "answer_recovery_evidence"]:
            if isinstance(row.get(key), (dict, list)):
                row[key] = json.dumps(
                    row[key], ensure_ascii=False, sort_keys=True, separators=(",", ":")
                )
        converted.append(row)
    table = pa.Table.from_pylist(converted, schema=pa.schema(fields))
    pq.write_table(table, path)
    if not pq.read_table(path).equals(table):
        raise ValueError("Parquet round-trip failed")


def run(root, output, workers=3):
    if output.exists():
        raise ValueError("Use a new output directory")
    output.mkdir(parents=True)
    specs = {}
    paths = {}
    for path in sorted((root / "sources").glob("*.json")):
        value = json.loads(path.read_text())
        if value.get("adapter") and (value.get("raw_url") or value.get("raw_files")):
            specs[value["source_id"]] = value
            paths[value["source_id"]] = path

    def generate(sid):
        destination = output / "inputs" / paths[sid].stem
        result = reproduce_source(paths[sid], destination, candidates_only=True)
        print(sid, result["rows"], flush=True)
        return sid, index_unique(rows((destination / "cases.jsonl").read_bytes()))

    with ThreadPoolExecutor(max_workers=workers) as pool:
        candidates = dict(pool.map(generate, specs))

    def source(repo, revision, filename):
        return fetch(repo, revision, filename, output / "inputs" / repo / filename)

    legacy_manifest = json.loads(source("najd-legacy-31", LEGACY_REVISION, "manifest.json"))
    legacy_data = source("najd-legacy-31", LEGACY_REVISION, "original/cases.jsonl")
    if hashlib.sha256(legacy_data).hexdigest() != legacy_manifest["files"]["original/cases.jsonl"]:
        raise ValueError("Legacy checksum mismatch")
    fixture_hashes = {}
    for name, checksum in legacy_manifest["files"].items():
        if name.startswith("fixtures/"):
            data = source("najd-legacy-31", LEGACY_REVISION, name)
            if hashlib.sha256(data).hexdigest() != checksum:
                raise ValueError(f"Fixture checksum mismatch: {name}")
            fixture_hashes[name] = checksum
    riddle_manifest = json.loads(source("arabic-riddles", RIDDLES_REVISION, "manifest.json"))
    riddle_data = source("arabic-riddles", RIDDLES_REVISION, "data/questions.jsonl")
    if hashlib.sha256(riddle_data).hexdigest() != riddle_manifest["publication_sha256"]:
        raise ValueError("Riddle checksum mismatch")
    selection_path = root / "releases/2026.09.14/public-selection.json"
    selection = json.loads(selection_path.read_text())["rows"]
    result = assemble(
        selection,
        candidates,
        specs,
        index_unique(rows(legacy_data)),
        {r["id"]: r["original_source_row"] for r in legacy_manifest["selection"]},
        index_unique(rows(riddle_data)),
    )
    release = output / "release"
    release.mkdir()
    evidence = {
        "target_case_downloads": 0,
        "rows": {},
        "sha256": {},
        "selection_sha256": hashlib.sha256(selection_path.read_bytes()).hexdigest(),
        "fixture_sha256": fixture_hashes,
        "reconstruction_boundary": (
            "Pinned upstream sources, archived legacy subset, fresh riddle snapshot, "
            "recovered selection and historical metadata"
        ),
    }
    for split, records in result.items():
        path = release / f"{split}.jsonl"
        write_rows(path, records)
        evidence["rows"][split] = len(records)
        evidence["sha256"][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    fixture_root = output / "inputs/najd-legacy-31/fixtures"
    shutil.copytree(fixture_root, release / "fixtures")
    evidence["fixture_workspace_checks"] = {}
    for record in result["cases"] + result["quarantine"]:
        fixture = record.get("fixture")
        if not fixture:
            continue
        source = fixture_root / fixture
        if not source.resolve().is_relative_to(fixture_root.resolve()) or not source.is_dir():
            raise ValueError(f"Invalid or missing fixture: {fixture}")
        # Historical runner copied the selected fixture folder contents to the case workspace.
        workspace = output / "fixture-workspaces" / record["id"]
        shutil.copytree(source, workspace)
        installed = {}
        for path in workspace.rglob("*"):
            if path.is_file():
                relative = path.relative_to(workspace).as_posix()
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                if fixture_hashes[f"fixtures/{fixture}/{relative}"] != digest:
                    raise ValueError("Installed fixture differs")
                installed[relative] = digest
        evidence["fixture_workspace_checks"][record["id"]] = installed
    expected = json.loads((root / "releases/2026.09.14/public-checksums.json").read_text())["files"]
    for name, actual in evidence["sha256"].items():
        if actual != expected[name]:
            raise ValueError(f"Reconstructed checksum differs: {name}: {actual}")
    for split, name in [("cases", "viewer.parquet"), ("quarantine", "quarantine.parquet")]:
        export_parquet(result[split], release / name)
        evidence["sha256"][name] = hashlib.sha256((release / name).read_bytes()).hexdigest()
    # These are preserved historical documents, not regenerated audit events.
    evidence["preserved_historical_documents"] = []
    for name in expected:
        if name.endswith(".json"):
            data = fetch(
                "najd-benchmark",
                BENCHMARK_REVISION,
                "datasets/najd-benchmark/2026.09.14/" + name,
                release / name,
            )
            if hashlib.sha256(data).hexdigest() != expected[name]:
                raise ValueError(f"Historical document checksum mismatch: {name}")
            evidence["preserved_historical_documents"].append(name)
            evidence["sha256"][name] = expected[name]
    evidence["byte_identical_artifacts"] = [
        name for name, digest in evidence["sha256"].items() if expected[name] == digest
    ]
    (release / "checksums.json").write_text(
        json.dumps({"algorithm": "sha256", "files": evidence["sha256"]}, indent=2, sort_keys=True)
        + "\n"
    )
    (output / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    return evidence


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=3, choices=range(1, 5))
    args = parser.parse_args()
    print(json.dumps(run(Path(__file__).resolve().parents[1], args.output, args.workers), indent=2))
