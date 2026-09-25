"""Prepare a small, repeatable human review packet without committing case text."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

from .pipeline import PipelineError, digest, read_jsonl


def prepare_review(input_path: Path, output_path: Path, per_category: int = 2) -> dict:
    if per_category < 1:
        raise PipelineError("per_category must be positive")
    if output_path.exists():
        raise PipelineError("review packet already exists")
    groups = defaultdict(list)
    for row in read_jsonl(input_path):
        groups[row["expected"].get("category", row["track"])].append(row)
    selected = []
    for category, rows in sorted(groups.items()):
        ranked = sorted(rows, key=lambda row: (digest(row["id"].encode()), row["id"]))
        selected.extend((category, row) for row in ranked[:per_category])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "case_id", "category", "dialect", "prompt", "expected_json", "source_url",
            "reviewer_id", "rights_decision", "privacy_decision", "semantic_decision",
            "issue", "evidence_url", "reviewed_at",
        ])
        for category, row in selected:
            writer.writerow([
                row["id"], category, row["tags"][-1], row["prompt"],
                json.dumps(row["expected"], ensure_ascii=False, sort_keys=True),
                "https://github.com/Moshe-ship/arabic-agent-eval/tree/"
                "9f075af0ae5b70580e650b26ddf1d26cf871b24f/data", "", "", "", "", "", "", "",
            ])
    return {
        "categories": len(groups),
        "sample_rows": len(selected),
        "sha256": digest(output_path.read_bytes()),
    }
