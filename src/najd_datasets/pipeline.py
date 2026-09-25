"""Source collection, deterministic cleaning, generation, and release checks."""

from __future__ import annotations

import hashlib
import itertools
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


class PipelineError(ValueError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _required(record: dict[str, Any], names: tuple[str, ...], kind: str) -> None:
    missing = [name for name in names if record.get(name) in (None, "")]
    if missing:
        raise PipelineError(f"{kind} missing: {', '.join(missing)}")


def validate_source(source: dict[str, Any]) -> None:
    _required(
        source,
        (
            "schema_version", "id", "kind", "collection_method", "origin", "license",
            "redistribution_basis", "split", "revision", "sha256", "review_status",
        ),
        "source",
    )
    if source["schema_version"] != "1":
        raise PipelineError("unsupported source schema version")
    if not isinstance(source.get("transformations"), list):
        raise PipelineError("transformations must be a list")
    if source["collection_method"] != source["kind"] + "_jsonl":
        raise PipelineError("collection_method does not match source kind")
    if not re.fullmatch(r"[0-9a-f]{64}", source["sha256"]):
        raise PipelineError("source SHA-256 must be a 64-character lowercase hex digest")
    if source["kind"] not in {"local", "huggingface"}:
        raise PipelineError("source kind must be local or huggingface")
    if source["kind"] == "local":
        _required(source, ("path",), "local source")
    else:
        _required(source, ("repo_id", "file"), "Hugging Face source")
        if not re.fullmatch(r"[0-9a-f]{40}", source["revision"]):
            raise PipelineError("Hugging Face revision must be a full commit hash")
    if source.get("rights_status") not in {"approved", "pending", "blocked"}:
        raise PipelineError("rights_status must be approved, pending, or blocked")


def collect(source_path: Path, output: Path) -> dict[str, Any]:
    source = read_json(source_path)
    validate_source(source)
    if source["kind"] == "local":
        input_path = (source_path.parent / source["path"]).resolve()
        if not input_path.is_relative_to(source_path.parent.parent.resolve()):
            raise PipelineError("local source path must stay under repository root")
    else:
        from huggingface_hub import hf_hub_download

        input_path = Path(
            hf_hub_download(
                repo_id=source["repo_id"],
                repo_type="dataset",
                revision=source["revision"],
                filename=source["file"],
            )
        )
    raw = input_path.read_bytes()
    raw_sha = digest(raw)
    if source.get("sha256") and raw_sha != source["sha256"]:
        raise PipelineError("source SHA-256 mismatch")
    rows = read_jsonl(input_path)
    if not all(isinstance(row, dict) for row in rows):
        raise PipelineError("JSONL rows must be objects")
    wrapped = [
        {
            "source_id": source["id"],
            "source_revision": source["revision"],
            "source_row": i,
            "payload": row,
        }
        for i, row in enumerate(rows, 1)
    ]
    write_jsonl(output, wrapped)
    report = {
        "source": source,
        "source_manifest_sha256": digest(source_path.read_bytes()),
        "raw_sha256": raw_sha,
        "rows": len(rows),
        "output_sha256": digest(output.read_bytes()),
    }
    write_json(output.with_suffix(".manifest.json"), report)
    return report


def _text(value: Any) -> str:
    if not isinstance(value, str):
        raise PipelineError("text field must be a string")
    return re.sub(r"\s+", " ", value).strip()


def clean(inputs: list[Path], output: Path) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    source_reports = []
    for path in inputs:
        report = read_json(path.with_suffix(".manifest.json"))
        if digest(path.read_bytes()) != report["output_sha256"]:
            raise PipelineError(f"collected file changed: {path}")
        source_reports.append(report)
        for wrapped in read_jsonl(path):
            row = wrapped["payload"]
            _required(row, ("id", "track", "language", "prompt", "expected"), "case")
            if not isinstance(row["expected"], dict) or not row["expected"]:
                raise PipelineError("expected must be a nonempty object")
            prompt = _text(row["prompt"])
            if not prompt:
                raise PipelineError("empty prompt")
            candidates.append(
                {
                    "id": f"{wrapped['source_id']}:{row['id']}",
                    "track": _text(row["track"]),
                    "language": _text(row["language"]),
                    "prompt": prompt,
                    "expected": row["expected"],
                    "tags": row.get("tags", []),
                    "review_status": "not_reviewed",
                    "provenance": {
                        "source_id": wrapped["source_id"],
                        "source_revision": wrapped["source_revision"],
                        "source_row": wrapped["source_row"],
                        "upstream": row.get("provenance"),
                    },
                }
            )
    ids = [row["id"] for row in candidates]
    if len(ids) != len(set(ids)):
        raise PipelineError("duplicate case IDs")
    seen: set[str] = set()
    kept = []
    for row in candidates:
        key = digest(
            json.dumps(
                {"track": row["track"], "prompt": row["prompt"], "expected": row["expected"]},
                sort_keys=True,
                ensure_ascii=False,
            ).encode()
        )
        if key not in seen:
            seen.add(key)
            kept.append(row)
    kept.sort(key=lambda row: row["id"])
    write_jsonl(output, kept)
    report = {
        "input_rows": len(candidates),
        "output_rows": len(kept),
        "exact_duplicates_removed": len(candidates) - len(kept),
        "sources": source_reports,
        "output_sha256": digest(output.read_bytes()),
        "review_status": "not_reviewed",
        "semantic_review": "not_performed",
    }
    write_json(output.with_suffix(".manifest.json"), report)
    return report


def _render(value: Any, variables: dict[str, str]) -> Any:
    if isinstance(value, str):
        return value.format_map(variables)
    if isinstance(value, list):
        return [_render(item, variables) for item in value]
    if isinstance(value, dict):
        return {key: _render(item, variables) for key, item in value.items()}
    return value


def generate(spec_path: Path, output: Path) -> dict[str, Any]:
    spec = read_json(spec_path)
    _required(
        spec,
        (
            "id",
            "track",
            "language",
            "prompt_template",
            "expected_template",
            "license",
            "redistribution_basis",
        ),
        "spec",
    )
    if spec.get("rights_status") not in {"approved", "pending", "blocked"}:
        raise PipelineError("generation rights_status must be approved, pending, or blocked")
    slots = spec.get("slots", {})
    if not slots or not all(isinstance(v, list) and v for v in slots.values()):
        raise PipelineError("spec needs nonempty slot lists")
    combinations = list(itertools.product(*(slots[key] for key in sorted(slots))))
    if len(combinations) > spec.get("max_cases", 1000):
        raise PipelineError("generation exceeds max_cases")
    rows = []
    spec_sha = digest(spec_path.read_bytes())
    for index, combo in enumerate(combinations, 1):
        variables = dict(zip(sorted(slots), combo, strict=True))
        rows.append(
            {
                "id": f"{spec['id']}:{index:05d}",
                "track": spec["track"],
                "language": spec["language"],
                "prompt": _render(spec["prompt_template"], variables),
                "expected": _render(spec["expected_template"], variables),
                "tags": spec.get("tags", []),
                "review_status": "not_reviewed",
                "provenance": {
                    "origin": "template_generated",
                    "spec_id": spec["id"],
                    "spec_sha256": spec_sha,
                    "variables": variables,
                },
            }
        )
    write_jsonl(output, rows)
    report = {
        "spec_id": spec["id"],
        "spec_sha256": spec_sha,
        "generation_spec": {
            "license": spec["license"],
            "redistribution_basis": spec["redistribution_basis"],
            "rights_status": spec["rights_status"],
        },
        "rows": len(rows),
        "output_sha256": digest(output.read_bytes()),
        "review_status": "not_reviewed",
        "semantic_review": "not_performed",
    }
    write_json(output.with_suffix(".manifest.json"), report)
    return report


def validate(path: Path) -> dict[str, Any]:
    rows = read_jsonl(path)
    ids = [row.get("id") for row in rows]
    failures = []
    if not rows:
        failures.append("empty dataset")
    if len(ids) != len(set(ids)):
        failures.append("duplicate IDs")
    for index, row in enumerate(rows, 1):
        for field in (
            "id",
            "track",
            "language",
            "prompt",
            "expected",
            "provenance",
            "review_status",
        ):
            if not row.get(field):
                failures.append(f"row {index}: missing {field}")
        if not isinstance(row.get("expected"), dict):
            failures.append(f"row {index}: expected is not an object")
    return {
        "rows": len(rows),
        "tracks": dict(Counter(r.get("track") for r in rows)),
        "sha256": digest(path.read_bytes()),
        "failures": failures,
        "passed": not failures,
    }
