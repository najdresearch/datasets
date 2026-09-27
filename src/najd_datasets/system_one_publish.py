"""Stage allowlisted System One packs for publication without changing the frozen input."""

import argparse
import hashlib
import json
import shutil
from pathlib import Path


def sha(data):
    return hashlib.sha256(data).hexdigest()


def examples(prepared):
    """Render real original cases, never invented demonstrations or model predictions."""
    natural = next((rows for name, _, rows in prepared if name == "natural-development"), [])
    if not natural:
        return []
    selected = []
    for kind, register in [("choice", "en"), ("noul", "ar-MSA"), ("score", "ar-SA")]:
        row = next(
            (
                r
                for r in natural
                if r.get("register") == register
                and any(q["type"] == kind for q in r["questions"].values())
            ),
            None,
        )
        if row:
            selected.append((kind, row))
    lines = [
        "",
        "## What is inside?",
        "",
        "Each case gives a model some context and asks it to make a small decision. "
        "The expected answer comes from the dataset, not from a model run.",
        "",
        "| Decision | Answer format | Example use |",
        "|---|---|---|",
        "| Choice | One allowed string key | Route a service request |",
        "| Boolean (`noul`) | `true` or `false` | Check whether a policy permits an action |",
        "| Score | An integer index into the supplied criteria | Select an urgency level |",
        "",
        "### The same request in three registers",
        "",
        "These are actual aligned rows from `natural-development`. "
        "The policy and question are localized too; the table shows the request only.",
        "",
        "| Case ID | Register | Request | Expected answer |",
        "|---|---|---|---|",
    ]
    if selected:
        family = selected[0][1]["family_id"]
        for r in natural:
            if r["family_id"] == family:
                request = str(r["state"].get("request", r["state"])).replace("|", "\\|")
                gold = json.dumps(r["expected"], ensure_ascii=False)
                lines.append(f"| `{r['id']}` | {r['register']} | {request} | `{gold}` |")
    for kind, row in selected:
        labels = {
            "choice": "Choice — English",
            "noul": "Boolean — MSA",
            "score": "Score — Saudi Arabic",
        }
        lines += [
            "",
            f"### {labels[kind]}",
            "",
            f"Actual case: `{row['id']}`. "
            "The supplied policy is fictional; this is not government or company guidance.",
            "",
            "```json",
            json.dumps(
                {k: row[k] for k in ["id", "state", "questions", "expected"]},
                ensure_ascii=False,
                indent=2,
            ),
            "```",
        ]
    lines += [
        "",
        "Original cases cover government routing, complaints, prerequisites, banking, "
        "telecom/logistics, HR/IT, procurement, and tool/text-UI actions. "
        "Adapted upstream packs add intent classification, tool selection, and "
        "language/culture diagnostics; see the pack table and per-subset licenses.",
    ]
    return lines


def stage(source, output, clearance, notices=None):
    suite = json.loads((source / "suite.json").read_text())
    if not clearance.get("publication_authorized"):
        raise ValueError("Publication authorization and license choice required")
    selected = clearance["packs"]
    if not selected or set(selected) - set(suite["pack_paths"]):
        raise ValueError("Unknown or empty pack allowlist")
    # Validate every selected byte before creating the staging directory.
    prepared = []
    for name, rights in selected.items():
        if rights.get("status") != "cleared" or not rights.get("license"):
            raise ValueError("Uncleared pack: " + name)
        if not rights.get("basis") or not rights.get("privacy_review"):
            raise ValueError("Missing rights or privacy evidence: " + name)
        path = source / name
        manifest = json.loads((path / "manifest.json").read_text())
        data = (path / "cases.jsonl").read_bytes()
        if sha(data) != manifest["cases_sha256"]:
            raise ValueError("Input hash mismatch: " + name)
        rows = [json.loads(x) for x in data.splitlines()]
        if len(rows) != manifest["cases"]:
            raise ValueError("Input count mismatch")
        for row in rows:
            row["release_rights"] = rights
            if not name.startswith("references/"):
                row["provenance"]["license"] = rights["license"]
                row["provenance"]["redistribution"] = "CC BY 4.0; author authorized public draft"
            row["publication_eligible"] = True
            row["evaluation_claim_eligible"] = False
            # A public draft is not an independently reviewed evaluation result.
            row["independent_review"] = "pending"
        prepared.append((name, manifest, rows))
    output.mkdir(parents=True, exist_ok=False)
    configs, packs, files = [], [], {}
    for name, manifest, rows in prepared:
        destination = output / name
        destination.mkdir(parents=True)
        data = "".join(
            json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows
        ).encode()
        manifest.update(
            cases_sha256=sha(data),
            source_cases_sha256=manifest["cases_sha256"],
            redistribution_cleared=True,
            publication_eligible=True,
            evaluation_claim_eligible=False,
        )
        (destination / "cases.jsonl").write_bytes(data)
        (destination / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
        )
        # Stable viewer columns avoid Arrow unions for bool/int/string decision outputs.
        viewer = output / "viewer" / name.replace("/", "--")
        viewer.mkdir(parents=True)
        view_rows = []
        for row in rows:
            view_rows.append(
                {
                    **{
                        k: row.get(k)
                        for k in ["id", "family_id", "task", "language", "register", "split"]
                    },
                    **{
                        k + "_json": json.dumps(row.get(k), ensure_ascii=False, sort_keys=True)
                        for k in ["state", "questions", "expected"]
                    },
                }
            )
        (viewer / "data.jsonl").write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in view_rows)
        )
        metadata = output / "metadata" / name.replace("/", "--")
        metadata.mkdir(parents=True)
        (metadata / "provenance-and-rights.jsonl").write_text(
            "".join(
                json.dumps(
                    {
                        "id": row["id"],
                        "pack": name,
                        "provenance": row.get("provenance"),
                        "release_rights": row["release_rights"],
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                )
                + "\n"
                for row in rows
            )
        )
        configs.append(
            {
                "config_name": name.replace("/", "--"),
                "data_files": [
                    {
                        "split": "train" if manifest["split"] == "development" else "test",
                        "path": str((viewer / "data.jsonl").relative_to(output)),
                    }
                ],
            }
        )
        packs.append(manifest)
    release = {
        "release": "system-one-v1-public-draft",
        "pack_paths": list(selected),
        "packs": packs,
        "status": "public_research_draft",
        "independent_review": "pending",
        "excluded_packs": sorted(set(suite["pack_paths"]) - set(selected)),
    }
    (output / "suite.json").write_text(json.dumps(release, indent=2, ensure_ascii=False) + "\n")
    (output / "clearance.json").write_text(
        json.dumps(clearance, indent=2, ensure_ascii=False) + "\n"
    )
    # JSON is valid YAML and accepted in HF card frontmatter.
    card = {
        "language": ["en", "ar"],
        "license": "other",
        "license_name": "per-subset-licenses",
        "license_link": "https://huggingface.co/datasets/najdresearch/system-one/blob/main/clearance.json",
        "configs": configs,
        "tags": ["synthetic", "decision-models", "evaluation"],
    }
    lines = [
        "---",
        json.dumps(card, indent=2),
        "---",
        "# Najd System One — public research draft",
        "",
        (
            "Decision tasks in English, MSA and Saudi Arabic. This draft is for research "
            "and debugging; independent linguistic and label review is pending."
        ),
        "",
        "| Pack | Cases | License |",
        "|---|---:|---|",
    ]
    lines += [f"| {name} | {m['cases']} | {selected[name]['license']} |" for name, m, _ in prepared]
    lines += examples(prepared)
    lines += [
        "",
        "## Files and columns",
        "",
        "| File | What it contains |",
        "|---|---|",
        "| `viewer/<config>/data.jsonl` | IDs, task, language, split, inputs and answers |",
        "| `metadata/<config>/provenance-and-rights.jsonl` | Sources and rights, keyed by `id` |",
        "| `<pack>/cases.jsonl` | Original typed benchmark rows, including complete metadata |",
        "| `clearance.json` and `licenses/` | Subset permissions and attribution notices |",
        "",
        "Join viewer rows to the metadata file for the same configuration using `id`. "
        "The viewer omits `provenance_json` and `release_rights_json`. "
        "Benchmark rows keep their original bytes for reproducible experiments.",
        "",
        "`state_json` contains the supplied context, `questions_json` defines the decision "
        "and allowed answers, and `expected_json` contains the gold answer. Parse these "
        "three columns with `json.loads` when using the viewer export.",
        "",
        "## Use and limitations",
        "",
        (
            "Viewer fields ending in `_json` preserve heterogeneous decision types as "
            "JSON strings. Benchmark runners use the original typed `cases.jsonl` files "
            "and verify their manifest hashes."
        ),
        (
            "The viewer calls development data `train` for tooling compatibility; this "
            "is not a training recommendation. Original split names remain in each row. "
            "Published reserved cases are not secret holdouts."
        ),
        (
            "Policies in Najd-authored data are fictional. Controlled cases share one "
            "logical template; translations are correlated. Do not treat every row as "
            "independent or pool packs into one headline score."
        ),
        (
            "The Saudi controlled wording is record-style, not natural customer "
            "conversation. Source Arabic locales are not automatically Saudi dialect."
        ),
        (
            "Rights apply per subset; no blanket relicensing of third-party material. "
            "Attribution and transformations are retained in row provenance and "
            "clearance.json."
        ),
        "",
        "## Reproduction",
        "",
        (
            "Builders: https://github.com/najdresearch/datasets . Scoring: "
            "https://github.com/najdresearch/benchmark . Pin the Hugging Face commit SHA "
            "and verify release-lock.json before evaluation."
        ),
    ]
    (output / "README.md").write_text("\n".join(lines) + "\n")
    if notices is not None:
        shutil.copytree(notices, output / "licenses")
    for file in sorted(output.rglob("*")):
        if file.is_file():
            files[str(file.relative_to(output))] = sha(file.read_bytes())
    (output / "release-lock.json").write_text(
        json.dumps({"files": files, "cases": sum(m["cases"] for _, m, _ in prepared)}, indent=2)
        + "\n"
    )
    return {"cases": sum(m["cases"] for _, m, _ in prepared), "packs": len(prepared)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--clearance", type=Path, required=True)
    p.add_argument("--notices", type=Path)
    a = p.parse_args()
    print(stage(a.source, a.output, json.loads(a.clearance.read_text()), a.notices))


if __name__ == "__main__":
    main()
