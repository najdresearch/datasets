"""Fetch and account for every file and case in one pinned Hugging Face release."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from .pipeline import PipelineError, digest, read_json, read_jsonl, write_json

UPSTREAM_REPRODUCED_SOURCES = frozenset({
    "arabic-agent-eval", "paired-msa-saudi-tool-use", "QCRI/IslamicFaithQA",
    "arabic-function-calling", "arabicragb", "humain-aratruthfulqa",
    "arasafe", "mena-values", "arbml-quran_hadith", "arbml-saudiirony",
    "arbml-arabic-rc", "humain-arapro", "dialectal-arabic-mmlu",
    "arbml-arabic_dialects_dataset", "arbml-arabic-hate-speech",
    "arbml-dangerous-dataset", "humain-aramath", "humain-araifeval",
    "inception-arabic-ifeval", "commonsense-validation", "arabic-exams",
    "aratrust", "arbml-cidar-eval-100", "arbml-cidar-mcq-100",
    "arabicmmlu", "absher", "alghafa-native", "pico-saudi-v0.01",
    "arabic-safety-evaluation",
})


def _fetch(url: str) -> bytes:
    for attempt in range(3):
        try:
            with urlopen(url, timeout=60) as response:
                return response.read()
        except URLError:
            if attempt == 2:
                raise
    raise AssertionError("unreachable")


def _verified_file(url: str, path: Path, expected_sha256: str) -> None:
    if path.exists() and digest(path.read_bytes()) == expected_sha256:
        return
    data = _fetch(url)
    if digest(data) != expected_sha256:
        raise PipelineError(f"SHA-256 mismatch for {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(data)
    temporary.replace(path)


def _coverage(release: Path, index_path: Path) -> dict:
    cases = read_jsonl(release / "cases.jsonl")
    quarantine = read_jsonl(release / "quarantine.jsonl")
    ledger = read_json(release / "sources.json")
    source_entries = {source["source_id"]: source for source in ledger["sources"]}
    def rebuild_status(source_id: str) -> str:
        if source_id in UPSTREAM_REPRODUCED_SOURCES:
            return "upstream_reproduced"
        if source_id == "najd-benchmark-v1":
            return "private_archive_reproduced"
        if any(
            path.startswith("private/authorized-source-extracts/")
            for path in source_entries[source_id]["source_files"]
        ):
            return "private_artifact_missing"
        return "adapter_needed"
    counts: dict[str, Counter] = {}
    ids = set()
    missing = Counter()
    index_rows = []
    for status, rows in (("certified", cases), ("quarantined", quarantine)):
        for row in rows:
            case_id = row["id"]
            if case_id in ids:
                raise PipelineError(f"duplicate case ID: {case_id}")
            ids.add(case_id)
            if row["audit_status"] != status:
                raise PipelineError(f"audit status mismatch: {case_id}")
            provenance = row.get("provenance") or {}
            source_id = provenance.get("sourceId")
            if not source_id or not provenance.get("sourceFile"):
                raise PipelineError(f"missing source provenance: {case_id}")
            for field in ("sourceRow", "sourceRevision"):
                if provenance.get(field) in (None, ""):
                    missing[field] += 1
            counts.setdefault(source_id, Counter())[status] += 1
            index_rows.append([
                case_id, status, source_id, provenance["sourceFile"],
                provenance.get("sourceRow", ""), provenance.get("sourceRevision", ""),
                rebuild_status(source_id),
            ])
    expected_ids = {source["source_id"] for source in ledger["sources"]}
    if set(counts) != expected_ids:
        raise PipelineError("case source IDs and source ledger differ")
    for source in ledger["sources"]:
        actual = counts[source["source_id"]]
        if actual["certified"] != source["certified_case_count"]:
            raise PipelineError(f"certified count mismatch: {source['source_id']}")
        if actual["quarantined"] != source["quarantine_case_count"]:
            raise PipelineError(f"quarantine count mismatch: {source['source_id']}")
    if len(cases) != ledger["certified_case_count"]:
        raise PipelineError("total certified count mismatch")
    if len(quarantine) != ledger["quarantine_case_count"]:
        raise PipelineError("total quarantine count mismatch")
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with index_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "case_id", "audit_status", "source_id", "source_file",
            "source_row", "source_revision", "upstream_rebuild_status",
        ])
        writer.writerows(sorted(index_rows))
    status_counts = Counter(rebuild_status(source_id) for source_id in counts)
    row_status_counts = Counter()
    for source_id, counter in counts.items():
        row_status_counts[rebuild_status(source_id)] += sum(counter.values())
    return {
        "certified_rows": len(cases),
        "quarantined_rows": len(quarantine),
        "total_rows": len(ids),
        "source_count": len(counts),
        "missing_source_row": missing["sourceRow"],
        "missing_source_revision": missing["sourceRevision"],
        "case_index_sha256": digest(index_path.read_bytes()),
        "upstream_rebuild_source_counts": dict(status_counts),
        "upstream_rebuild_row_counts": dict(row_status_counts),
        "sources": {
            source_id: dict(counter) for source_id, counter in sorted(counts.items())
        },
    }


def sync_release(spec_path: Path, output_dir: Path) -> dict:
    spec = read_json(spec_path)
    repo = spec["repo_id"]
    revision = spec["revision"]
    release_name = spec["release_dir"]
    base = f"https://huggingface.co/datasets/{repo}/resolve/{revision}/"
    metadata_url = f"https://huggingface.co/api/datasets/{repo}/revision/{revision}"
    metadata = json.loads(_fetch(metadata_url))
    remote_files = {entry["rfilename"] for entry in metadata["siblings"]}
    checksum_name = f"{release_name}/checksums.json"
    checksums_path = output_dir / checksum_name
    _verified_file(base + checksum_name, checksums_path, spec["checksums_sha256"])
    checksums = read_json(checksums_path)
    expected_files = set(spec["root_files"]) | {checksum_name}
    expected_files |= {f"{release_name}/{name}" for name in checksums["files"]}
    if remote_files != expected_files:
        raise PipelineError("pinned repository file list differs from release manifest")
    for name, sha256 in spec["root_files"].items():
        _verified_file(base + name, output_dir / name, sha256)
    for name, sha256 in checksums["files"].items():
        relative = f"{release_name}/{name}"
        _verified_file(base + relative, output_dir / relative, sha256)
    coverage = _coverage(output_dir / release_name, output_dir / "case-index.csv")
    report = {
        "repo_id": repo,
        "revision": revision,
        "verified_files": len(expected_files),
        "coverage": coverage,
    }
    write_json(output_dir / "verification-report.json", report)
    return report
