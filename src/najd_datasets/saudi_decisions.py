"""Build unreviewed original EN/MSA/Saudi development decisions, without model calls."""

import argparse
import hashlib
import json
import random
from collections import Counter
from pathlib import Path

REGISTERS = ("en", "ar-MSA", "ar-SA")


def build(source: Path, output: Path) -> dict:
    raw = source.read_bytes()
    families = json.loads(raw)
    seen = set()
    rows = []
    table = [
        "# Saudi decision drafts — human review required",
        "",
        "Original fictional policies. No model results or reviewed gold labels.",
        "",
        "| ID / workflow | English | MSA | Saudi | Draft action / rationale |",
        "|---|---|---|---|---|",
    ]
    for f in families:
        if f["id"] in seen or f["split"] != "development":
            raise ValueError("Duplicate family or non-development input")
        seen.add(f["id"])
        kind = f.get("question_type", "choice")
        gold = f["expected"]
        gold_valid = (
            (kind == "choice" and gold in f["options"])
            or (kind == "noul" and type(gold) is bool)
            or (
                kind == "score" and type(gold) is int and 0 <= gold < len(f["score_criteria"]["en"])
            )
        )
        if set(f["requests"]) != set(REGISTERS) or not gold_valid:
            raise ValueError("Missing aligned variants or invalid action")
        if any(not x.strip() for x in f["requests"].values()):
            raise ValueError("Empty language variant")
        if kind == "score" and len(f["score_criteria"]["ar"]) != len(f["score_criteria"]["en"]):
            raise ValueError("Ordinal scales must align across languages")
        unsafe = f.get("unsafe_values", f.get("unsafe", []))
        for value in unsafe:
            if type(value) is type(gold) and value == gold:
                raise ValueError("Gold decision cannot also be unsafe")
            if type(value) is not type(gold):
                raise ValueError("Unsafe value type must match the decision")
            if kind == "choice" and value not in f["options"]:
                raise ValueError("Unsafe choice must be an available option")
        keys = list(f.get("options", {}))
        random.Random(f["id"]).shuffle(keys)  # identical order across paired variants
        for register in REGISTERS:
            lang = "en" if register == "en" else "ar"
            question = {
                "type": kind,
                "instructions": f.get("instructions", {}).get(
                    lang,
                    "Choose the next action using the supplied policy."
                    if lang == "en"
                    else "اختر الإجراء التالي بناءً على السياسة المرفقة.",
                ),
            }
            if kind == "choice":
                question["criteria"] = {k: f["options"][k][lang] for k in keys}
            elif kind == "score":
                question["criteria"] = f["score_criteria"][lang]
            rows.append(
                {
                    "id": f"{f['id']}-{register}",
                    "family_id": f["id"],
                    "template_group": f["template_group"],
                    "task": f["domain"],
                    "language": lang,
                    "register": register,
                    "split": "development",
                    "state": {"policy": f["policy"][lang], "request": f["requests"][register]},
                    "questions": {"action": question},
                    "expected": {"action": f["expected"]},
                    "unsafe": f.get("unsafe", []),
                    "unsafe_values": {"action": f.get("unsafe_values", f.get("unsafe", []))},
                    "unsafe_annotation_status": f.get("unsafe_annotation_status", "not_annotated"),
                    "unsafe_rationale": f.get("unsafe_rationale", "See supplied decision policy"),
                    "review_status": f.get("review_status", "draft_unreviewed"),
                    "acceptance_status": f.get("acceptance_status", "not_recorded"),
                    "independent_review": "pending",
                    "reviewer": None,
                    "rationale": f["rationale"],
                    "provenance": {
                        "origin": f["origin"],
                        "source_family": f["id"],
                        "license": "release_pending",
                        "redistribution": "not_approved",
                        "transformation": "Authored aligned variants from fictional scenario",
                    },
                }
            )
        cells = [
            f"{f['id']} / {f['domain']}",
            *[f["requests"][r] for r in REGISTERS],
            f"{f['expected']}: {f['rationale']}",
        ]
        table.append(
            "| " + " | ".join(x.replace("|", "\\|").replace("\n", " ") for x in cells) + " |"
        )
    if not rows:
        raise ValueError("Empty pack")
    for f in families:
        table += ["", f"## {f['id']} — policy", "", f["policy"]["en"], "", f["policy"]["ar"]]
    data = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows)
    manifest = {
        "task_pack": families[0].get("pack_version", "saudi-decisions-draft-v0.3")
        if any("question_type" in f for f in families)
        else "saudi-decisions-draft-v0.2",
        "question_types": dict(Counter(f.get("question_type", "choice") for f in families)),
        "schema_version": 1,
        "cases": len(rows),
        "families": len(families),
        "policy_groups": len({f["template_group"] for f in families}),
        "acceptance_status_counts": dict(
            Counter(f.get("acceptance_status", "not_recorded") for f in families)
        ),
        "split": "development",
        "cases_sha256": hashlib.sha256(data.encode()).hexdigest(),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "publication_eligible": False,
        "review_status": "draft_unreviewed",
        "registers": list(REGISTERS),
        "domains": dict(Counter(f["domain"] for f in families)),
        "limitations": [
            "Safety annotations are drafts where supplied, not independent review",
            "No independent bilingual review",
            "Only development cases",
            "Fictional policies are not real agency or company rules",
            "Shared workflow templates are not independent holdout families",
        ],
    }
    output.mkdir(parents=True, exist_ok=False)
    (output / "cases.jsonl").write_text(data)
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (output / "review.md").write_text("\n".join(table) + "\n")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.source, args.output), indent=2))


if __name__ == "__main__":
    main()
