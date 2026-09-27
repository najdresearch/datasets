"""Package a complete fresh collection after explicit redistribution authorization."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


def package(snapshot, output, authorization):
    approval = json.loads(authorization.read_text())
    manifest = json.loads((snapshot / "manifest.json").read_text())
    data = (snapshot / "questions.jsonl").read_bytes()
    if hashlib.sha256(data).hexdigest() != manifest["sha256"]:
        raise ValueError("Collection hash changed")
    if not (
        approval.get("public_redistribution_confirmed") is True
        and approval.get("dataset_sha256") == manifest["sha256"]
        and approval.get("reviewer")
        and approval.get("date")
        and set(approval.get("source_ids", [])) == {p["source_id"] for p in manifest["pages"]}
    ):
        raise ValueError("Missing hash-bound source redistribution authorization")
    rows = [json.loads(line) for line in data.decode().splitlines() if line]
    if manifest["missing_ids"] or len(rows) != 333 or len({r["id"] for r in rows}) != 333:
        raise ValueError("Incomplete collection")
    if output.exists():
        raise ValueError("Output exists")
    output.mkdir(parents=True)
    (output / "data").mkdir()
    for row in rows:
        row["rights_status"] = "owner_confirmed_permission"
    published = "".join(
        json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows
    ).encode()
    (output / "data/questions.jsonl").write_bytes(published)
    counts = Counter(r["source_id"] for r in rows)
    manifest.update(
        {
            "publication_sha256": hashlib.sha256(published).hexdigest(),
            "rights_status": "owner_confirmed_permission",
            "rights_basis": "Dataset owner confirmed permission for public redistribution on "
            + approval["date"],
            "ready_for_publication": True,
            "semantic_review": "not_performed",
        }
    )
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    (output / "sources.json").write_text(
        json.dumps(manifest["pages"], ensure_ascii=False, indent=2) + "\n"
    )
    table = "\n".join(
        f"| [{p['source_id']}]({p['canonical_url']}) | {counts[p['source_id']]} |"
        for p in manifest["pages"]
    )
    card = (
        """---
language:
- ar
license: other
license_name: source-specific-permissions
license_link: LICENSE.md
task_categories:
- question-answering
configs:
- config_name: default
  data_files:
  - split: test
    path: data/questions.jsonl
---
# Najd Arabic Riddles and Questions

333 Arabic question–answer pairs freshly collected from nine source pages on 2026-09-27.
The collection includes 298 riddle-labelled items, 11 general questions and 24 Islamic knowledge questions.
Categories follow the source-page grouping, not independent item-level adjudication.
This is a source-attributed historical subset, not a new validated reasoning benchmark.

## Sources and attribution

The questions and answers originate from the following publishers/pages, not from Najd Research.
Najd supplies the collection, selection, normalization and provenance tooling.

| Source page | Selected pairs |
|---|---:|
"""
        + table
        + """

Every row contains `source_url`, `source_id`, `retrieval_url`, `retrieved_at`,
`snapshot_sha256`, source pair positions and the corresponding historical case ID.
`source_url` is the publisher's canonical page. Some `retrieval_url` values use Jina Reader
for text extraction; Jina is not the original author.

## Collection and selection

The deterministic collector parses nine pages and matches the exact question and answer text
against the 333 selected cases from [Najd Benchmark 2026.09.14](https://huggingface.co/datasets/najdresearch/najd-benchmark/tree/cb30c1c9e46c62f691380c3269885cdb8f22f52b).
All 333 pairs matched during this fresh run. Extra page items are not added automatically.
Duplicate occurrences within a page retain their positions. Cross-source duplicates are retained
for historical fidelity, not treated as statistically independent evidence.

This is a fresh snapshot, not a recovery of the missing historical extract.
No translation, generated answers, or answer correction was performed.
The collector and packaging code live in [najdresearch/datasets](https://github.com/najdresearch/datasets).
`manifest.json` records hashes and collection details; `sources.json` lists all source pages.
Raw pages are retained locally and are not redistributed with this dataset.
Live source pages may change; rerunning collection can fail the exact-match check.

## Permissions and limitations

The dataset owner confirmed public redistribution permission for these sources on 2026-09-27,
conditional on source attribution, which is provided above and in every row.
This records the owner's permission statement; it is not an independent legal verification.
No blanket CC or Apache license is granted over third-party text. See `LICENSE.md`.

Answers are preserved as published by their sources and may be incorrect, ambiguous, culturally
specific, or dependent on Arabic wordplay. Religious answers have not had specialist review.
`review_status=not_reviewed` remains unchanged. The test split is a display convention:
these are public cases, not a sealed test set. Do not claim independence from the historical
Najd Benchmark or train on these rows and report held-out performance on that benchmark.
This publication does not modify the original benchmark or historical scores.
"""
    )
    (output / "README.md").write_text(card)
    (output / "LICENSE.md").write_text("""# Source-specific permissions

Original text remains subject to the respective source owners' rights.
Public redistribution was confirmed by the dataset owner on 2026-09-27 with attribution required.
This release does not independently grant unrestricted downstream commercial use, sublicensing,
or redistribution. Consult the linked source owners for applicable reuse terms.
""")
    print(json.dumps({"rows": len(rows), "sha256": manifest["publication_sha256"]}))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for name in ["snapshot", "output", "authorization"]:
        p.add_argument("--" + name, type=Path, required=True)
    a = p.parse_args()
    package(a.snapshot, a.output, a.authorization)
