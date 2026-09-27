---
pretty_name: Najd Benchmark
license: other
language:
- ar
- en
size_categories:
- 1K<n<10K
tags:
- arabic
- saudi-arabia
- benchmark
- evaluation
- najd-benchmark
configs:
- config_name: default
  data_files:
  - split: test
    path: datasets/najd-benchmark/2026.09.14/viewer.parquet
- config_name: quarantine
  data_files:
  - split: test
    path: datasets/najd-benchmark/2026.09.14/quarantine.parquet
task_categories:
- text-generation
---

# Najd Benchmark

Najd Benchmark is a **6,089-case Arabic-first evaluation collection** from Najd Research for assessing language models and agent configurations in Saudi and broader Arabic contexts. The historical release contains **5,717 structurally certified cases** in `default/test` and **372 cases** in `quarantine/test`. These historical split assignments are preserved. All 6,089 published case records can now be reconstructed from public inputs; this does not establish semantic correctness or resolve every redistribution permission.

## Historical audit status (2026-09-14)

> Every element in `default/test` passed exhaustive structural validation, and every source represented in that split links to an exact, verified upstream artifact.

This certification is structural and provenance-focused. It **does not claim factual or semantic correctness**. `audit_status` and `audit_issues` report this audit's result.

- Dataset: `najd-benchmark`
- Version: `2026.09.14`
- Certified split: `default/test` (5,717 cases; 29 sources)
- Quarantine split: `quarantine/test` (372 cases)
- Certified JSONL: `datasets/najd-benchmark/2026.09.14/cases.jsonl`
- Quarantine JSONL: `datasets/najd-benchmark/2026.09.14/quarantine.jsonl`
- Machine-readable audit: [`audit.json`](datasets/najd-benchmark/2026.09.14/audit.json)
- Repair log: [`repairs.json`](datasets/najd-benchmark/2026.09.14/repairs.json)
- Case schema: [`case.schema.json`](datasets/najd-benchmark/2026.09.14/case.schema.json)

## What was checked

Every case was checked for unique identity, required fields, non-empty prompts and tags, expected-answer contract shape, answer/index validity where applicable, provenance fields, Unicode replacement characters, and split audit metadata. Every source retained in `default/test` was resolved to an immutable Hugging Face commit or Git commit/release. Records with unresolved exact source links or missing answers were moved to `quarantine/test` rather than inferred.

Deterministic repairs restored 61 zero-valued answer labels from pinned upstream rows, removed 29 empty tags, renamed 997 misleading `derived_copy_of` fields to `derived_from_candidate_id`, and normalized 1,140 per-record provenance revisions to exact commits. Four Arabic RC prompts contain replacement characters in the pinned upstream artifact itself, so they were quarantined instead of guessed. Each changed record has before/after hashes and evidence in `repairs.json`.

## Certified composition

| Category | Cases | Category | Cases |
|---|---:|---|---:|
| agentic | 499 | agentic_tool_use | 201 |
| alignment | 500 | arabic | 500 |
| coding | 5 | culture | 5 |
| document | 492 | footballSport | 8 |
| general | 499 | history | 6 |
| islamic_qa | 476 | literature | 5 |
| localDialects | 6 | media | 6 |
| music&art | 6 | rag | 499 |
| reasoning | 8 | religious | 500 |
| safety | 500 | saudi | 496 |
| truthfulness | 500 |  |  |

## Sources and attribution

The table accounts for all 6,089 original records. Its split counts and link-status labels describe the **2026-09-14 audit**, not current permission approval. Fresh public source snapshots now support reconstruction of the 333 web questions, and the 31 legacy cases and fixtures are public. Original historical extract bytes and legacy authoring history remain unavailable. The historical [`sources.json`](datasets/najd-benchmark/2026.09.14/sources.json) is preserved; the [current evidence register](https://github.com/najdresearch/datasets/blob/main/releases/source-rights-evidence.json) records subsequent findings.

| Source | Certified | Quarantine | Revision | Link status |
|---|---:|---:|---|---|
| [absher](https://huggingface.co/datasets/Renad10/Absher-Benchmark/tree/554f7457e9f91290f204ac56ab82e707f302944e) | 239 | 4 | `554f7457e9f91290f204ac56ab82e707f302944e` | Verified |
| [alghafa-native](https://huggingface.co/datasets/OALL/AlGhafa-Arabic-LLM-Benchmark-Native/tree/a31ebd34ca311d7e0cfc6ad7f458b3435af280f5) | 150 | 0 | `a31ebd34ca311d7e0cfc6ad7f458b3435af280f5` | Verified |
| [almrsal-general-contest](https://www.almrsal.com/post/1556481) | 0 | 11 | `Not recorded` | Quarantined |
| [almrsal-riddles](https://www.almrsal.com/post/1369176) | 0 | 99 | `Not recorded` | Quarantined |
| [arabic-agent-eval](https://github.com/Moshe-ship/arabic-agent-eval/tree/9f075af0ae5b70580e650b26ddf1d26cf871b24f) | 51 | 0 | `9f075af0ae5b70580e650b26ddf1d26cf871b24f` | Verified |
| [arabic-exams](https://huggingface.co/datasets/OALL/Arabic_EXAMS/tree/bc7a29346dbcaa16a8cd883b1f3e681ab2b7ff2a) | 24 | 0 | `bc7a29346dbcaa16a8cd883b1f3e681ab2b7ff2a` | Verified |
| [arabic-function-calling](https://huggingface.co/datasets/HeshamHaroon/Arabic_Function_Calling/tree/ec4d3302f6b2d91c5fbe81864c2ee498b8cd3ade) | 499 | 0 | `ec4d3302f6b2d91c5fbe81864c2ee498b8cd3ade` | Verified |
| [arabic-safety-evaluation](https://github.com/mbzuai-nlp/Arabic_safety_evaluation/tree/aae91341a5ffcef61c9cb797ca259fb98ff45352) | 35 | 0 | `aae91341a5ffcef61c9cb797ca259fb98ff45352` | Verified |
| [arabicmmlu](https://huggingface.co/datasets/MBZUAI/ArabicMMLU/tree/7aa530e2893ac420352b3f5c1a1310c010e9758b) | 104 | 0 | `7aa530e2893ac420352b3f5c1a1310c010e9758b` | Verified |
| [arabicragb](https://huggingface.co/datasets/HeshamHaroon/ArabicRAGB/tree/9427b6c04c6bb8c85e45cb32071cf6a7978280d2) | 499 | 0 | `9427b6c04c6bb8c85e45cb32071cf6a7978280d2` | Verified |
| [arasafe](https://github.com/qcri/AraSafe-benchmark/tree/b5e8a6f3d9f83a57ab8b4bea58b4d68a44ae6331) | 300 | 0 | `b5e8a6f3d9f83a57ab8b4bea58b4d68a44ae6331` | Verified |
| [aratrust](https://huggingface.co/datasets/EmanAmeen/AraTrust/tree/54f05f0e8a980c2937f488316fbc28392b41a52b) | 15 | 0 | `54f05f0e8a980c2937f488316fbc28392b41a52b` | Verified |
| [arbml-arabic-hate-speech](https://huggingface.co/datasets/arbml/Arabic_Hate_Speech/tree/06797a1aa4ab67ad290179096499fcfbea5d3396) | 94 | 0 | `06797a1aa4ab67ad290179096499fcfbea5d3396` | Verified |
| [arbml-arabic-rc](https://huggingface.co/datasets/arbml/Arabic_RC/tree/5e87525e9805b3f944e4bb89455e966fc1befd43) | 492 | 4 | `5e87525e9805b3f944e4bb89455e966fc1befd43` | Verified |
| [arbml-arabic_dialects_dataset](https://huggingface.co/datasets/arbml/Arabic_Dialects_Dataset/tree/cad29588d485a685c01dc9d4f2a4d51be146285a) | 76 | 0 | `cad29588d485a685c01dc9d4f2a4d51be146285a` | Verified |
| [arbml-cidar-eval-100](https://huggingface.co/datasets/arbml/CIDAR-EVAL-100/tree/f7997c45b73a26c1b54a697c9c8bb6a78c9e8b84) | 7 | 0 | `f7997c45b73a26c1b54a697c9c8bb6a78c9e8b84` | Verified |
| [arbml-cidar-mcq-100](https://huggingface.co/datasets/arbml/CIDAR-MCQ-100/tree/a64885fb2b20a7ec066209681cc31a751f4e1425) | 7 | 0 | `a64885fb2b20a7ec066209681cc31a751f4e1425` | Verified |
| [arbml-dangerous-dataset](https://huggingface.co/datasets/arbml/Dangerous_Dataset/tree/3d1bed077281daea67963195892c748d36fff5a8) | 56 | 0 | `3d1bed077281daea67963195892c748d36fff5a8` | Verified |
| [arbml-quran_hadith](https://huggingface.co/datasets/arbml/Quran_Hadith/tree/db75746e2bb76dc1969869d552c9809c60c14358) | 500 | 0 | `db75746e2bb76dc1969869d552c9809c60c14358` | Verified |
| [arbml-saudiirony](https://huggingface.co/datasets/arbml/SaudiIrony/tree/008b2ebf5a8a19194cf91048d8e3453b934c2b52) | 257 | 0 | `008b2ebf5a8a19194cf91048d8e3453b934c2b52` | Verified |
| [commonsense-validation](https://huggingface.co/datasets/arbml/Commonsense_Validation/tree/85da6793fc34e58c885b80a9d070122afb249083) | 48 | 0 | `85da6793fc34e58c885b80a9d070122afb249083` | Verified |
| [dialectal-arabic-mmlu](https://huggingface.co/datasets/MBZUAI/Dialectal-Arabic-MMLU/tree/f3c801b43861aa47bdbaca5f884598e9fabc8e67) | 165 | 0 | `f3c801b43861aa47bdbaca5f884598e9fabc8e67` | Verified |
| [humain-araifeval](https://huggingface.co/datasets/humain-ai/AraIFEval/tree/49d32ae083091fc1fbfa22c300c209ebe4740372) | 3 | 0 | `49d32ae083091fc1fbfa22c300c209ebe4740372` | Verified |
| [humain-aramath](https://huggingface.co/datasets/humain-ai/AraMath/tree/b79e79b1b993d153613d1ce2357a1177f2cdcfa1) | 50 | 0 | `b79e79b1b993d153613d1ce2357a1177f2cdcfa1` | Verified |
| [humain-arapro](https://huggingface.co/datasets/humain-ai/AraPro/tree/e606730ed50b663d7655ea2e02793238f5166422) | 363 | 0 | `e606730ed50b663d7655ea2e02793238f5166422` | Verified |
| [humain-aratruthfulqa](https://huggingface.co/datasets/humain-ai/AraTruthfulQA/tree/162744fbf0590606415eb0924f2b5bd680486e3a) | 500 | 0 | `162744fbf0590606415eb0924f2b5bd680486e3a` | Verified |
| [inception-arabic-ifeval](https://huggingface.co/datasets/inception42/Arabic-IFEval/tree/48f209003f5c90055248d11b8f0e4ffd4162cb87) | 2 | 0 | `48f209003f5c90055248d11b8f0e4ffd4162cb87` | Verified |
| [mawdoo3-animals](https://mawdoo3.com/%D8%A3%D9%84%D8%BA%D8%A7%D8%B2_%D8%B9%D9%86_%D8%A7%D9%84%D8%AD%D9%8A%D9%88%D8%A7%D9%86%D8%A7%D8%AA_%D9%85%D8%B9_%D8%A7%D9%84%D8%AD%D9%84) | 0 | 19 | `Not recorded` | Quarantined |
| [mawdoo3-riddles](https://mawdoo3.com/%D8%A3%D9%84%D8%BA%D8%A7%D8%B2_%D8%B0%D9%83%D8%A7%D8%A1_%D9%85%D8%B9_%D8%A7%D9%84%D8%AD%D9%84%D9%88%D9%84) | 0 | 18 | `Not recorded` | Quarantined |
| [mawdoo3-science](https://mawdoo3.com/%D8%A3%D9%84%D8%BA%D8%A7%D8%B2_%D8%B9%D9%86_%D8%A7%D9%84%D8%B9%D9%84%D9%85_%D9%85%D8%B9_%D8%A7%D9%84%D8%AD%D9%84) | 0 | 15 | `Not recorded` | Quarantined |
| [mena-values](https://huggingface.co/datasets/llm-lab/MENA_VALUES_Benchmark/tree/43bdb1b77d3ed2cbbd957a0d3a976d986fdfebcc) | 500 | 0 | `43bdb1b77d3ed2cbbd957a0d3a976d986fdfebcc` | Verified |
| [najd-benchmark-v1](https://huggingface.co/datasets/najdresearch/najd-legacy-31) | 0 | 31 | `1.0.0` | Quarantined |
| [paired-msa-saudi-tool-use](https://github.com/aalsaedi/paired-msa-saudi-tool-use-dataset/tree/ba360380c1ca1dacb48b12c20c130385ef20650a) | 150 | 0 | `ba360380c1ca1dacb48b12c20c130385ef20650a` | Verified |
| [pico-saudi-v0.01](https://github.com/mznmel/Pico-Saudi-LLMs-Benchmark/tree/6117a74aa757ddee27cd72c20aa428cf7e8e6b1b) | 55 | 0 | `6117a74aa757ddee27cd72c20aa428cf7e8e6b1b` | Verified |
| [QCRI/IslamicFaithQA](https://huggingface.co/datasets/QCRI/IslamicFaithQA/tree/a525f5d47a04f9290e6aecaf34668c23a4431d63) | 476 | 0 | `a525f5d47a04f9290e6aecaf34668c23a4431d63` | Verified |
| [qusama-riddles](https://qusama1.yoo7.com/t304-100-%D9%84%D8%BA%D8%B2-%D9%85%D8%B9-%D8%A7%D9%84%D8%AD%D9%84-%D9%87%D9%88%D9%88%D9%88%D9%88%D9%88%D9%88%D9%88%D9%88%D9%88%D8%B9) | 0 | 96 | `Not recorded` | Quarantined |
| [sayidaty-children-riddles](https://www.sayidaty.net/%D8%B3%D9%8A%D8%AF%D8%AA%D9%8A-%D9%88%D8%B7%D9%81%D9%84%D9%83/%D8%A3%D8%B7%D9%81%D8%A7%D9%84-%D9%88%D9%85%D8%B1%D8%A7%D9%87%D9%82%D9%88%D9%86/1814996-%D8%A3%D9%84%D8%BA%D8%A7%D8%B2-%D9%84%D9%84%D8%A3%D8%B7%D9%81%D8%A7%D9%84-%D9%88%D8%A7%D9%84%D8%AD%D9%84) | 0 | 1 | `Not recorded` | Quarantined |
| [twinkl-arabic-riddles](https://www.twinkl.com/blog/arabic-riddles-with-answers-more-than-50) | 0 | 50 | `Not recorded` | Quarantined |
| [twinkl-islamic-questions](https://www.twinkl.com/blog/180-islamic-questions-for-competition) | 0 | 24 | `Not recorded` | Quarantined |

### Current rights evidence (2026-09-27)

This collection is used for research into Arabic and Saudi AI evaluation. Source attribution and research purpose do not themselves establish redistribution permission. `license: other` does not relicense third-party material.

| Evidence | Sources | Cases |
|---|---:|---:|
| Public upstream license declarations located | 17 | 2,966 |
| Owner-attested permission for the nine web sources | 9 | 333 |
| Owner-authorized legacy publication | 1 | 31 |
| Applicable license or permission evidence still needed | 12 | 2,759 |

Historical “permission on file” labels and approval fields are historical assertions, not independently verified permission records. The 12 unresolved sources are AlGhafa, Arabic EXAMS, Arabic Safety Evaluation, AraSafe, ARBML Arabic Hate Speech, Arabic RC, Arabic Dialects Dataset, Dangerous Dataset, Quran/Hadith, Dialectal Arabic MMLU, AraPro and AraTruthfulQA. The historical dataset is preserved while permission records are sought.

See [source attribution and pinned license evidence](https://github.com/najdresearch/datasets/blob/main/docs/source-attribution.md). Upstream conditions, including noncommercial and share-alike terms, continue to apply. Successful reconstruction does not approve commercial Evaluation-as-a-Service use.

## Dataset Viewer

Choose `default` to inspect certified cases or `quarantine` to inspect isolated records. The Viewer uses deterministic Parquet projections. Heterogeneous `expected`, `provenance`, and `answer_recovery_evidence` objects are serialized as lossless JSON text; canonical JSONL retains native objects.

## Intended use and limitations

Use this dataset for model evaluation, audit, error analysis, and reproducible comparisons. It is not training data, a production safety standard, or a definitive ranking of model quality. Individual cases have not completed exhaustive semantic review and may still contain annotation errors, ambiguity, cultural assumptions, unsafe subject matter, or source-specific artifacts. Scores also depend on prompting, runtime configuration, grading method, and evaluation date.

## Reproducibility

The [datasets repository](https://github.com/najdresearch/datasets) contains the collection, normalization, reconstruction and contribution documentation.

```sh
git clone https://github.com/najdresearch/datasets.git
cd datasets
uv sync --locked --extra dev --extra parquet --extra excel
uv run python scripts/reconstruct_public_release.py --output build/public-release
uv run python scripts/verify_public_release.py build/public-release
```

The build requires public network access but no credentials or private files. It does not download the target case files; the separate verifier downloads them only after reconstruction.

| Output | Verification |
|---|---|
| Both JSONL case files — 6,089 rows | Exact published bytes |
| Both Parquet exports | Equal values, row order and schema; serialization bytes may differ |
| Seven historical JSON documents | Preserved with exact checksums, not newly performed audits |
| Eleven fixture files | Hash-verified and installed into six fixture-dependent case workspaces |

The reconstruction uses 5,725 upstream-derived records, the [31 public legacy cases](https://huggingface.co/datasets/najdresearch/najd-legacy-31), and the [333 freshly collected Arabic questions](https://huggingface.co/datasets/najdresearch/arabic-riddles). The latter two overlap with this dataset; their counts are not additional cases. Fresh questions supply Q/A content while an explicit recovered release specification preserves historical metadata. This does not recover the missing original extract or original authoring process.

See the [build instructions and exact reconstruction scope](https://github.com/najdresearch/datasets/blob/main/docs/public-release-builder.md) and [contribution guide](https://github.com/najdresearch/datasets/blob/main/CONTRIBUTING.md).

Verify release artifacts against [`checksums.json`](datasets/najd-benchmark/2026.09.14/checksums.json). The verified data revision is `43674ef228c1461d6fd34e20c20f51efcbdce56d`; the later documentation-only revision leaves those payloads unchanged. Evaluation reports should cite the dataset revision, version, case-file hash, selected config(s), prompting and scoring settings.

## Citation

```bibtex
@dataset{najd_research_najd_benchmark_2026,
  author    = {{Najd Research}},
  title     = {Najd Benchmark},
  year      = {2026},
  version   = {2026.09.14},
  publisher = {Hugging Face},
  url       = {https://huggingface.co/datasets/najdresearch/najd-benchmark}
}
```

## Contact

Questions and corrections: [Najd Benchmark Community](https://huggingface.co/datasets/najdresearch/najd-benchmark/discussions).

## Metadata revision

Review annotations are omitted from current data. This metadata-only revision does not change questions, answers, IDs, splits, or scoring. Earlier commit snapshots remain available for historical reproducibility. Removing annotations does not record a completed review.

## Documentation update — 2026-09-27

Updated reconstruction instructions, exact source attribution and rights-evidence status. No case records, scores, split assignments, schemas or release payloads were changed.
