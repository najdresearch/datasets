"""Offline integrity/coverage audit for a finished System One candidate."""

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def audit(root: Path):
    suite = json.loads((root / "suite.json").read_text())
    entries = suite["pack_paths"]
    summary = []
    policy_splits = defaultdict(set)
    all_ids = set()
    request_groups = defaultdict(list)
    for relative in entries:
        directory = root / relative
        m = json.loads((directory / "manifest.json").read_text())
        raw = (directory / "cases.jsonl").read_bytes()
        if hashlib.sha256(raw).hexdigest() != m["cases_sha256"]:
            raise ValueError("Hash mismatch " + relative)
        rows = [json.loads(x) for x in raw.splitlines()]
        if len(rows) != m["cases"]:
            raise ValueError("Count mismatch")
        families = defaultdict(list)
        tokens = []
        candidate_counts = []
        types = Counter()
        for r in rows:
            if r["id"] in all_ids:
                raise ValueError("Duplicate suite ID " + r["id"])
            all_ids.add(r["id"])
            families[r["family_id"]].append(r)
            if r["split"] != m["split"]:
                raise ValueError("Manifest split mismatch")
            if set(r["expected"]) != set(r["questions"]):
                raise ValueError("Gold fields mismatch")
            for key, q in r["questions"].items():
                g = r["expected"][key]
                kind = q["type"]
                types[kind] += 1
                if kind == "choice":
                    ok = isinstance(g, str) and g in q["criteria"]
                    candidate_counts.append(len(q["criteria"]))
                elif kind == "noul":
                    ok = type(g) is bool
                elif kind == "score":
                    ok = type(g) is int and 0 <= g < len(q["criteria"])
                else:
                    ok = False
                if not ok:
                    raise ValueError("Invalid typed gold " + r["id"])
                for v in r.get("unsafe_values", {}).get(key, []):
                    if type(v) is type(g) and v == g:
                        raise ValueError("Unsafe gold")
            text = json.dumps(r["state"], ensure_ascii=False, sort_keys=True)
            # Character counts only. Token counts depend on the evaluated tokenizer.
            tokens.append(len(text))
            request_groups[hashlib.sha256(text.encode()).hexdigest()].append((relative, r["id"]))
            if relative.startswith("controlled-"):
                policy_splits[r["template_group"]].add(r["split"])
        for group in families.values():
            if len({json.dumps(r["expected"], sort_keys=True) for r in group}) != 1:
                raise ValueError("Paired gold mismatch")
        summary.append(
            {
                "path": relative,
                "cases": len(rows),
                "families": len(families),
                "question_types": dict(types),
                "candidate_count_histogram": dict(Counter(candidate_counts)),
                "max_state_characters": max(tokens),
                "registers": dict(Counter(r.get("register", r["language"]) for r in rows)),
                "cases_sha256": m["cases_sha256"],
            }
        )
    if any(len(s) != 1 for s in policy_splits.values()):
        raise ValueError("Policy group split leakage")
    repeats = [v for v in request_groups.values() if len(v) > 1]
    result = {
        "status": "passed",
        "cases": sum(s["cases"] for s in summary),
        "packs": summary,
        "controlled_policy_groups": len(policy_splits),
        "cross_split_controlled_policy_overlap": 0,
        "exact_repeated_state_groups": len(repeats),
        "repeated_states": repeats,
        "independent_review": False,
        "model_inference": False,
        "publication_eligible": False,
        "limitations": [
            "Exact matching is not semantic deduplication",
            "Known AISA/Arabic_Function_Calling shared IDs represented once",
            "Controlled holdout shares its logical template with development",
            "Capacity report does not establish model runtime compatibility",
        ],
    }
    (root / "audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    lines = [
        "# Dataset release candidate",
        "",
        f"**{result['cases']:,} cases across {len(summary)} packs.** No model inference.",
        "",
        "| Pack | Cases | Families | Largest choice set |",
        "|---|---:|---:|---:|",
    ]
    for s in summary:
        lines.append(
            f"| {s['path']} | {s['cases']} | {s['families']} | "
            f"{max(s['candidate_count_histogram'], default=0)} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "Local candidate: controlled synthetic tests, natural drafts, and public references. "
        "No overall score is defined. Synthetic reserve is group-disjoint but "
        "shares a logical template and public code; it is not a sealed holdout.",
        "",
        "See source-status.json for included, shared-lineage, diagnostic and excluded sources. "
        "Report source/task/register/type separately. Not all source varieties are paired. "
        "No human-independent review or publication approval is claimed.",
    ]
    (root / "README.md").write_text("\n".join(lines) + "\n")
    return result
