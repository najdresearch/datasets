"""Deterministic public reference selection; requires small cached, pinned inputs."""

import argparse
import ast
import csv
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from .decision_sources import checked
from .system_one_release import digest, write_pack


def stratified(rows, key, identity, cap):
    groups = defaultdict(list)
    for r in rows:
        groups[str(key(r))].append(r)
    return [
        r
        for k in sorted(groups)
        for r in sorted(
            groups[k], key=lambda r: digest(("najd-system-one-v1|" + str(identity(r))).encode())
        )[:cap]
    ]


def item(identifier, family, source, register, state, questions, expected, provenance):
    return {
        "id": identifier,
        "family_id": family,
        "task": source,
        "language": "en" if register == "en" else "ar",
        "register": register,
        "split": "public_reference",
        "state": state,
        "questions": questions,
        "expected": expected,
        "unsafe": [],
        "unsafe_annotation_status": "not_annotated",
        "publication_eligible": False,
        "review_status": "source_gold_provisionally_used",
        "independent_review": "pending",
        "provenance": provenance,
    }


def choice(options, register):
    return {
        "type": "choice",
        "instructions": "Select the correct category key."
        if register == "en"
        else "اختر مفتاح الفئة الصحيحة.",
        "criteria": options,
    }


def build(repo, output):
    import pyarrow.parquet as pq

    lock = json.loads((repo / "tasks/system-one-saudi-v0.2/download-lock.json").read_text())
    cached = repo / "build/system-one-sources"
    entries = {e["path"]: e for e in lock["sources"]}

    def raw(name):
        return checked(cached / name, entries[name]["sha256"])

    def provenance(name, **extra):
        return {
            **entries[name],
            "upstream_split": "source_public",
            "transformation": "typed decision mapping",
            "redistribution": "source-license attribution pending release",
            **extra,
        }

    packs = []
    statuses = {}
    output.mkdir(parents=True, exist_ok=False)
    # Complete published Fast Decisions files. Multi-label fields become membership Booleans.
    fast = []
    for name in sorted(n for n in entries if n.startswith("fast-")):
        for i, line in enumerate(raw(name).splitlines()):
            r = json.loads(line)
            qs = {}
            gold = {}
            for j, field in enumerate(r["output"]["classifications"]):
                if field["multi_label"]:
                    for k, label in enumerate(field["labels"]):
                        key = f"q{j}_label{k}"
                        qs[key] = {
                            "type": "noul",
                            "instructions": f"For {field['task']}, does label {label!r} apply?",
                        }
                        gold[key] = label in field["true_label"]
                else:
                    if len(field["true_label"]) != 1:
                        raise ValueError("Unexpected single-label gold")
                    key = f"q{j}"
                    qs[key] = choice({x: x for x in field["labels"]}, "en")
                    qs[key]["instructions"] = f"Select the correct label for {field['task']}."
                    gold[key] = field["true_label"][0]
            family = f"fast-{name}-{i}"
            fast.append(
                item(
                    family,
                    family,
                    "fast-decisions/" + name[5:-6],
                    "en",
                    {"text": r["input"]},
                    qs,
                    gold,
                    provenance(name, upstream_row=i),
                )
            )
    packs.append(
        write_pack(
            output / "fast-decisions", fast, "fast-decisions-reference-v1", "public_reference"
        )
    )
    statuses["fast-decisions"] = {
        "status": "included",
        "cases": len(fast),
        "note": "17 subsets; multi-label membership adaptation; metrics differ from upstream",
    }
    # Banking: five source families per intent, all 77 candidates retained.
    inspection = json.loads(
        (repo / "tasks/system-one-saudi-v0.2/source-inspection.json").read_text()
    )
    bm = inspection["arbanking77"]
    source = repo / "build/source-inspection"
    bank = list(
        csv.DictReader(
            io.StringIO(checked(source / "arbanking77.csv", bm["sha256"]).decode("utf-8-sig"))
        )
    )
    sa = list(
        csv.DictReader(
            io.StringIO(
                checked(source / "Banking77_Arabized_Saudi_test.csv", bm["saudi_sha256"]).decode(
                    "utf-8-sig"
                )
            )
        )
    )
    opts = {lang: {r["Intent_ID"]: r["Intent_" + lang] for r in bank} for lang in ["en", "ar"]}
    reverse = {v: k for k, v in opts["ar"].items()}
    br = []
    for r in stratified(
        [r for r in bank if r["Question_MSA1"] not in ("", "NULL")],
        lambda r: r["Intent_ID"],
        lambda r: r["QID"],
        5,
    ):
        for reg, field, lang in [("en", "Question_en", "en"), ("ar-MSA", "Question_MSA1", "ar")]:
            family = "bank-" + r["QID"]
            prov = {
                **bm,
                "source": "ArBanking77",
                "license": "CC-BY-SA-4.0",
                "upstream_id": r["QID"],
                "upstream_split": r["QuestionID_MSA1"].rstrip("0123456789")
                if lang == "ar"
                else "unknown",
                "transformation": "five hashed-ranked paired source families per intent",
                "redistribution": "attribution/share-alike required",
            }
            br.append(
                item(
                    family + "-" + reg,
                    family,
                    "ArBanking77",
                    reg,
                    {"text": r[field]},
                    {"action": choice(opts[lang], reg)},
                    {"action": r["Intent_ID"]},
                    prov,
                )
            )
    for r in stratified(sa, lambda r: r["label"], lambda r: r["text"], 5):
        family = "bank-sa-" + digest(r["text"].encode())[:20]
        br.append(
            item(
                family,
                family,
                "ArBanking77",
                "ar-SA",
                {"text": r["text"]},
                {"action": choice(opts["ar"], "ar-SA")},
                {"action": reverse[r["label"]]},
                {
                    "source": "ArBanking77",
                    "revision": bm["revision"],
                    "url": "https://github.com/SinaLab/ArBanking77",
                    "license": "CC-BY-SA-4.0",
                    "raw_sha256": bm["saudi_sha256"],
                    "upstream_split": "test",
                    "transformation": "five hashed-ranked rows per intent; unpaired Saudi",
                    "redistribution": "attribution/share-alike required",
                },
            )
        )
    packs.append(
        write_pack(output / "arbanking77", br, "arbanking77-reference-v1", "public_reference")
    )
    statuses["arbanking77"] = {
        "status": "included",
        "cases": len(br),
        "note": "Saudi not paired to English/MSA; all 77 labels",
    }
    # MASSIVE: align by source ID and retain full intent space.
    tables = {
        lang: pq.read_table(io.BytesIO(raw("massive-" + lang + ".parquet")))
        for lang in ["en", "ar"]
    }
    names = json.loads(tables["en"].schema.metadata[b"huggingface"])["info"]["features"]["intent"][
        "names"
    ]
    names_ar = json.loads(tables["ar"].schema.metadata[b"huggingface"])["info"]["features"][
        "intent"
    ]["names"]
    if names != names_ar:
        raise ValueError("MASSIVE intent vocab mismatch")
    mr = []
    ar = {r["id"]: r for r in tables["ar"].to_pylist()}
    candidates = sorted(tables["en"].to_pylist(), key=lambda r: digest(r["id"].encode()))
    utterance_labels = defaultdict(set)
    for r in candidates:
        for locale, text in [("en", r["utt"]), ("ar", ar[r["id"]]["utt"])]:
            utterance_labels[(locale, " ".join(text.split()))].add(r["intent"])
    seen_text = set()
    unique = []
    for r in candidates:
        keys = [("en", " ".join(r["utt"].split())), ("ar", " ".join(ar[r["id"]]["utt"].split()))]
        if any(len(utterance_labels[k]) > 1 or k in seen_text for k in keys):
            continue
        seen_text.update(keys)
        unique.append(r)
    for e in stratified(unique, lambda r: r["intent"], lambda r: r["id"], 5):
        a = ar[e["id"]]
        if e["intent"] != a["intent"]:
            raise ValueError("MASSIVE pair gold mismatch")
        for locale, r in [("en", e), ("ar", a)]:
            reg = "en" if locale == "en" else "ar-source"
            family = "massive-" + r["id"]
            mr.append(
                item(
                    family + "-" + locale,
                    family,
                    "MASSIVE",
                    reg,
                    {"text": r["utt"]},
                    {"action": choice({str(i): n for i, n in enumerate(names)}, reg)},
                    {"action": str(r["intent"])},
                    provenance(
                        "massive-" + locale + ".parquet",
                        upstream_split=r["partition"],
                        source_locale=r["locale"],
                        upstream_id=r["id"],
                        transformation="five aligned families per intent; register unverified",
                    ),
                )
            )
    packs.append(write_pack(output / "massive", mr, "massive-reference-v1", "public_reference"))
    statuses["massive"] = {
        "status": "included",
        "cases": len(mr),
        "note": "Arabic locale retained; fixed English labels; duplicate/conflicting pairs removed",
    }
    # Existing paired action adapter now complete with schemas and decision policy.
    from .decision_sources import build as build_paired

    tmp = output / "adapter-intermediate"
    build_paired(
        repo / "build/source-inspection",
        repo / "tasks/system-one-saudi-v0.2/source-inspection.json",
        tmp,
    )
    paired = [
        json.loads(x)
        for x in (tmp / "cases.jsonl").read_text().splitlines()
        if "paired-msa-saudi-tool-use" in x
    ]
    packs.append(
        write_pack(
            output / "paired-tool-use", paired, "paired-tool-use-reference-v1", "public_reference"
        )
    )
    statuses["paired-msa-saudi-tool-use"] = {
        "status": "included",
        "cases": len(paired),
        "note": "Action-only; tools/arguments execution not scored",
    }
    # AISA is the schema-enriched version of the same upstream function-calling test lineage.
    ais = pq.read_table(io.BytesIO(raw("aisa-test.parquet"))).to_pylist()
    fm = json.loads((repo / "sources/arabic-function-calling.json").read_text())
    old = [
        json.loads(x)
        for x in checked(
            repo / "build/arabic-function-calling/upstream.jsonl", fm["raw_sha256"]
        ).splitlines()
    ]
    overlap = len({r["id"] for r in ais} & {r["id"] for r in old})
    if overlap != len(ais):
        raise ValueError("Unexpected AISA lineage change")
    af = []
    excluded = Counter()
    selected = stratified(
        ais, lambda r: (r["domain"], r["tool_called"], r["requires_function"]), lambda r: r["id"], 5
    )
    for r in selected:
        messages = ast.literal_eval(r["messages"])
        tools = ast.literal_eval(r["tools"])
        # Source assistant targets never enter the model state.
        observed = [
            {"role": m["role"], "content": m["content"]}
            for m in messages
            if m["role"] in ("developer", "user")
        ]
        candidates = {
            t["function"]["name"]: t["function"].get("description", t["function"]["name"])
            for t in tools
        }
        candidates["no_tool"] = "لا حاجة لاستدعاء أداة"
        gold = r["tool_called"] if r["requires_function"] else "no_tool"
        if gold not in candidates:
            excluded["gold_not_in_tools"] += 1
            continue
        family = "arabic-function-lineage-" + r["id"]
        af.append(
            item(
                family,
                family,
                "AISA/Arabic_Function_Calling",
                "ar-" + r["dialect"],
                {"messages": observed, "tools": tools},
                {"action": choice(candidates, "ar")},
                {"action": gold},
                provenance(
                    "aisa-test.parquet",
                    upstream_split=r["metadata"],
                    upstream_id=r["id"],
                    upstream_lineage="HeshamHaroon/Arabic_Function_Calling",
                    transformation="five per domain/tool/call stratum; tool choice only",
                ),
            )
        )
    packs.append(
        write_pack(
            output / "arabic-function-calling",
            af,
            "arabic-function-reference-v1",
            "public_reference",
        )
    )
    statuses["aisa-ar-functioncall"] = {
        "status": "included_shared_lineage",
        "cases": len(af),
        "overlapping_ids": overlap,
        "excluded": dict(excluded),
    }
    statuses["arabic-function-calling"] = {
        "status": "represented_by_schema_enriched_AISA",
        "note": "Do not sum as independent source evidence",
    }
    # Arabic agent eval: single first-step selection only, with source-provided function names.
    am = json.loads((repo / "sources/arabic-agent-eval.json").read_text())
    agent = [
        json.loads(x)
        for x in checked(
            repo / "build/arabic-agent-eval-pinned/upstream.jsonl", am["raw_sha256"]
        ).splitlines()
    ]
    ag = []
    skip = Counter()
    for r in agent:
        calls = r.get("expected_calls", [])
        if len(calls) != 1:
            skip["multi_step_or_no_single_call"] += 1
            continue
        gold = calls[0]["function"]
        options = {n: n for n in r["available_functions"]}
        if gold not in options:
            skip["gold_not_available"] += 1
            continue
        family = "agent-" + r["id"]
        ag.append(
            item(
                family,
                family,
                "arabic-agent-eval",
                "ar-" + r["dialect"],
                {"request": r["instruction"], "available_function_names": r["available_functions"]},
                {"action": choice(options, "ar")},
                {"action": gold},
                {
                    "source": "arabic-agent-eval",
                    "url": am["upstream_url"],
                    "revision": am["revision"],
                    "raw_sha256": am["raw_sha256"],
                    "license": am["license"],
                    "upstream_id": r["id"],
                    "upstream_split": "source_public",
                    "transformation": "single-call name selection; function-name-only diagnostic",
                    "redistribution": "attribution required",
                },
            )
        )
    packs.append(
        write_pack(output / "agent-diagnostic", ag, "agent-name-diagnostic-v1", "public_reference")
    )
    statuses["arabic-agent-eval"] = {
        "status": "diagnostic_only",
        "cases": len(ag),
        "excluded": dict(skip),
        "note": "No full schema; not in primary comparison",
    }
    # Reconstructed public MCQ diagnostics; verify reconstruction report hashes first.
    for name in ["absher", "aratrust"]:
        folder = repo / "build" / name
        report = json.loads((folder / "report.json").read_text())
        data = [
            json.loads(x) for x in checked(folder / "cases.jsonl", report["sha256"]).splitlines()
        ]
        sm = json.loads((repo / "sources" / (name + ".json")).read_text())
        diag = []
        skipped = Counter()
        for r in data:
            ex = r["expected"]
            opts = ex.get("options")
            if opts:
                options = {
                    x.split(")", 1)[0].strip(): x.split(")", 1)[1].strip() for x in opts if ")" in x
                }
            else:
                options = dict(re.findall(r"(?:^|\n)([أبجدABCD])\)\s*([^\n]+)", r["prompt"]))
            gold = ex.get("answerKey", ex.get("answer"))
            if gold not in options or len(options) < 2:
                skipped["not_supported_mcq"] += 1
                continue
            if r.get("audit_status") == "quarantined":
                skipped["upstream_quarantine"] += 1
                continue
            diag.append(
                item(
                    name + "-" + r["id"],
                    name + "-" + r["id"],
                    name,
                    "ar-source",
                    {"text": r["prompt"]},
                    {"action": choice(options, "ar")},
                    {"action": gold},
                    {
                        "source": name,
                        "url": sm["upstream_url"],
                        "revision": sm["revision"],
                        "license": sm["license"],
                        "reconstruction_sha256": report["sha256"],
                        "upstream_id": r["id"],
                        "upstream_split": "source_public",
                        "transformation": "MCQ extraction; diagnostic stratified sample",
                        "redistribution": sm["redistribution_basis"],
                    },
                )
            )
        diag = stratified(diag, lambda r: r["expected"]["action"], lambda r: r["id"], 50)
        packs.append(
            write_pack(
                output / (name + "-diagnostic"), diag, name + "-diagnostic-v1", "public_reference"
            )
        )
        statuses[name] = {
            "status": "diagnostic_only",
            "cases": len(diag),
            "excluded": dict(skipped),
        }
    statuses.update(
        {
            "arabfuncbench": {
                "status": "excluded_access_gate",
                "note": "Requires contact-sharing agreement; not silently accepted",
            },
            "syntha-saudi-support": {
                "status": "inspiration_only",
                "note": "Commercial rights not acquired",
            },
            "silma-rag-qa": {
                "status": "excluded_from_decision_v1",
                "note": "Needs new decision labels and constituent-rights review",
            },
            "arabicragb": {
                "status": "excluded_from_decision_v1",
                "note": "Retrieval/QA gold is not decision gold; no invented negative labels",
            },
            "arasafe": {
                "status": "excluded_rights_unresolved",
                "note": "License undeclared in ledger; permission unresolved",
            },
        }
    )
    index = {
        "packs": packs,
        "source_status": statuses,
        "publication_eligible": False,
        "sampling_seed": "najd-system-one-v1",
    }
    (output / "references.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n")
    return index


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", type=Path, default=Path.cwd())
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    d = build(a.repo.resolve(), a.output)
    print(json.dumps({x["task_pack"]: x["cases"] for x in d["packs"]}, indent=2))


if __name__ == "__main__":
    main()
