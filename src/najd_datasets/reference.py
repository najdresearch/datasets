"""Render a readable reference from the pinned public source ledger."""

from __future__ import annotations

from pathlib import Path

from .pipeline import read_json


def render_source_catalog(ledger_path: Path, output_dir: Path) -> dict[str, int]:
    ledger = read_json(ledger_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = output_dir / "sources"
    pages.mkdir(exist_ok=True)
    catalog = [
        "# Historical source catalog",
        "",
        "These are the source claims recorded for Najd Benchmark 2026.09.14. "
        "A verified link or recorded permission does not certify the meaning of a case. "
        "Recheck rights before any new release.",
        "",
        "| Source | Cases | Certified | Quarantined | Link check | Upstream rebuild |",
        "|---|---:|---:|---:|---|---|",
    ]
    for source in sorted(ledger["sources"], key=lambda item: item["source_id"]):
        name = source["source_id"]
        slug = name.lower().replace("/", "-")
        if name in {
            "arabic-agent-eval", "paired-msa-saudi-tool-use", "QCRI/IslamicFaithQA",
            "arabic-function-calling", "arabicragb",
            "humain-aratruthfulqa",
            "arasafe",
            "mena-values",
            "arbml-quran_hadith", "arbml-saudiirony", "arbml-arabic-rc", "humain-arapro",
            "dialectal-arabic-mmlu",
            "arbml-arabic_dialects_dataset", "arbml-arabic-hate-speech",
            "arbml-dangerous-dataset",
        }:
            rebuild = "verified"
        elif any(
            path.startswith("private/authorized-source-extracts/")
            for path in source.get("source_files", [])
        ):
            rebuild = "original extract missing; fresh content matches"
        else:
            rebuild = "adapter needed"
        catalog.append(
            f"| [{name}](sources/{slug}.md) | {source['case_count']} | "
            f"{source['certified_case_count']} | {source['quarantine_case_count']} | "
            f"{source['verification_status']} | {rebuild} |"
        )
        lines = [
            f"# {name}",
            "",
            f"This source contributed {source['case_count']} historical candidates. "
            f"The release certified {source['certified_case_count']} structurally and "
            f"quarantined {source['quarantine_case_count']}.",
            "",
            "## Origin and collection record",
            "",
            f"- Original source: {source.get('upstream_url') or 'Not recorded'}",
            "- Pinned artifact: "
            f"{source.get('exact_artifact_url') or 'Not verified or not recorded'}",
            "- Source revisions: "
            f"{', '.join(source.get('source_revisions', [])) or 'Not recorded'}",
            "- Ingest revisions: "
            f"{', '.join(source.get('ingest_source_revisions', [])) or 'Not recorded'}",
            f"- Link check: {source['verification_status']} — {source['verification_method']}",
            "",
            "### Recorded source files",
            "",
            *[f"- `{path}`" for path in source.get("source_files", [])],
            "",
            "## Rights and review",
            "",
            f"- Upstream license: `{source['upstream_license']}`",
            f"- Redistribution basis recorded by release: `{source['redistribution_basis']}`",
            f"- Approval authority recorded by release: `{source['approval_authority']}`",
            "- Semantic review: not performed in this release.",
            "- Collection adapter from original upstream bytes: not reconstructed here. "
            "The [reproduction path](../reproduction.md) starts from the preserved "
            "pre-audit export.",
            "",
            "## Evidence",
            "",
            "- [Pinned public source ledger](https://huggingface.co/datasets/najdresearch/najd-benchmark/blob/cb30c1c9e46c62f691380c3269885cdb8f22f52b/datasets/najd-benchmark/2026.09.14/sources.json)",
            "- [Historical reproduction](../reproduction.md)",
            "",
        ]
        if name in {
            "arabic-agent-eval", "paired-msa-saudi-tool-use", "QCRI/IslamicFaithQA",
            "arabic-function-calling", "arabicragb",
            "humain-aratruthfulqa",
            "arasafe",
            "mena-values",
            "arbml-quran_hadith", "arbml-saudiirony", "arbml-arabic-rc", "humain-arapro",
            "dialectal-arabic-mmlu",
            "arbml-arabic_dialects_dataset", "arbml-arabic-hate-speech",
            "arbml-dangerous-dataset",
        }:
            index = lines.index(
                "- Collection adapter from original upstream bytes: not reconstructed here. "
                "The [reproduction path](../reproduction.md) starts from the preserved "
                "pre-audit export."
            )
            count = source["case_count"]
            manifest = {
                "QCRI/IslamicFaithQA": "islamic-faith-qa",
                "arbml-quran_hadith": "arbml-quran-hadith",
                "arbml-arabic_dialects_dataset": "arbml-arabic-dialects",
            }.get(name, name)
            lines[index] = (
                f"- Original upstream bytes reproduce all {count} public rows. "
                "Run `uv run najd-datasets reproduce-source "
                f"sources/{manifest}.json --output build/{manifest}` "
                f"using the [pinned adapter manifest](../../sources/{manifest}.json)."
            )
        (pages / f"{slug}.md").write_text("\n".join(lines), encoding="utf-8")
    catalog.extend(["", "[How the rows are reproduced](reproduction.md).", ""])
    (output_dir / "source-catalog.md").write_text("\n".join(catalog), encoding="utf-8")
    return {"sources": len(ledger["sources"])}
