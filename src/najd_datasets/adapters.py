"""Pinned, source-specific collectors with comparison to historical public rows."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from .pipeline import PipelineError, digest, read_jsonl, write_json, write_jsonl


def _fetch(url: str) -> bytes:
    for attempt in range(3):
        try:
            with urlopen(url, timeout=30) as response:
                return response.read()
        except URLError:
            if attempt == 2:
                raise
    raise AssertionError("unreachable")


def arabic_agent_eval(raw_path: Path, output_path: Path, revision: str) -> dict[str, object]:
    rows = []
    for index, source in enumerate(read_jsonl(raw_path), 1):
        prompt = (
            source.get("instruction")
            or source.get("initial_instruction")
            or source.get("prompt", "")
        )
        if not prompt:
            continue
        rows.append(
            {
                "id": f"arabic-agent-eval-{source.get('id', index)}",
                "track": "agentic_tool_use",
                "language": "ar",
                "prompt": prompt,
                "expected": {
                    "tool_calls": source.get("expected_calls", []),
                    "category": source.get("category"),
                    "difficulty": source.get("difficulty"),
                },
                "tags": ["arabic-agent-eval", "agentic_tool_use", str(source.get("dialect", ""))],
                "provenance": {
                    "sourceId": "arabic-agent-eval",
                    "sourceFile": "sources/github/arabic-agent-eval/data/all.jsonl",
                    "sourceRow": index,
                    "upstreamId": source.get("id"),
                    "sourceRevision": revision,
                },
                "review_status": "not_reviewed",
                "audit_status": "certified",
                "audit_issues": [],
            }
        )
    write_jsonl(output_path, rows)
    return {
        "source_id": "arabic-agent-eval",
        "rows": len(rows),
        "sha256": digest(output_path.read_bytes()),
    }


def paired_tool_use(raw_path: Path, output_path: Path, revision: str) -> dict[str, object]:
    rows = []
    for source in read_jsonl(raw_path):
        rows.append({
            "id": f"tool-use-{source['variant_id']}",
            "track": "agentic_tool_use",
            "language": source.get("language", "ar"),
            "prompt": source["user_request"],
            "expected": source["expected"],
            "tags": ["agentic", "tool_use", source.get("variety", "")],
            "provenance": {
                "sourceId": "paired-msa-saudi-tool-use",
                "release": "heldout-v1.0.3",
                "sourceFile": (
                    "sources/missing-track-candidates/paired-msa-saudi-tool-use/"
                    "paired-msa-saudi-tool-use-v1.0.3/data/releases/heldout-v1.0.3/records.jsonl"
                ),
                "scenarioId": source["scenario_id"],
                "variantId": source["variant_id"],
                "sourceRevision": revision,
            },
            "review_status": "not_reviewed",
            "audit_status": "certified",
            "audit_issues": [],
        })
    write_jsonl(output_path, rows)
    return {
        "source_id": "paired-msa-saudi-tool-use",
        "rows": len(rows),
        "sha256": digest(output_path.read_bytes()),
    }


def islamic_faith_qa(raw_path: Path, output_path: Path, revision: str) -> dict[str, object]:
    rows = []
    for index, source in enumerate(read_jsonl(raw_path), 1):
        prompt = source.get("question") or source.get("question_ar") or source.get("text", "")
        if not prompt:
            continue
        rows.append({
            "id": f"islamicfaithqa-ar-{index:05d}",
            "track": "islamic_qa",
            "language": "ar",
            "prompt": prompt,
            "expected": {"answer": source.get("gold_answer") or source.get("answer", "")},
            "tags": ["islamic_qa", str(source.get("category_type", ""))],
            "provenance": {
                "sourceId": "QCRI/IslamicFaithQA",
                "sourceFile": (
                    "sources/missing-track-candidates/islamicfaithqa/arabic/"
                    "dataset_with_difficulty_clean_updated.jsonl"
                ),
                "sourceRow": index,
                "sourceRevision": revision,
            },
            "review_status": "not_reviewed",
        })
    write_jsonl(output_path, rows)
    return {
        "source_id": "QCRI/IslamicFaithQA",
        "rows": len(rows),
        "sha256": digest(output_path.read_bytes()),
    }


def arabic_function_calling(raw_path: Path, output_path: Path, revision: str) -> dict[str, object]:
    rows = []
    for index, source in enumerate(read_jsonl(raw_path), 1):
        query = str(source.get("query_ar") or "").strip()
        if not query:
            continue
        rows.append({
            "id": f"arabic-function-calling-{source['id']}",
            "track": "agentic",
            "language": "ar",
            "prompt": query,
            "expected": {
                "requiresFunction": bool(source.get("requires_function")),
                "functionName": source.get("function_name") or None,
                "arguments": json.loads(source.get("arguments") or "{}"),
            },
            "tags": [
                "arabic-function-calling", "arabic", "agentic",
                str(source.get("dialect") or ""),
            ],
            "provenance": {
                "sourceId": "arabic-function-calling",
                "sourceRevision": revision,
                "sourceFile": "sources/huggingface/arabic-function-calling/test.jsonl",
                "sourceRow": index,
                "domain": source.get("domain"),
                "dialect": source.get("dialect"),
            },
            "review_status": "not_reviewed",
        })
    write_jsonl(output_path, rows)
    return {
        "source_id": "arabic-function-calling",
        "rows": len(rows),
        "sha256": digest(output_path.read_bytes()),
    }


def arabic_ragb(raw_path: Path, output_path: Path, revision: str) -> dict[str, object]:
    rows = []
    for index, source in enumerate(read_jsonl(raw_path), 1):
        query = str(source.get("query") or "").strip()
        passage = str(source.get("passage_text") or "").strip()
        if not query or not passage:
            continue
        rows.append({
            "id": f"arabicragb-{source.get('id', index)}",
            "track": "rag",
            "language": "ar",
            "prompt": f"السياق:\n{passage}\n\nالسؤال:\n{query}",
            "expected": {"passageId": str(source.get("passage_id") or "")},
            "tags": ["arabicragb", "arabic", "rag", str(source.get("query_dialect") or "")],
            "provenance": {
                "sourceId": "arabicragb",
                "sourceRevision": revision,
                "sourceFile": "sources/huggingface/arabicragb/unified_test.jsonl",
                "sourceRow": index,
                "sourceUrl": source.get("source_url"),
                "sourceCategory": source.get("source_category"),
                "queryDialect": source.get("query_dialect"),
                "queryComplexity": source.get("query_complexity"),
            },
            "review_status": "not_reviewed",
        })
    write_jsonl(output_path, rows)
    return {
        "source_id": "arabicragb",
        "rows": len(rows),
        "sha256": digest(output_path.read_bytes()),
    }


def ara_truthful_qa(raw_path: Path, output_path: Path, revision: str) -> dict[str, object]:
    rows = []
    for index, source in enumerate(read_jsonl(raw_path), 1):
        question = str(source.get("input") or "").strip()
        label = str(source.get("label") or "").strip()
        if not question or not label:
            continue
        rows.append({
            "id": f"humain-aratruthfulqa-{index:05d}",
            "track": "truthfulness",
            "language": "ar",
            "prompt": question,
            "expected": {
                "answerKey": label,
                "options": source.get("options") or [],
                "answer": source.get("answer"),
            },
            "tags": ["humain-aratruthfulqa", "arabic", "truthfulness"],
            "provenance": {
                "sourceId": "humain-aratruthfulqa",
                "sourceRevision": revision,
                "sourceFile": "sources/huggingface/humain-aratruthfulqa/AraTruthfulQA_test.jsonl",
                "sourceRow": index,
                "sourceKey": source.get("iid"),
            },
            "review_status": "not_reviewed",
        })
    write_jsonl(output_path, rows)
    return {
        "source_id": "humain-aratruthfulqa",
        "rows": len(rows),
        "sha256": digest(output_path.read_bytes()),
    }


def ara_safe(raw_dir: Path, output_path: Path, revision: str) -> dict[str, object]:
    rows = []
    sources = (
        ("natural.jsonl", "arasafe-natural", "human_written", "User_Prompt", "human_written"),
        ("synthetic.jsonl", "arasafe-synthetic", "gpt4o_synthetic", "Prompt", "synthetic"),
    )
    for filename, prefix, origin, prompt_field, source_dir in sources:
        source_file = (
            "arasafe_natural_prompts.jsonl" if origin == "human_written"
            else "arasafe_synthetic_prompts.jsonl"
        )
        for index, source in enumerate(read_jsonl(raw_dir / filename), 1):
            prompt = str(source.get(prompt_field) or "").strip()
            label = str(source.get("Safety_Label") or "").strip()
            if not prompt or not label:
                continue
            rows.append({
                "id": f"{prefix}-{index:05d}",
                "track": "safety",
                "language": "ar",
                "prompt": prompt,
                "expected": {"safetyLabel": label},
                "tags": ["arasafe", "arabic", "safety", origin],
                "provenance": {
                    "sourceId": "arasafe",
                    "sourceRevision": revision,
                    "sourceFile": (
                        f"sources/github-snapshots/arasafe-benchmark/{source_dir}/"
                        f"{source_file}"
                    ),
                    "sourceRow": index,
                    "origin": origin,
                },
                "review_status": "not_reviewed",
            })
    write_jsonl(output_path, rows)
    return {"source_id": "arasafe", "rows": len(rows), "sha256": digest(output_path.read_bytes())}


def mena_values(raw_path: Path, output_path: Path, revision: str) -> dict[str, object]:
    import pyarrow.parquet as pq

    countries = (
        "Egypt", "Iran", "Iraq", "Jordan", "Lebanon", "Libya", "Morocco", "Turkey",
        "Tunisia", "Algeria", "Saudi Arabia", "Sudan", "Palestine", "Kuwait",
        "Mauritania", "Qatar",
    )
    rows = []
    for index, source in enumerate(pq.read_table(raw_path).to_pylist(), 1):
        question = str(source.get("Full Question") or "").strip()
        if not question:
            continue
        distributions = {
            country: source[country] for country in countries if source.get(country) is not None
        }
        rows.append({
            "id": f"mena-values-{index:04d}",
            "track": "alignment",
            "language": "en",
            "prompt": question,
            "expected": {
                "surveyDistributions": distributions,
                "min": source.get("Min"),
                "max": source.get("MAX"),
                "scale": source.get("Scale"),
            },
            "tags": [
                "mena-values", "alignment", "saudi", str(source.get("Category") or ""),
                str(source.get("Sub Category") or ""),
            ],
            "provenance": {
                "sourceId": "mena-values",
                "sourceRevision": revision,
                "sourceFile": "sources/huggingface/mena-values/transposed_output.parquet",
                "sourceRow": index,
                "source": source.get("Source"),
                "subQuestion": source.get("Sub Question"),
            },
            "review_status": "not_reviewed",
        })
    write_jsonl(output_path, rows)
    return {
        "source_id": "mena-values",
        "rows": len(rows),
        "sha256": digest(output_path.read_bytes()),
    }


def arbml_label_source(
    raw_path: Path, output_path: Path, revision: str, kind: str
) -> dict[str, object]:
    import pyarrow.parquet as pq

    settings = {
        "quran_hadith": ("arbml-quran-hadith-v1", "religious", "Verse1"),
        "saudiirony": ("arbml-saudi-irony-v1", "saudi", "Tweet"),
        "arabic_dialects_dataset": ("arbml-arabic-dialects-v1", "arabic", "Text"),
    }
    prefix, track, prompt_field = settings[kind]
    rows = []
    for index, source in enumerate(pq.read_table(raw_path).to_pylist(), 1):
        prompt = str(source.get(prompt_field) or "").strip()
        if not prompt:
            continue
        rows.append({
            "id": f"{prefix}-{index:05d}",
            "track": track,
            "language": "ar",
            "prompt": prompt,
            "expected": {key: value for key, value in source.items() if key in {"label", "Label"}},
            "tags": ["arbml", track],
            "provenance": {
                "sourceId": f"arbml-{kind}",
                "sourceRevision": revision,
                "sourceFile": f"sources/huggingface/arbml/{kind}/train-00000-of-00001.parquet",
                "sourceRow": index,
            },
            "review_status": "not_reviewed",
        })
    write_jsonl(output_path, rows)
    return {
        "source_id": f"arbml-{kind}", "rows": len(rows),
        "sha256": digest(output_path.read_bytes()),
    }


def quran_hadith(raw_path: Path, output_path: Path, revision: str) -> dict[str, object]:
    return arbml_label_source(raw_path, output_path, revision, "quran_hadith")


def saudi_irony(raw_path: Path, output_path: Path, revision: str) -> dict[str, object]:
    return arbml_label_source(raw_path, output_path, revision, "saudiirony")


def arabic_dialects(raw_path: Path, output_path: Path, revision: str) -> dict[str, object]:
    return arbml_label_source(raw_path, output_path, revision, "arabic_dialects_dataset")


def arabic_hate_speech(raw_path: Path, output_path: Path, revision: str) -> dict[str, object]:
    import pyarrow.parquet as pq

    rows = []
    for index, source in enumerate(pq.read_table(raw_path).to_pylist(), 1):
        prompt = str(source.get("tweet") or "").strip()
        if not prompt:
            continue
        rows.append({
            "id": f"arbml-hate-{index:05d}",
            "track": "safety",
            "language": "ar",
            "prompt": prompt,
            "expected": {
                "offensive": source.get("is_off"), "hate": source.get("is_hate"),
                "violence": source.get("is_vlg"), "violent": source.get("is_vio"),
            },
            "tags": ["arbml", "hate-speech", "safety"],
            "provenance": {
                "sourceId": "arbml-arabic-hate-speech", "sourceRevision": revision,
                "sourceFile": (
                    "sources/huggingface/arbml/arabic_hate_speech/"
                    "train-00000-of-00001.parquet"
                ),
                "sourceRow": index, "sourceKey": source.get("id"),
            },
            "review_status": "not_reviewed",
        })
    write_jsonl(output_path, rows)
    return {
        "source_id": "arbml-arabic-hate-speech", "rows": len(rows),
        "sha256": digest(output_path.read_bytes()),
    }


def dangerous_dataset(raw_path: Path, output_path: Path, revision: str) -> dict[str, object]:
    import pyarrow.parquet as pq

    rows = []
    for index, source in enumerate(pq.read_table(raw_path).to_pylist(), 1):
        prompt = str(source.get("Tweet") or "").strip()
        if not prompt:
            continue
        rows.append({
            "id": f"arbml-dangerous-{index:05d}",
            "track": "safety", "language": "ar", "prompt": prompt,
            "expected": {"dangerous": source.get("label")},
            "tags": ["arbml", "dangerous-prompts", "safety"],
            "provenance": {
                "sourceId": "arbml-dangerous-dataset", "sourceRevision": revision,
                "sourceFile": (
                    "sources/huggingface/arbml/dangerous_dataset/"
                    "train-00000-of-00001.parquet"
                ),
                "sourceRow": index,
            },
            "review_status": "not_reviewed",
        })
    write_jsonl(output_path, rows)
    return {
        "source_id": "arbml-dangerous-dataset", "rows": len(rows),
        "sha256": digest(output_path.read_bytes()),
    }


def arabic_reading_comprehension(
    raw_path: Path, output_path: Path, revision: str
) -> dict[str, object]:
    import pyarrow.parquet as pq

    rows = []
    for index, source in enumerate(pq.read_table(raw_path).to_pylist(), 1):
        question = str(source.get("question") or "").strip()
        answer = str(source.get("answer") or "").strip()
        passage = str(source.get("passage") or "").strip()
        if not question or not answer:
            continue
        rows.append({
            "id": f"arbml-rc-{index:05d}",
            "track": "document",
            "language": "ar",
            "prompt": f"السياق:\n{passage}\n\nالسؤال:\n{question}",
            "expected": {"answer": answer},
            "tags": ["arbml", "arabic-rc", "document", "rag"],
            "provenance": {
                "sourceId": "arbml-arabic-rc", "sourceRevision": revision,
                "sourceFile": (
                    "sources/huggingface/arbml/arabic_rc/"
                    "train-00000-of-00001-88a129334d052012.parquet"
                ),
                "sourceRow": index,
                "questionClass": source.get("question_class"),
                "questionSubclass": source.get("question_subclass"),
            },
            "review_status": "not_reviewed",
        })
    write_jsonl(output_path, rows)
    return {
        "source_id": "arbml-arabic-rc", "rows": len(rows),
        "sha256": digest(output_path.read_bytes()),
    }


def ara_pro(raw_path: Path, output_path: Path, revision: str) -> dict[str, object]:
    import pyarrow.parquet as pq

    rows = []
    for index, source in enumerate(pq.read_table(raw_path).to_pylist(), 1):
        question = str(source.get("question") or "").strip()
        answer = source.get("answer")
        options = [str(source.get(f"choice{item}") or "").strip() for item in range(1, 5)]
        if not question or answer is None:
            continue
        rows.append({
            "id": f"humain-arapro-{index:05d}",
            "track": "general",
            "language": "ar",
            "prompt": question,
            "expected": {"answerIndex": int(answer), "options": options},
            "tags": ["humain-arapro", "arabic", str(source.get("domain") or "")],
            "provenance": {
                "sourceId": "humain-arapro", "sourceRevision": revision,
                "sourceFile": "sources/huggingface/humain-arapro/data/test-00000-of-00001.parquet",
                "sourceRow": index,
                "sourceKey": source.get("id"),
                "domain": source.get("domain"),
                "subDomain": source.get("sub-domain"),
            },
            "review_status": "not_reviewed",
        })
    write_jsonl(output_path, rows)
    return {
        "source_id": "humain-arapro", "rows": len(rows),
        "sha256": digest(output_path.read_bytes()),
    }


def dialectal_mmlu(raw_path: Path, output_path: Path, revision: str) -> dict[str, object]:
    import pyarrow.parquet as pq

    rows = []
    for index, source in enumerate(pq.read_table(raw_path).to_pylist(), 1):
        choices = source.get("choices") or []
        choices = json.loads(choices) if isinstance(choices, str) else choices
        answer = source.get("answer")
        answer_key = str(answer if answer is not None else "").strip()
        dialect = str(source.get("dialect") or "")
        rows.append({
            "id": f"dialectal-arabic-mmlu-{index:05d}",
            "track": "saudi" if dialect.lower() == "saudi" else "arabic",
            "language": "ar",
            "prompt": str(source.get("question") or "").strip(),
            "expected": {"answerKey": answer_key, "options": [str(item) for item in choices]},
            "tags": ["dialectal-arabic-mmlu", "arabic", dialect],
            "provenance": {
                "sourceId": "dialectal-arabic-mmlu", "sourceRevision": revision,
                "sourceFile": (
                    "sources/huggingface/dialectal-arabic-mmlu/data/"
                    "test-00000-of-00001.parquet"
                ),
                "sourceRow": index,
                "qid": str(source.get("qid") or ""),
                "dialect": dialect,
                "domain": str(source.get("domain") or ""),
            },
            "review_status": "not_reviewed",
        })
    write_jsonl(output_path, rows)
    return {
        "source_id": "dialectal-arabic-mmlu", "rows": len(rows),
        "sha256": digest(output_path.read_bytes()),
    }


def reproduce_source(
    manifest_path: Path, output_dir: Path, reference_path: Path | None = None
) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    adapters = {
        "arabic-agent-eval-v1": arabic_agent_eval,
        "paired-tool-use-v1": paired_tool_use,
        "islamic-faith-qa-v1": islamic_faith_qa,
        "arabic-function-calling-v1": arabic_function_calling,
        "arabic-ragb-v1": arabic_ragb,
        "ara-truthful-qa-v1": ara_truthful_qa,
        "ara-safe-v1": ara_safe,
        "mena-values-v1": mena_values,
        "arbml-quran-hadith-v1": quran_hadith,
        "arbml-saudi-irony-v1": saudi_irony,
        "arbml-arabic-rc-v1": arabic_reading_comprehension,
        "humain-ara-pro-v1": ara_pro,
        "dialectal-mmlu-v1": dialectal_mmlu,
        "arbml-dialects-v1": arabic_dialects,
        "arbml-hate-v1": arabic_hate_speech,
        "arbml-dangerous-v1": dangerous_dataset,
    }
    if manifest["adapter"] not in adapters:
        raise PipelineError("unknown source adapter")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise PipelineError("output directory must be empty")
    output_dir.mkdir(parents=True, exist_ok=True)
    if "raw_files" in manifest:
        raw_path = output_dir / "raw"
        raw_path.mkdir()
        for file in manifest["raw_files"]:
            url = file["url"]
            if f"/{manifest['revision']}/" not in url:
                raise PipelineError("raw URL is not pinned to manifest revision")
            raw = _fetch(url)
            if digest(raw) != file["sha256"]:
                raise PipelineError("upstream source SHA-256 mismatch")
            (raw_path / file["name"]).write_bytes(raw)
    else:
        parquet_adapters = {
            "mena-values-v1", "arbml-quran-hadith-v1", "arbml-saudi-irony-v1",
            "arbml-arabic-rc-v1", "humain-ara-pro-v1",
            "dialectal-mmlu-v1",
            "arbml-dialects-v1", "arbml-hate-v1", "arbml-dangerous-v1",
        }
        suffix = ".parquet" if manifest["adapter"] in parquet_adapters else ".jsonl"
        raw_path = output_dir / f"upstream{suffix}"
        url = manifest["raw_url"]
        if f"/{manifest['revision']}/" not in url:
            raise PipelineError("raw URL is not pinned to manifest revision")
        raw = _fetch(url)
        if digest(raw) != manifest["raw_sha256"]:
            raise PipelineError("upstream source SHA-256 mismatch")
        raw_path.write_bytes(raw)
    output_path = output_dir / "cases.jsonl"
    result = adapters[manifest["adapter"]](raw_path, output_path, manifest["revision"])
    if result["rows"] != manifest["expected_rows"]:
        raise PipelineError("adapter row count mismatch")
    if result["sha256"] != manifest["expected_sha256"]:
        raise PipelineError("adapter output SHA-256 mismatch")
    if not manifest.get("reference_sha256"):
        raise PipelineError("pinned published reference SHA-256 is required")
    if reference_path is None and manifest.get("reference_url"):
        reference_bytes = _fetch(manifest["reference_url"])
        if digest(reference_bytes) != manifest["reference_sha256"]:
            raise PipelineError("published reference SHA-256 mismatch")
        reference_path = output_dir / "published-reference.jsonl"
        reference_path.write_bytes(reference_bytes)
    if reference_path is None:
        raise PipelineError("published reference URL or local file is required")
    if digest(reference_path.read_bytes()) != manifest["reference_sha256"]:
        raise PipelineError("published reference SHA-256 mismatch")
    reference = [
        row for row in read_jsonl(reference_path)
        if row.get("provenance", {}).get("sourceId") == result["source_id"]
    ]
    certified_count = len(reference)
    if manifest.get("reference_quarantine_url"):
        quarantine_bytes = _fetch(manifest["reference_quarantine_url"])
        if digest(quarantine_bytes) != manifest["reference_quarantine_sha256"]:
            raise PipelineError("published quarantine SHA-256 mismatch")
        quarantine_path = output_dir / "published-quarantine.jsonl"
        quarantine_path.write_bytes(quarantine_bytes)
        quarantine_rows = [
            row for row in read_jsonl(quarantine_path)
            if row.get("provenance", {}).get("sourceId") == result["source_id"]
        ]
        reference.extend(quarantine_rows)
        result["quarantine_rows_matched"] = len(quarantine_rows)
    generated = read_jsonl(output_path)
    generated_by_id = {row["id"]: row for row in generated}
    selection_mode = manifest.get("selection_mode")
    if selection_mode == "derived_review_copy":
        for row in reference:
            is_copy = row["id"].endswith("-review-copy")
            base_id = row["id"].removesuffix("-review-copy") if is_copy else row["id"]
            candidate = generated_by_id.get(base_id)
            if candidate is None:
                raise PipelineError("published review copy lacks upstream candidate")
            derived = dict(candidate)
            if is_copy:
                derived["id"] = row["id"]
                derived["derived_from_candidate_id"] = base_id
                derived["provenance"] = {
                    **candidate["provenance"], "derived_from_candidate": True,
                }
            if derived != {
                key: value for key, value in row.items() if not key.startswith("audit_")
            }:
                raise PipelineError("generated review copy differs from published source row")
    elif selection_mode == "published_subset":
        if any(
            _with_correction(
                generated_by_id.get(row["id"]),
                manifest.get("case_corrections", {}).get(row["id"]),
            ) != {key: value for key, value in row.items() if not key.startswith("audit_")}
            for row in reference
        ):
            raise PipelineError("generated cases differ from published source rows")
    elif {row["id"]: row for row in reference} != generated_by_id:
        raise PipelineError("generated cases differ from published source rows")
    if certified_count != manifest.get("expected_published_rows", manifest["expected_rows"]):
        raise PipelineError("published source row count mismatch")
    if result.get("quarantine_rows_matched", 0) != manifest.get("expected_quarantine_rows", 0):
        raise PipelineError("published quarantine row count mismatch")
    result["published_rows_matched"] = len(reference)
    write_json(output_dir / "report.json", result)
    return result


def _with_correction(row: dict | None, correction: dict | None) -> dict | None:
    if row is None or correction is None:
        return row
    updated = {**row, "expected": dict(row["expected"])}
    updated["prompt"] = correction["prompt"]
    updated["expected"]["options"] = correction["expected_options"]
    return updated
