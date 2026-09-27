"""Fetch the nine recorded pages and match the historical 333 selected pairs.

Raw snapshots and candidate text belong in an ignored output directory until rights are cleared.
No translations, answer corrections, or model calls are made.
"""

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import Request, urlopen

from najd_datasets.riddle_parsers import PARSERS


def sha(data):
    return hashlib.sha256(data).hexdigest()


def collect(sources_path, reference, output):
    if output.exists():
        raise ValueError("Output exists; choose a new snapshot directory")
    output.mkdir(parents=True)
    (output / "raw").mkdir()
    sources = json.loads(sources_path.read_text())["sources"]
    historical = [json.loads(line) for line in reference.read_text().splitlines() if line]
    selected = [
        r
        for r in historical
        if r.get("provenance", {}).get("sourceId") in {s["source_id"] for s in sources}
    ]
    if len(selected) != 333 or len({r["id"] for r in selected}) != 333:
        raise ValueError("Expected 333 unique historical reference cases")
    pages, rows, missing = [], [], []
    for source in sources:
        request = Request(
            source["retrieval_url"], headers={"User-Agent": "NajdResearchDatasetCollector/1.0"}
        )
        with urlopen(request, timeout=60) as response:
            raw = response.read()
        path = output / "raw" / (source["source_id"] + ".txt")
        path.write_bytes(raw)
        pairs = PARSERS[source["parser"]](raw.decode("utf-8"))
        indexed = {}
        for number, (question, answer) in enumerate(pairs, 1):
            indexed.setdefault((question, answer), []).append(number)
        page = {
            **source,
            "retrieved_at": datetime.now(UTC).isoformat(),
            "raw_sha256": sha(raw),
            "extracted_pairs": len(pairs),
        }
        pages.append(page)
        for old in selected:
            if old["provenance"]["sourceId"] != source["source_id"]:
                continue
            key = (old["prompt"], old["expected"]["answer"])
            if key not in indexed:
                missing.append(old["id"])
                continue
            rows.append(
                {
                    "id": old["id"],
                    "question_ar": key[0],
                    "answer_ar": key[1],
                    "source_id": source["source_id"],
                    "source_url": source["canonical_url"],
                    "retrieval_url": source["retrieval_url"],
                    "retrieved_at": page["retrieved_at"],
                    "snapshot_sha256": page["raw_sha256"],
                    "source_pair_positions": indexed[key],
                    "historical_source_item_id": old["provenance"]["sourceItemId"],
                    "category": "islamic_knowledge"
                    if "islamic" in source["source_id"]
                    else "general_questions"
                    if "contest" in source["source_id"]
                    else "riddles",
                    "rights_status": "pending",
                }
            )
        print(source["source_id"], "parsed", len(pairs), flush=True)
    rows.sort(key=lambda r: r["id"])
    data = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows).encode()
    (output / "questions.jsonl").write_bytes(data)
    manifest = {
        "version": 1,
        "rows": len(rows),
        "sha256": sha(data),
        "missing_ids": missing,
        "historical_reference_sha256": sha(reference.read_bytes()),
        "sources_manifest_sha256": sha(sources_path.read_bytes()),
        "parser_sha256": sha(
            Path(__import__("najd_datasets.riddle_parsers", fromlist=["x"]).__file__).read_bytes()
        ),
        "pages": pages,
        "rights_status": "pending",
        "ready_for_publication": False,
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    if missing:
        raise ValueError(f"{len(missing)} selected pairs not recovered; see manifest")
    print(json.dumps({"rows": len(rows), "sha256": sha(data)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, default=Path("sources/arabic-riddles-pages.json"))
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    collect(args.sources, args.reference, args.output)
