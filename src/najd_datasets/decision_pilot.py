"""Build the original synthetic decision pilot as development-only local artifacts."""
import argparse
import copy
import hashlib
import json
from pathlib import Path


def build(source: Path, output: Path) -> dict:
    pairs = json.loads((source / "pairs.json").read_text())
    spec = json.loads((source / "spec.json").read_text())
    rows = []
    for pair in pairs:
        for language in spec["languages"]:
            task = pair["task"]
            state = {"text": pair[language]}
            if task == "policy":
                state = {"policy": pair["policy"], "request": pair[language]}
            elif task == "computer_action":
                state = {"goal": pair[language], "screen": pair["screen"],
                         "candidates": pair["candidates"]}
            questions = copy.deepcopy(spec["questions"][task])
            if task == "computer_action":
                questions["action"].pop("criteria_from")
                questions["action"]["criteria"] = {
                    c["id"]: c["action"] for c in pair["candidates"]
                }
            rows.append({"id": pair["id"] + "-" + language, "family_id": pair["id"],
                         "language": language, "task": task, "split": "development",
                         "state": state, "questions": questions, "expected": pair["expected"],
                         "unsafe": pair.get("unsafe", [])})
    if len(rows) != 48 or len({r["id"] for r in rows}) != 48:
        raise ValueError("Expected 48 unique original pilot cases")
    data = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows)
    manifest = {"task_pack": "decision-pilot-dev-v0.1", "schema_version": 1,
                "split": "development", "cases": len(rows), "families": len(pairs),
                "cases_sha256": hashlib.sha256(data.encode()).hexdigest(),
                "origin": "Original synthetic Najd decision-model pilot, September 2026",
                "source_hashes": {f: hashlib.sha256((source / f).read_bytes()).hexdigest()
                                  for f in ["pairs.json", "spec.json"]},
                "publication_eligible": False,
                "release_status": "local development; no independent bilingual/rights review",
                "redistribution": "pending explicit dataset release review",
                "transformation": "Expand each original scenario to paired EN/AR states",
                "known_issues": ["T01 wrong-color category is ambiguous; preserve pilot gold"],
                "holdout": "none; these cases have already informed adapter development"}
    output.mkdir(parents=True, exist_ok=False)
    (output / "cases.jsonl").write_text(data)
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.source, args.output), indent=2))


if __name__ == "__main__":
    main()
