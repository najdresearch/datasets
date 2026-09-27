"""Offline inventory of reconstruction inputs, not evidence of a successful rebuild."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from .pipeline import PipelineError


def audit_public_inputs(release_path: Path, sources_dir: Path) -> dict:
    release = json.loads(release_path.read_text())
    manifests = {}
    for path in sorted(sources_dir.glob("*.json")):
        data = json.loads(path.read_text())
        source_id = data.get("source_id")
        if source_id:
            if source_id in manifests:
                raise PipelineError(f"Duplicate source manifest: {source_id}")
            manifests[source_id] = (path.name, data)
    rows = []
    seen = set()
    totals = Counter()
    for source in release["sources"]:
        source_id = source["source_id"]
        count = source["case_count"]
        if source_id in seen or type(count) is not int or count <= 0:
            raise PipelineError("Release source IDs must be unique with positive integer counts")
        seen.add(source_id)
        name, manifest = manifests.get(source_id, (None, {}))
        raw_files = manifest.get("raw_files") or [{
            "url": manifest.get("raw_url"), "sha256": manifest.get("raw_sha256")
        }]
        pinned = all(
            isinstance(item.get("url"), str)
            and item["url"].startswith("https://")
            and isinstance(item.get("sha256"), str)
            and len(item["sha256"]) == 64
            and all(char in "0123456789abcdef" for char in item["sha256"])
            for item in raw_files
        )
        if not manifest:
            status = "missing_source_manifest"
        elif not pinned:
            status = "no_public_pinned_raw_input"
        elif not manifest.get("adapter"):
            status = "missing_adapter"
        else:
            status = "public_input_declared_unverified"
        totals[status] += count
        rows.append({"source_id": source_id, "rows": count,
                     "manifest": name, "status": status})
    if sum(totals.values()) != release["case_count"]:
        raise PipelineError("Source counts do not match release case_count")
    return {
        "schema_version": 1,
        "scope": "offline_manifest_inventory",
        "case_count": release["case_count"],
        "public_reconstruction_complete": False,
        "note": "Public URLs and hashes are declarations, not successful reconstruction evidence. "
                "Run adapters and verify selection, all fields, and release artifacts separately.",
        "totals": dict(sorted(totals.items())),
        "sources": rows,
    }
