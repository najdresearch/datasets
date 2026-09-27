---
pretty_name: Najd Benchmark
license: other
language: [ar, en]
size_categories: [1K<n<10K]
tags: [arabic, saudi-arabia, benchmark, evaluation]
task_categories: [text-generation]
configs:
- config_name: default
  data_files:
  - split: test
    path: datasets/najd-benchmark/2026.09.27/viewer.parquet
---

# Najd Benchmark

**6,089 evaluation cases for Arabic and Saudi AI, from 39 sources.**

Use the collection to compare models on Arabic language, Saudi knowledge, reasoning, retrieval, tool use, safety and other tasks. All cases are available together in `default/test`.

## Load the data

```python
from datasets import load_dataset

data = load_dataset("najdresearch/najd-benchmark", split="test")
```

- [Cases — JSONL](datasets/najd-benchmark/2026.09.27/cases.jsonl)
- [Cases — Parquet](datasets/najd-benchmark/2026.09.27/viewer.parquet)
- [Manifest](datasets/najd-benchmark/2026.09.27/manifest.json), [schema](datasets/najd-benchmark/2026.09.27/case.schema.json) and [checksums](datasets/najd-benchmark/2026.09.27/checksums.json)

JSONL retains native answer/provenance objects. Parquet encodes heterogeneous objects as JSON strings for the viewer. Individual `audit_issues` notes retain known limitations without labeling cases by audit status.

## Reproduce and contribute

Collection, normalization and reconstruction code lives in [najdresearch/datasets](https://github.com/najdresearch/datasets).

```sh
git clone https://github.com/najdresearch/datasets.git
cd datasets
uv sync --locked --extra dev --extra parquet --extra excel
uv run python scripts/reconstruct_public_release.py --output build/historical
uv run python scripts/build_unified_release.py build/historical/release build/current
```

The public reconstruction supplies every case from pinned upstream inputs, the [31 legacy cases and fixtures](https://huggingface.co/datasets/najdresearch/najd-legacy-31), and [333 freshly collected Arabic questions](https://huggingface.co/datasets/najdresearch/arabic-riddles). Those subsets are already included in the 6,089 count. Original legacy authoring history and the original web extract remain unavailable; the recovered release specification records historical metadata explicitly.

See [reconstruction details](https://github.com/najdresearch/datasets/blob/main/docs/public-release-builder.md) and [how to contribute](https://github.com/najdresearch/datasets/blob/main/CONTRIBUTING.md).

## Sources

Credit belongs to the original creators. Each case retains source provenance; the [source register](datasets/najd-benchmark/2026.09.27/sources.json) contains evidence and pinned references.

| Source | Cases |
|---|---:|
| [absher](https://huggingface.co/datasets/Renad10/Absher-Benchmark) | 243 |
| [alghafa-native](https://huggingface.co/datasets/OALL/AlGhafa-Arabic-LLM-Benchmark-Native) | 150 |
| [almrsal-general-contest](https://www.almrsal.com/post/1556481) | 11 |
| [almrsal-riddles](https://www.almrsal.com/post/1369176) | 99 |
| [arabic-agent-eval](https://github.com/Moshe-ship/arabic-agent-eval) | 51 |
| [arabic-exams](https://huggingface.co/datasets/OALL/Arabic_EXAMS) | 24 |
| [arabic-function-calling](https://huggingface.co/datasets/HeshamHaroon/Arabic_Function_Calling) | 499 |
| [arabic-safety-evaluation](https://github.com/mbzuai-nlp/Arabic_safety_evaluation) | 35 |
| [arabicmmlu](https://huggingface.co/datasets/MBZUAI/ArabicMMLU) | 104 |
| [arabicragb](https://huggingface.co/datasets/HeshamHaroon/ArabicRAGB) | 499 |
| [arasafe](https://github.com/qcri/AraSafe-benchmark) | 300 |
| [aratrust](https://huggingface.co/datasets/EmanAmeen/AraTrust) | 15 |
| [arbml-arabic-hate-speech](https://huggingface.co/datasets/arbml/Arabic_Hate_Speech) | 94 |
| [arbml-arabic-rc](https://huggingface.co/datasets/arbml/Arabic_RC) | 496 |
| [arbml-arabic_dialects_dataset](https://huggingface.co/datasets/arbml/Arabic_Dialects_Dataset) | 76 |
| [arbml-cidar-eval-100](https://huggingface.co/datasets/arbml/CIDAR-EVAL-100) | 7 |
| [arbml-cidar-mcq-100](https://huggingface.co/datasets/arbml/CIDAR-MCQ-100) | 7 |
| [arbml-dangerous-dataset](https://huggingface.co/datasets/arbml/Dangerous_Dataset) | 56 |
| [arbml-quran_hadith](https://huggingface.co/datasets/arbml/Quran_Hadith) | 500 |
| [arbml-saudiirony](https://huggingface.co/datasets/arbml/SaudiIrony) | 257 |
| [commonsense-validation](https://huggingface.co/datasets/arbml/Commonsense_Validation) | 48 |
| [dialectal-arabic-mmlu](https://huggingface.co/datasets/MBZUAI/Dialectal-Arabic-MMLU) | 165 |
| [humain-araifeval](https://huggingface.co/datasets/humain-ai/AraIFEval) | 3 |
| [humain-aramath](https://huggingface.co/datasets/humain-ai/AraMath) | 50 |
| [humain-arapro](https://huggingface.co/datasets/humain-ai/AraPro) | 363 |
| [humain-aratruthfulqa](https://huggingface.co/datasets/humain-ai/AraTruthfulQA) | 500 |
| [inception-arabic-ifeval](https://huggingface.co/datasets/inception42/Arabic-IFEval) | 2 |
| [mawdoo3-animals](https://mawdoo3.com/%D8%A3%D9%84%D8%BA%D8%A7%D8%B2_%D8%B9%D9%86_%D8%A7%D9%84%D8%AD%D9%8A%D9%88%D8%A7%D9%86%D8%A7%D8%AA_%D9%85%D8%B9_%D8%A7%D9%84%D8%AD%D9%84) | 19 |
| [mawdoo3-riddles](https://mawdoo3.com/%D8%A3%D9%84%D8%BA%D8%A7%D8%B2_%D8%B0%D9%83%D8%A7%D8%A1_%D9%85%D8%B9_%D8%A7%D9%84%D8%AD%D9%84%D9%88%D9%84) | 18 |
| [mawdoo3-science](https://mawdoo3.com/%D8%A3%D9%84%D8%BA%D8%A7%D8%B2_%D8%B9%D9%86_%D8%A7%D9%84%D8%B9%D9%84%D9%85_%D9%85%D8%B9_%D8%A7%D9%84%D8%AD%D9%84) | 15 |
| [mena-values](https://huggingface.co/datasets/llm-lab/MENA_VALUES_Benchmark) | 500 |
| [najd-benchmark-v1](https://huggingface.co/datasets/najdresearch/najd-legacy-31) | 31 |
| [paired-msa-saudi-tool-use](https://github.com/aalsaedi/paired-msa-saudi-tool-use-dataset) | 150 |
| [pico-saudi-v0.01](https://github.com/mznmel/Pico-Saudi-LLMs-Benchmark) | 55 |
| [QCRI/IslamicFaithQA](https://huggingface.co/datasets/QCRI/IslamicFaithQA) | 476 |
| [qusama-riddles](https://qusama1.yoo7.com/t304-100-%D9%84%D8%BA%D8%B2-%D9%85%D8%B9-%D8%A7%D9%84%D8%AD%D9%84-%D9%87%D9%88%D9%88%D9%88%D9%88%D9%88%D9%88%D9%88%D9%88%D9%88%D8%B9) | 96 |
| [sayidaty-children-riddles](https://www.sayidaty.net/%D8%B3%D9%8A%D8%AF%D8%AA%D9%8A-%D9%88%D8%B7%D9%81%D9%84%D9%83/%D8%A3%D8%B7%D9%81%D8%A7%D9%84-%D9%88%D9%85%D8%B1%D8%A7%D9%87%D9%82%D9%88%D9%86/1814996-%D8%A3%D9%84%D8%BA%D8%A7%D8%B2-%D9%84%D9%84%D8%A3%D8%B7%D9%81%D8%A7%D9%84-%D9%88%D8%A7%D9%84%D8%AD%D9%84) | 1 |
| [twinkl-arabic-riddles](https://www.twinkl.com/blog/arabic-riddles-with-answers-more-than-50) | 50 |
| [twinkl-islamic-questions](https://www.twinkl.com/blog/180-islamic-questions-for-competition) | 24 |

## Use and limitations

This dataset supports research and evaluation. Cases may contain ambiguous questions, annotation errors or source artifacts. Scores depend on the case selection, prompts, model settings and grading method. It is not a production safety certification.

Upstream terms apply; `license: other` does not relicense the data. Public license declarations are recorded for 17 sources, owner attestations for nine website sources, and owner authorization for the legacy subset. Permission evidence remains outstanding for 12 sources covering 2,759 cases. Attribution and research purpose do not replace permission or authorize commercial EaaS use. See the [rights evidence register](https://github.com/najdresearch/datasets/blob/main/docs/source-attribution.md).

## Version

Version **2026.09.27** combines the existing case files into one collection and removes `audit_status`. Case IDs, prompts, answers, provenance and individual issue notes are unchanged. Earlier snapshots remain accessible through Hugging Face revision history. Reports using the earlier default configuration evaluated a smaller case set; record the revision and selected case IDs when comparing results.

## Citation

```bibtex
@dataset{najd_research_najd_benchmark_2026,
  author = {{Najd Research}},
  title = {Najd Benchmark},
  year = {2026},
  version = {2026.09.27},
  publisher = {Hugging Face},
  url = {https://huggingface.co/datasets/najdresearch/najd-benchmark}
}
```

Questions and corrections: [Community](https://huggingface.co/datasets/najdresearch/najd-benchmark/discussions).
