# Rebuilding the final 774 published rows

These rows were always present in the pinned public snapshot. Each source now has a collector that starts from a pinned upstream file or a hash-checked private archive file, builds candidate rows, and compares every selected row with the published release. The comparison ignores only release audit fields.

| Source | Format | Candidates | Published | Recorded transformation |
|---|---|---:|---:|---|
| [Absher](../sources/absher.json) | 18 CSV files | 18,564 | 243 | Term category normalization and six case repairs; four rows remain quarantined. |
| [AlGhafa Native](../sources/alghafa-native.json) | 9 Parquet files | 22,932 | 150 | Explicit task-to-ID prefixes replace the old machine-specific path hash. |
| [ArabicMMLU](../sources/arabicmmlu.json) | 40 subject CSV files | 14,455 | 104 | Subject row IDs, empty-tag cleanup, and recorded candidate markers. The aggregate `All` split is excluded. |
| [Pico Saudi](../sources/pico-saudi-v0.01.json) | CSV | 55 | 55 | Rebuild the historical suite contract from the original questions. The official and archived CSV differ in bytes but parse to the same 55 rows. |
| [AraMath](../sources/humain-aramath.json) | JSONL | 605 | 50 | Candidate marker on selected rows. |
| [Commonsense Validation](../sources/commonsense-validation.json) | Parquet | 1,000 | 48 | Match the published two-sentence question and binary answer-key contract. |
| [Arabic Safety Evaluation](../sources/arabic-safety-evaluation.json) | 2 Excel files | 3,095 | 35 | Keep source taxonomy labels and row positions; omit model response columns. |
| [Najd v1 internal copy](../sources/najd-benchmark-v1.json) | private archived JSONL | 64 | 31 | Preserve original row positions and the recorded legacy provenance; all 31 remain quarantined. |
| [Arabic EXAMS](../sources/arabic-exams.json) | Parquet | 537 | 24 | Multiple-choice field mapping. |
| [AraTrust](../sources/aratrust.json) | Parquet | 522 | 15 | Candidate marker on selected rows. |
| [CIDAR Eval](../sources/arbml-cidar-eval-100.json) | Parquet | 100 | 7 | Topic-label mapping; one selected row lacks the historical candidate marker. |
| [CIDAR MCQ](../sources/arbml-cidar-mcq-100.json) | Parquet | 100 | 7 | Question, choices, and answer mapping. |
| [AraIFEval](../sources/humain-araifeval.json) | JSONL | 536 | 3 | Instruction-ID mapping and candidate marker. |
| [Arabic IFEval](../sources/inception-arabic-ifeval.json) | JSONL | 404 | 2 | Instruction-ID and keyword-argument mapping with candidate marker. |

## Run the adapters

Install the optional readers once:

```bash
uv sync --extra dev --extra parquet --extra excel
```

For each public source above, run `uv run --extra parquet --extra excel najd-datasets reproduce-source sources/<name>.json --output build/<name>`. The command fetches the pinned input, checks its SHA-256, checks the generated candidate count and hash, downloads the pinned public reference, and compares the selected rows field by field. Use an empty output directory for each run.

The internal copy requires the preserved private archive. Place its `datasets/m3-saudi-v1/cases.jsonl` file at `private/historical-inputs/m3-saudi-v1/cases.jsonl` after cloning; `private/` is Git-ignored and the file is not committed:

```bash
uv run najd-datasets reproduce-source sources/najd-benchmark-v1.json \
  --local-raw private/historical-inputs/m3-saudi-v1/cases.jsonl \
  --output build/najd-benchmark-v1
```

Its manifest pins the archive Git commit, original path, and raw SHA-256. A wrong local file fails before comparison. This archived source is a 64-row predecessor under a different name; all 31 selected internal-copy rows match its content and original row positions. The archive input is distinct from the nine-source authorized extract described in [private extract dependencies](private-extract-dependencies.md).

## Boundaries

The 774 rows are now reproducible through the adapters, but 333 other quarantined rows still lack their original historical extract. Their published content matches a fresh extraction, as documented separately. Source matching checks release provenance and transformation fidelity; it does not change the historical audit status.
