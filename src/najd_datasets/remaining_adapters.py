"""Original-source adapters for the remaining historical release sources."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

from .pipeline import digest, read_jsonl, write_jsonl


def _finish(source_id: str, output_path: Path, rows: list[dict]) -> dict[str, object]:
    write_jsonl(output_path, rows)
    return {"source_id": source_id, "rows": len(rows), "sha256": digest(output_path.read_bytes())}


def ara_math(raw_path: Path, output_path: Path, revision: str) -> dict[str, object]:
    rows = []
    for index, source in enumerate(read_jsonl(raw_path), 1):
        question = str(source.get("question") or "").strip()
        label = str(source.get("label") or "").strip()
        if not question or not label:
            continue
        rows.append({
            "id": f"humain-aramath-{index:05d}",
            "track": "general", "language": "ar", "prompt": question,
            "expected": {
                "answerKey": label,
                "options": source.get("options") or [],
                "numericAnswer": source.get("answer"),
            },
            "tags": ["humain-aramath", "arabic", "math"],
            "provenance": {
                "sourceId": "humain-aramath", "sourceRevision": revision,
                "sourceFile": "sources/huggingface/humain-aramath/test.jsonl",
                "sourceRow": index, "sourceKey": source.get("iid"),
            },
            "review_status": "not_reviewed",
        })
    return _finish("humain-aramath", output_path, rows)


def humain_araifeval(raw_path: Path, output_path: Path, revision: str) -> dict[str, object]:
    rows = []
    for index, source in enumerate(read_jsonl(raw_path), 1):
        rows.append({
            "id": f"humain-araifeval-{source['IF_id']}",
            "track": "arabic", "language": "ar", "prompt": source["prompt"],
            "expected": {"instructionIds": source.get("instruction_list", [])},
            "tags": ["humain-araifeval", "arabic", "instruction_following"],
            "provenance": {
                "sourceId": "humain-araifeval", "sourceRevision": revision,
                "sourceFile": "sources/huggingface/humain-araifeval/Arabic_IF_Eval_Flat.jsonl",
                "sourceRow": index, "originalSampleId": source.get("original_sample_id"),
            },
            "review_status": "not_reviewed",
        })
    return _finish("humain-araifeval", output_path, rows)


def inception_ifeval(raw_path: Path, output_path: Path, revision: str) -> dict[str, object]:
    rows = []
    for index, source in enumerate(read_jsonl(raw_path), 1):
        rows.append({
            "id": f"inception-arabic-ifeval-{source['key']}",
            "track": "arabic", "language": "ar", "prompt": source["prompt"],
            "expected": {
                "instructionIds": source.get("instruction_id_list", []),
                "kwargs": source.get("kwargs"),
            },
            "tags": ["inception-arabic-ifeval", "arabic", "instruction_following"],
            "provenance": {
                "sourceId": "inception-arabic-ifeval", "sourceRevision": revision,
                "sourceFile": "sources/huggingface/inception-arabic-ifeval/ar_IFEval.jsonl",
                "sourceRow": index, "key": source.get("key"),
            },
            "review_status": "not_reviewed",
        })
    return _finish("inception-arabic-ifeval", output_path, rows)


def commonsense_validation(raw_path: Path, output_path: Path, revision: str) -> dict[str, object]:
    import pyarrow.parquet as pq

    rows = []
    for index, source in enumerate(pq.read_table(raw_path).to_pylist(), 1):
        rows.append({
            "id": f"commonsense-validation-{index:05d}",
            "track": "general", "language": "ar",
            "prompt": (
                f"الجملة الأولى: {source.get('first_sentence', '')}\n"
                f"الجملة الثانية: {source.get('second_sentence', '')}\n"
                "هل الجملتان متوافقتان؟"
            ),
            "expected": {"answerKey": str(source["label"])},
            "tags": ["commonsense-validation", "arabic", "general"],
            "provenance": {
                "sourceId": "commonsense-validation", "sourceRevision": revision,
                "sourceFile": (
                    "sources/huggingface/commonsense-validation/data/"
                    "validation-00000-of-00001.parquet"
                ),
                "sourceRow": index, "sourceKey": str(source.get("id") or index),
            },
            "review_status": "not_reviewed",
        })
    return _finish("commonsense-validation", output_path, rows)


def arabic_exams(raw_path: Path, output_path: Path, revision: str) -> dict[str, object]:
    import pyarrow.parquet as pq

    rows = []
    for index, source in enumerate(pq.read_table(raw_path).to_pylist(), 1):
        question = str(source.get("question") or "").strip()
        if not question:
            continue
        options = [
            str(source.get(key) or "").strip()
            for key in "ABCD" if str(source.get(key) or "").strip()
        ]
        rows.append({
            "id": f"arabic-exams-{index:05d}",
            "track": "general", "language": "ar", "prompt": question,
            "expected": {"answerKey": str(source.get("answer") or "").strip(), "options": options},
            "tags": ["arabic-exams", "general"],
            "provenance": {
                "sourceId": "arabic-exams", "sourceRevision": revision,
                "sourceFile": "sources/huggingface/arabic-exams/data/test-00000-of-00001.parquet",
                "sourceRow": index, "sourceKey": str(source.get("id") or index),
            },
            "review_status": "not_reviewed",
        })
    return _finish("arabic-exams", output_path, rows)


def ara_trust(raw_path: Path, output_path: Path, revision: str) -> dict[str, object]:
    import pyarrow.parquet as pq

    rows = []
    for index, source in enumerate(pq.read_table(raw_path).to_pylist(), 1):
        options = [source.get(key, "").strip() for key in "ABC"]
        category = str(source.get("Category") or "unknown").strip()
        subcategory = str(source.get("Subcategory") or "unknown").strip()
        rows.append({
            "id": f"aratrust-{index:04d}",
            "track": "safety", "language": "ar", "prompt": source["Question"].strip(),
            "expected": {"answerKey": source["Answer"].strip(), "options": options},
            "tags": ["aratrust", "safety", "alignment", category, subcategory],
            "provenance": {
                "sourceId": "aratrust", "sourceRevision": revision,
                "sourceFile": "sources/huggingface/aratrust/data/test-00000-of-00001.parquet",
                "sourceRow": index, "category": category, "subcategory": subcategory,
            },
            "review_status": "not_reviewed",
        })
    return _finish("aratrust", output_path, rows)


def cidar_eval(raw_path: Path, output_path: Path, revision: str) -> dict[str, object]:
    import pyarrow.parquet as pq

    rows = []
    for index, source in enumerate(pq.read_table(raw_path).to_pylist(), 1):
        prompt = str(source.get("Sentence") or "").strip()
        if not prompt:
            continue
        rows.append({
            "id": f"arbml-cidar-eval-{index:03d}",
            "track": "general", "language": "ar", "prompt": prompt,
            "expected": {"topic": source.get("Topic")},
            "tags": ["arbml", "cidar", "classification"],
            "provenance": {
                "sourceId": "arbml-cidar-eval-100", "sourceRevision": revision,
                "sourceFile": (
                    "sources/huggingface/arbml/cidar_eval_100/data/"
                    "train-00000-of-00001.parquet"
                ),
                "sourceRow": index,
            },
            "review_status": "not_reviewed",
        })
    return _finish("arbml-cidar-eval-100", output_path, rows)


def cidar_mcq(raw_path: Path, output_path: Path, revision: str) -> dict[str, object]:
    import pyarrow.parquet as pq

    rows = []
    for index, source in enumerate(pq.read_table(raw_path).to_pylist(), 1):
        question = str(source.get("Question") or "").strip()
        answer = str(source.get("answer") or "").strip()
        if not question or not answer:
            continue
        options = {key: str(source.get(key) or "").strip() for key in "ABCD"}
        rows.append({
            "id": f"arbml-cidar-mcq-{index:03d}",
            "track": "general", "language": "ar",
            "prompt": (
                question + "\n"
                + "\n".join(f"{key}. {value}" for key, value in options.items())
            ),
            "expected": {"answer": answer, "answer_text": options.get(answer, "")},
            "tags": ["arbml", "cidar", "mcq"],
            "provenance": {
                "sourceId": "arbml-cidar-mcq-100", "sourceRevision": revision,
                "sourceFile": (
                    "sources/huggingface/arbml/cidar_mcq_100/data/"
                    "test-00000-of-00001.parquet"
                ),
                "sourceRow": index,
            },
            "review_status": "not_reviewed",
        })
    return _finish("arbml-cidar-mcq-100", output_path, rows)


def arabic_mmlu(raw_dir: Path, output_path: Path, revision: str) -> dict[str, object]:
    rows = []
    for path in sorted(raw_dir.rglob("test.csv")):
        if path.parent.name == "All":
            continue
        relative = f"sources/huggingface/arabicmmlu/{path.relative_to(raw_dir)}"
        with path.open(encoding="utf-8-sig", newline="") as handle:
            for index, source in enumerate(csv.DictReader(handle), 1):
                question = source["Question"].strip()
                context = source.get("Context", "").strip()
                prompt = (f"السياق:\n{context}\n\n" if context else "") + question
                options = [
                    source.get(f"Option {item}", "").strip()
                    for item in range(1, 6)
                    if source.get(f"Option {item}", "").strip()
                ]
                suffix = hashlib.sha1((relative + str(index)).encode()).hexdigest()[:8]
                rows.append({
                    "id": f"arabicmmlu-{source['ID']}-{suffix}",
                    "track": "arabic", "language": "ar", "prompt": prompt,
                    "expected": {"answerKey": source["Answer Key"].strip(), "options": options},
                    "tags": [
                        "arabicmmlu", "arabic", "general",
                        source.get("Subject", "").strip(), source.get("Level", "").strip(),
                    ],
                    "provenance": {
                        "sourceId": "arabicmmlu", "sourceRevision": revision,
                        "sourceFile": relative, "sourceRow": index + 1,
                        "sourceIdField": source["ID"],
                        "subject": source.get("Subject", ""),
                        "level": source.get("Level", ""),
                        "country": source.get("Country", ""),
                        "group": source.get("Group", ""),
                    },
                    "review_status": "not_reviewed",
                })
    return _finish("arabicmmlu", output_path, rows)


def absher(raw_dir: Path, output_path: Path, revision: str) -> dict[str, object]:
    rows = []
    tasks = (
        "Meaning", "True_False", "Fill_in_Blank", "Contextual_Usage",
        "Cultural_Interpretation", "Location_Recognition",
    )
    for group in ("Words", "Phrases", "Proverbs"):
        for task in tasks:
            path = raw_dir / f"{group}_{task}_questions.csv"
            if not path.exists():
                continue
            source_sha = digest(path.read_bytes())
            with path.open(encoding="utf-8", newline="") as handle:
                records = list(csv.reader(handle))
            if not records or len(records[0]) != 5:
                raise ValueError(f"unexpected Absher columns: {path.name}")
            nonempty = [record for record in records[1:] if any(record)]
            for index, record in enumerate(nonempty, 1):
                term, meaning, dialect, prompt, answer = record
                group_slug = group.lower()
                task_slug = task.lower()
                normalized = (
                    "words" if group_slug == "phrases" and len(term.strip().split()) == 1
                    else group_slug
                )
                surface = "word" if len(term.strip().split()) == 1 else "phrase"
                rows.append({
                    "id": f"absher-{group_slug}-{task_slug}-{index:05d}",
                    "track": "saudi", "language": "ar", "prompt": prompt,
                    "expected": {"answer": answer.strip() or None},
                    "tags": ["absher", "saudi", surface, task_slug, dialect or "unknown"],
                    "provenance": {
                        "sourceId": "absher", "sourceRevision": revision,
                        "sourceFile": f"sources/absher/raw/{path.name}",
                        "sourceRow": index + 1,
                        "term": term, "meaning": meaning, "dialect": dialect,
                        "sourceSha256": source_sha,
                        "sourceQuality": (
                            "present" if answer.strip() else "missing_correct_answer"
                        ),
                        "sourceCategory": group_slug,
                        "normalizedCategory": normalized,
                        "normalization": "single_token_is_word_v1",
                        "surfaceCategory": surface,
                        "classificationRule": "one_token_word_else_phrase_v1",
                    },
                    "review_status": "not_reviewed",
                })
    return _finish("absher", output_path, rows)


# The historical importer hashed an absolute checkout path into each case ID.
# These prefixes are the recorded IDs of the nine original tasks; keeping the
# mapping explicit makes reproduction independent of the user's directory.
ALGHAFA_TASK_PREFIXES = {
    "mcq_exams_test_ar": "55172796",
    "meta_ar_dialects": "4812e3d5",
    "meta_ar_msa": "649d61e8",
    "multiple_choice_facts_truefalse_balanced_task": "09fb0a15",
    "multiple_choice_grounded_statement_soqal_task": "574f7040",
    "multiple_choice_grounded_statement_xglue_mlqa_task": "a0cbcf23",
    "multiple_choice_rating_sentiment_no_neutral_task": "75acce91",
    "multiple_choice_rating_sentiment_task": "c6353c7a",
    "multiple_choice_sentiment_task": "b9936379",
}


def alghafa_native(raw_dir: Path, output_path: Path, revision: str) -> dict[str, object]:
    import pyarrow.parquet as pq

    rows = []
    for path in sorted(raw_dir.rglob("test-00000-of-00001.parquet")):
        task = path.parent.name
        prefix = ALGHAFA_TASK_PREFIXES[task]
        source_file = (
            f"sources/huggingface/alghafa-native/{task}/test-00000-of-00001.parquet"
        )
        for index, source in enumerate(pq.read_table(path).to_pylist(), 1):
            question = str(source.get("query") or "").strip()
            options = [
                str(source.get(key) or "").strip()
                for key in ("sol1", "sol2", "sol3", "sol4", "sol5")
                if str(source.get(key) or "").strip()
            ]
            if not question:
                continue
            rows.append({
                "id": f"alghafa-{prefix}-{index:05d}",
                "track": "arabic", "language": "ar", "prompt": question,
                "expected": {
                    "answerKey": str(source.get("label") or "").strip(),
                    "options": options,
                },
                "tags": ["alghafa", "arabic", task],
                "provenance": {
                    "sourceId": "alghafa-native", "sourceRevision": revision,
                    "sourceFile": source_file, "sourceRow": index, "task": task,
                },
                "review_status": "not_reviewed",
            })
    return _finish("alghafa-native", output_path, rows)


def pico_saudi(raw_path: Path, output_path: Path, revision: str) -> dict[str, object]:
    rows = []
    with raw_path.open(encoding="utf-8-sig", newline="") as handle:
        source_rows = list(csv.DictReader(handle))
    for index, source in enumerate(source_rows, 1):
        category = source["question_category"]
        tags = ["public", "pico", "saudi", "human_review", f"pico_category:{category}"]
        dialect = None
        dimensions = ["correctness", "arabic_quality", "saudi_cultural_accuracy"]
        if category == "localDialects":
            tags.extend(["dialect", "slang"])
            dialect = "saudi"
            dimensions.append("dialect_match")
        if category in {"reasoning", "coding"}:
            tags.append("capability")
        rows.append({
            "id": f"pico-{source['question_id']}",
            "category": category, "track": category, "language": "ar",
            "prompt": source["question"],
            "system_prompt": "You must provide all your responses exclusively in Arabic",
            "tags": tags, "dialect": dialect,
            "expected": {"must_not_refuse": True},
            "judge_dimensions": dimensions,
            "provenance": {
                "sourceId": "pico-saudi-v0.01", "sourceRevision": revision,
                "sourceFile": "datasets/pico-saudi-v0.01/cases.jsonl",
                "sourceRow": index, "repair": "legacy_contract_v1",
            },
            "review_status": "not_reviewed",
        })
    return _finish("pico-saudi-v0.01", output_path, rows)


def arabic_safety_evaluation(
    raw_dir: Path, output_path: Path, revision: str
) -> dict[str, object]:
    import pandas as pd

    rows = []
    files = (
        ("Regional sensitive dataset.xlsx", "arabic-safety-egypt-v1"),
        ("Regional_specific_dataset_for_arab_countries.xlsx",
         "arabic-safety-arab-countries-v1"),
    )
    for filename, prefix in files:
        for zero_index, source in pd.read_excel(raw_dir / filename).iterrows():
            question = str(source.get("Questions in Arabic") or "").strip()
            if not question:
                continue
            question_type = str(source.get("Q-Type") or "")
            source_id = source.get("Id")
            source_key = str(source_id if pd.notna(source_id) else zero_index)
            rows.append({
                "id": f"{prefix}-{zero_index + 1:05d}",
                "track": "safety", "language": "ar", "prompt": question,
                "expected": {"taxonomy": {
                    "level1": str(source.get("Taxnomy| Level 1") or ""),
                    "level2": str(source.get("Taxnomy| Level 2") or ""),
                    "level3": str(source.get("Taxnomy| Level 3") or ""),
                    "questionType": question_type,
                }},
                "tags": [
                    "arabic-safety-evaluation", "arabic", "safety", "alignment",
                    question_type,
                ],
                "provenance": {
                    "sourceId": "arabic-safety-evaluation", "sourceRevision": revision,
                    "sourceFile": (
                        "sources/github-snapshots/arabic-safety-evaluation/data/" + filename
                    ),
                    "sourceRow": int(zero_index) + 2, "sourceKey": source_key,
                },
                "review_status": "not_reviewed",
            })
    return _finish("arabic-safety-evaluation", output_path, rows)


def najd_v1_copy(raw_path: Path, output_path: Path, revision: str) -> dict[str, object]:
    rows = []
    for index, source in enumerate(read_jsonl(raw_path), 1):
        row = dict(source)
        row["provenance"] = {
            "sourceId": "najd-benchmark-v1", "sourceRevision": revision,
            "sourceFile": "datasets/najd-benchmark-v1/cases.jsonl",
            "sourceRow": index, "repair": "legacy_contract_v1",
        }
        row["review_status"] = "not_reviewed"
        rows.append(row)
    return _finish("najd-benchmark-v1", output_path, rows)
