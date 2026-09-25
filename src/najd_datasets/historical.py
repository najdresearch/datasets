"""Rebuild the public 2026.09.14 benchmark rows from the preserved pre-audit bundle.

This is a historical reproduction path. It does not certify semantic correctness or rights.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from .pipeline import PipelineError, digest, read_json, write_json

RELEASE_DIR = Path(__file__).resolve().parents[2] / "releases" / "2026.09.14"


def _identity(row: dict[str, Any]) -> str:
    payload = "\x1f".join(
        str(row.get(field, ""))
        for field in ("track", "category", "prompt", "answer", "correct_answer")
    )
    return digest(payload.strip().encode("utf-8"))


def _rank(row: dict[str, Any]) -> tuple[str, str]:
    payload = json.dumps(row, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return digest(payload), str(row.get("id", ""))


def _canonical(row: dict[str, Any]) -> str:
    return json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def select(input_path: Path, output_path: Path, plan: dict[str, Any]) -> list[dict[str, Any]]:
    if digest(input_path.read_bytes()) != plan["input_sha256"]:
        raise PipelineError("pre-audit input hash mismatch")
    unique: dict[str, dict[str, Any]] = {}
    rows = 0
    with input_path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            rows += 1
            unique.setdefault(_identity(row), row)
    if rows != plan["input_rows"]:
        raise PipelineError("pre-audit input row count mismatch")
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in unique.values():
        category = str(row.get("track") or row.get("category") or "general")
        row["track"] = category
        groups[category].append(row)
    selected = []
    cap = plan["selection"]["per_category_cap"]
    for category in sorted(groups):
        selected.extend(sorted(groups[category], key=_rank)[:cap])
    selected.sort(key=lambda row: (str(row.get("track", "")), str(row.get("id", ""))))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for row in selected:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    if len(selected) != plan["selection"]["expected_rows"]:
        raise PipelineError("selected row count mismatch")
    if digest(output_path.read_bytes()) != plan["selection"]["sha256"]:
        raise PipelineError("selected bundle hash mismatch")
    return selected


def repair(row: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    provenance = row["provenance"]
    source_id = provenance["sourceId"]
    if source_id in plan["source_revisions"]:
        provenance["sourceRevision"] = plan["source_revisions"][source_id]
    rewrite = plan["source_rewrite"]
    if source_id == rewrite["from"]:
        provenance["sourceId"] = rewrite["to"]
        provenance["sourceFile"] = rewrite["source_file"]
    if "derived_copy_of" in row:
        row["derived_from_candidate_id"] = row.pop("derived_copy_of")
    if "" in row.get("tags", []):
        row["tags"] = [tag for tag in row["tags"] if tag]
    if source_id in plan["zero_answer_key_sources"] and row["expected"].get("answerKey") == "":
        row["expected"]["answerKey"] = "0"
    correction = plan["case_corrections"].get(row["id"])
    if correction:
        row["prompt"] = correction["prompt"]
        row["expected"]["options"] = correction["expected_options"]
    return row


def audit(row: dict[str, Any], verified_sources: set[str]) -> dict[str, Any]:
    required = ("id", "track", "language", "prompt", "expected", "provenance", "review_status")
    if any(not row.get(field) for field in required):
        raise PipelineError(f"case {row.get('id')} has a missing required field")
    source_id = row["provenance"]["sourceId"]
    if source_id not in verified_sources:
        issues = ["unverified_exact_source_link"]
    elif "\ufffd" in json.dumps(row, ensure_ascii=False):
        issues = ["unicode_replacement_character"]
    elif "answer" in row["expected"] and row["expected"]["answer"] in (None, ""):
        issues = ["missing_expected_answer"]
    else:
        issues = []
    row["audit_status"] = "quarantined" if issues else "certified"
    row["audit_issues"] = issues
    return row


def reproduce(input_path: Path, output_dir: Path) -> dict[str, Any]:
    plan = read_json(RELEASE_DIR / "plan.json")
    sources_path = RELEASE_DIR / "sources.json"
    if digest(sources_path.read_bytes()) != plan["audit"]["sources_sha256"]:
        raise PipelineError("source ledger hash mismatch")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise PipelineError("output directory must be empty")
    output_dir.mkdir(parents=True, exist_ok=True)
    selected = select(input_path, output_dir / "selected-cases.jsonl", plan)
    source_ledger = read_json(sources_path)
    verified_sources = {
        entry["source_id"]
        for entry in source_ledger["sources"]
        if entry["certified_case_count"] > 0
    }
    cases_path = output_dir / "cases.jsonl"
    quarantine_path = output_dir / "quarantine.jsonl"
    counts = {"certified": 0, "quarantined": 0}
    with (
        cases_path.open("w", encoding="utf-8") as cases,
        quarantine_path.open("w", encoding="utf-8") as quarantined,
    ):
        for selected_row in selected:
            row = audit(repair(selected_row, plan), verified_sources)
            counts[row["audit_status"]] += 1
            destination = cases if row["audit_status"] == "certified" else quarantined
            destination.write(_canonical(row) + "\n")
    for status, name, path in (
        ("certified", "cases", cases_path),
        ("quarantined", "quarantine", quarantine_path),
    ):
        expected = plan["audit"][name]
        if counts[status] != expected["rows"] or digest(path.read_bytes()) != expected["sha256"]:
            raise PipelineError(f"{name} does not match published row count and SHA-256")
    report = {
        "release": plan["release"],
        "input_sha256": plan["input_sha256"],
        "selected_sha256": plan["selection"]["sha256"],
        "cases": {"rows": counts["certified"], "sha256": digest(cases_path.read_bytes())},
        "quarantine": {
            "rows": counts["quarantined"],
            "sha256": digest(quarantine_path.read_bytes()),
        },
        "status": "byte-for-byte core rows reproduced",
        "semantic_review": "not_performed",
    }
    write_json(output_dir / "reproduction-report.json", report)
    return report
