"""Hash-verified, offline public-reference decision adapters. No model or network calls."""

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path


def checked(path, expected):
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError(f"Source hash mismatch: {path.name}")
    return data


def row(identifier, family, register, state, options, gold, provenance):
    if gold not in options:
        raise ValueError(f"Unknown source gold {gold}")
    return {
        "id": identifier,
        "family_id": family,
        "task": provenance["source"],
        "language": "en" if register == "en" else "ar",
        "register": register,
        "split": "public_reference",
        "state": state,
        "questions": {
            "action": {
                "type": "choice",
                "instructions": (
                    "Select the correct action or intent. Return its key."
                    if register == "en"
                    else "اختر الإجراء أو النية الصحيحة وأعد مفتاحها."
                ),
                "criteria": options,
            }
        },
        "expected": {"action": gold},
        "provenance": provenance,
        "review_status": "draft_adaptation",
        "reviewer": None,
        "unsafe": [],
        "unsafe_annotation_status": "not_annotated",
    }


def build(raw_dir, inspection, output):
    meta = json.loads(inspection.read_text())
    # The inspection file is a versioned trust root, not a hash inferred from incoming bytes.
    source_manifest = Path(__file__).parents[2] / "sources/paired-msa-saudi-tool-use.json"
    pm = json.loads(source_manifest.read_text())
    paired = [
        json.loads(x) for x in checked(raw_dir / "paired.jsonl", pm["raw_sha256"]).splitlines()
    ]
    bank = list(
        csv.DictReader(
            io.StringIO(
                checked(raw_dir / "arbanking77.csv", meta["arbanking77"]["sha256"]).decode(
                    "utf-8-sig"
                )
            )
        )
    )
    saudi = list(
        csv.DictReader(
            io.StringIO(
                checked(
                    raw_dir / "Banking77_Arabized_Saudi_test.csv",
                    meta["arbanking77"]["saudi_sha256"],
                ).decode("utf-8-sig")
            )
        )
    )
    registry = json.loads(checked(raw_dir / "tools.yaml", meta["paired"]["tools"]["sha256"]))
    tools_by_name = {t["name"]: t for t in registry["tools"]}
    rows = []
    actions = ["call_tool", "ask_clarification", "answer_without_tool", "report_unsupported"]
    if {r["expected"]["action"] for r in paired} - set(actions):
        raise ValueError("Unexpected source action")
    # Only project to action selection. Do not claim tool-name/argument/execution evaluation.
    options = {a: a.replace("_", " ") for a in actions}
    for r in paired:
        if r["variety"] not in ("msa", "saudi_general"):
            raise ValueError("Unknown source variety")
        reg = "ar-MSA" if r["variety"] == "msa" else "ar-SA"
        rows.append(
            row(
                "paired-" + r["variant_id"],
                "paired-" + r["pair_id"],
                reg,
                {
                    "request": r["user_request"],
                    "decision_policy": (
                        "This is a synthetic read-only mock-tool environment. Call a supported "
                        "tool when all required arguments are known. Ask for missing required "
                        "arguments; do not invent defaults. Answer without a tool when "
                        "the supplied "
                        "information is sufficient. Report unsupported when the requested "
                        "operation "
                        "cannot be done using the available tools. Judge the supplied "
                        "mock schemas, "
                        "not real-world service availability."
                    ),
                    "context": r["context"],
                    "available_tools": [tools_by_name[name] for name in r["available_tools"]],
                    "tool_reference_context": registry["reference_context"],
                },
                options,
                r["expected"]["action"],
                {
                    "source": "paired-msa-saudi-tool-use",
                    "revision": pm["revision"],
                    "url": pm["upstream_url"],
                    "license": pm["license"],
                    "upstream_split": r["split"],
                    "upstream_id": r["variant_id"],
                    "transformation": (
                        "action-only projection with pinned tool schemas; semantic review required"
                    ),
                    "redistribution": "pending new-release review",
                },
            )
        )
    en_options = {r["Intent_ID"]: r["Intent_en"] for r in bank}
    ar_options = {r["Intent_ID"]: r["Intent_ar"] for r in bank}
    reverse = {v: k for k, v in ar_options.items()}
    # Deterministic small inspection sample, not a representative benchmark.
    used = set()
    for r in bank:
        if r["Intent_ID"] in used or r["Question_MSA1"] in ("", "NULL"):
            continue
        used.add(r["Intent_ID"])
        provenance = {
            "source": "ArBanking77",
            "revision": meta["arbanking77"]["revision"],
            "url": "https://github.com/SinaLab/ArBanking77",
            "license": "CC-BY-SA-4.0",
            "upstream_id": r["QID"],
            "upstream_variant_id": r["QuestionID_MSA1"],
            "upstream_split": r["QuestionID_MSA1"].rstrip("0123456789"),
            "transformation": "first available EN/MSA pair per intent, capped at 20 intents",
            "redistribution": "pending new-release attribution review",
        }
        for reg, text, opts in [
            ("en", r["Question_en"], en_options),
            ("ar-MSA", r["Question_MSA1"], ar_options),
        ]:
            family = "bank-" + r["QID"]
            rows.append(
                row(
                    family + "-" + reg,
                    family,
                    reg,
                    {"request": text},
                    opts,
                    r["Intent_ID"],
                    {
                        **provenance,
                        "upstream_split": provenance["upstream_split"]
                        if reg == "ar-MSA"
                        else "unknown",
                        "upstream_variant_id": provenance["upstream_variant_id"]
                        if reg == "ar-MSA"
                        else r["QID"],
                    },
                )
            )
        if len(used) == 20:
            break
    used = set()
    for index, r in enumerate(saudi):
        if r["label"] in used:
            continue
        used.add(r["label"])
        identifier = f"bank-sa-unpaired-{index}"
        rows.append(
            row(
                identifier,
                identifier,
                "ar-SA",
                {"request": r["text"]},
                ar_options,
                reverse[r["label"]],
                {
                    "source": "ArBanking77",
                    "revision": meta["arbanking77"]["revision"],
                    "url": "https://github.com/SinaLab/ArBanking77",
                    "license": "CC-BY-SA-4.0",
                    "upstream_split": "test",
                    "upstream_row_index": index,
                    "transformation": "first Saudi row per label, capped at 20; unpaired",
                    "redistribution": "pending new-release attribution review",
                },
            )
        )
        if len(used) == 20:
            break
    if len({r["id"] for r in rows}) != len(rows):
        raise ValueError("Duplicate adapted ID")
    data = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows)
    manifest = {
        "task_pack": "public-decision-adapter-smoke-v0.3",
        "cases": len(rows),
        "cases_sha256": hashlib.sha256(data.encode()).hexdigest(),
        "split": "public_reference",
        "publication_eligible": False,
        "reviewer": None,
        "review_status": "draft_adaptation",
        "source_inspection_sha256": hashlib.sha256(inspection.read_bytes()).hexdigest(),
        "limitations": [
            "Nonrepresentative inspection samples",
            "No newly sealed holdout",
            "Paired tools action-only with pinned English tool schemas",
            "Saudi banking examples unpaired",
            "77 banking choices retained",
            "Mixed English tool labels and Arabic requests",
            "No independent semantic review",
        ],
    }
    output.mkdir(parents=True, exist_ok=False)
    (output / "cases.jsonl").write_text(data)
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--raw-dir", type=Path, required=True)
    p.add_argument("--inspection", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(build(a.raw_dir, a.inspection, a.output), indent=2))


if __name__ == "__main__":
    main()
