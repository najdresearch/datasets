"""Package the 31 historical Najd cases and their required original fixture files."""

import argparse
import hashlib
import json
import shutil
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(original, reference, fixtures, output):
    if output.exists():
        raise ValueError("Output already exists")
    original_hash = digest(original)
    if original_hash != "cde88fc8d3780ae81ff776dcb56a90e5f5f29bf132089ba323015d3e7876b014":
        raise ValueError("Unexpected archived input")
    if digest(reference) != "5b108a254466d621da41e53acfa5b6302b310c4f9f80d8e87124d605cbfc5ed8":
        raise ValueError("Unexpected historical reference")
    raw = [json.loads(line) for line in original.read_text().splitlines() if line]
    historical = [json.loads(line) for line in reference.read_text().splitlines() if line]
    chosen = [
        r for r in historical if r.get("provenance", {}).get("sourceId") == "najd-benchmark-v1"
    ]
    assert len(chosen) == len({r["id"] for r in chosen}) == 31
    by_id = {r["id"]: (i, r) for i, r in enumerate(raw, 1)}
    output.mkdir(parents=True)
    (output / "data").mkdir()
    (output / "original").mkdir()
    rows, originals, mapping = [], [], []
    for case in sorted(chosen, key=lambda x: x["id"]):
        position, source = by_id[case["id"]]
        assert source["prompt"] == case["prompt"] and source["expected"] == case["expected"]
        assert position == case["provenance"]["sourceRow"]
        originals.append(source)
        mapping.append({"id": case["id"], "original_source_row": position})
        rows.append(
            {
                "id": case["id"],
                "prompt": case["prompt"],
                "expected_json": json.dumps(case["expected"], ensure_ascii=False, sort_keys=True),
                "language": case["language"],
                "track": case["track"],
                "fixture": case.get("fixture"),
                "source_id": "najd-benchmark-v1",
                "original_source_row": position,
                "review_status": "not_reviewed",
            }
        )
    for name, data in [
        ("data/cases.jsonl", rows),
        ("original/cases.jsonl", originals),
        ("historical-cases.jsonl", chosen),
    ]:
        (output / name).write_text(
            "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in data)
        )
    for fixture in sorted({r["fixture"] for r in rows if r["fixture"]}):
        if fixture not in {"docs", "rag", "agent_contacts"}:
            raise ValueError("Unreviewed fixture")
        shutil.copytree(fixtures / fixture, output / "fixtures" / fixture)
    manifest = {
        "version": "1.0.0",
        "rows": 31,
        "origin": "Najd historical m3-saudi-v1 subset",
        "original_archive_commit": "211d3df42c6b9dba1838c1b94e942d30724f09cd",
        "original_64_row_file_sha256": original_hash,
        "selection": mapping,
        "reference_sha256": digest(reference),
        "semantic_review": "not_performed",
        "publication_authority": "Dataset owner explicitly requested public release on 2026-09-27",
        "files": {
            str(p.relative_to(output)): digest(p) for p in sorted(output.rglob("*")) if p.is_file()
        },
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    (output / "README.md").write_text("""---
language:
- ar
- en
license: other
license_name: historical-najd-source-terms
license_link: LICENSE.md
configs:
- config_name: default
  data_files:
  - split: test
    path: data/cases.jsonl
---
# Najd Legacy 31

The 31 Najd-authored historical cases selected from the earlier 64-case m3-saudi-v1 input into Najd Benchmark 2026.09.14. Published at the dataset owner's request to make these inputs accessible.

## Files and reproducibility

- `data/cases.jsonl`: uniform viewer-friendly rows; `expected_json` preserves the heterogeneous answer rubric as JSON.
- `original/cases.jsonl`: original selected case objects, unchanged in content.
- `historical-cases.jsonl`: corresponding released rows, including historical audit metadata.
- `fixtures/`: original document, RAG and contacts fixtures needed by six selected cases. Names and business scenarios are benchmark fixture content, not a source of factual company claims.
- `manifest.json`: exact selected IDs, original row positions, file hashes and archive commit.

The source is Najd's earlier local dataset, not an external website. Original authoring/generation records are unavailable. Publication makes this subset accessible; it does not recover the complete original 64-row file or prove an upstream generation procedure.

The historical reference is [Najd Benchmark at cb30c1c](https://huggingface.co/datasets/najdresearch/najd-benchmark/tree/cb30c1c9e46c62f691380c3269885cdb8f22f52b). Build code is maintained in [najdresearch/datasets](https://github.com/najdresearch/datasets).

## Limits

Historical candidate material, not a validated benchmark. `not_reviewed` is retained; answers and rubrics have not undergone independent semantic review. Keyword rubrics are not comprehensive correctness tests. Public cases are not sealed held-out evaluation. Some fixtures intentionally contain false distractors marked untrusted. Facts are historical and should not be assumed current. This release does not change the existing benchmark or scores.
""")
    (output / "LICENSE.md").write_text(
        "Publicly accessible historical Najd source material, published at the dataset owner’s request. No new permissive reuse license is asserted by this release. Contact Najd Research for reuse terms.\n"
    )
    print(json.dumps({"rows": 31, "output": str(output), "files": len(manifest["files"])}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["original", "reference", "fixtures", "output"]:
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    build(args.original, args.reference, args.fixtures, args.output)
