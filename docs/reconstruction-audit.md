# Public reconstruction dependency audit

> Update: the [public release builder](public-release-builder.md) now reconstructs all 6,089 case records without private inputs or target case downloads. Earlier dependency descriptions below document the historical path. Missing original extract/authoring evidence and unverified redistribution permissions remain distinct from reproducible case content.


This audit explains what can be rebuilt from public inputs and exactly what still blocks a complete reconstruction. Publishing an input, matching its content, and recreating its original bytes are different claims.

## Run the evidence check

```sh
uv sync --locked --extra dev --extra parquet --extra excel
uv run python scripts/audit_public_reconstruction.py --output build/public-audit
```

The runner uses anonymous HTTP and a new output directory. It never reads `private/`, an archived checkout, local Drive, or credentials. It runs the 29 public upstream adapters, reconstructs the 31-case public legacy subset, and compares the 333 public fresh question/answer pairs. Existing adapter selection still depends on the published reference; this is explicitly not an independent full release builder.

## Recorded execution result

The [committed evidence report](../releases/public-reconstruction-evidence.json) records a clean-checkout run with **39 of 39 sources accounted for and 6,089 of 6,089 rows passing their stated comparison**.

| Rows | Verified scope | What this does not prove |
|---|---|---|
| 5,725 | All 29 public upstream adapters passed raw/output hash and selected-row checks | Independent selection or full release metadata assembly |
| 31 | Public original selected objects plus row mapping reproduce all non-audit fields | Original case authoring/generation process |
| 333 | Pinned fresh public snapshot matches every historical question and answer | Original extract bytes, all historical provenance fields, or raw-page replay |

## Current closure status

The [public release builder](public-release-builder.md) supersedes the partial checks above. It rebuilds both case files byte for byte and exports equivalent Parquet content. See [the dependency ledger](../releases/reconstruction-dependencies.json) for the exact closure scope of each item.

| Dependency | Current result |
|---|---|
| R1–R2 | Anonymous public build and public legacy subset integrated |
| R3 | All 333 complete published rows reconstructed from fresh Q/A and preserved historical metadata; original extract still missing |
| R4–R5 | Committed selection specification and direct assembly remove target-case selection and private intermediate export dependencies |
| R6 | JSONL rebuilt, Parquet generated, historical JSON documents preserved with checksums |
| R7 | Attribution and research purpose documented; remaining permission records not verified |
| R8 | Pinned public question snapshot is the explicit boundary; original HTML replay is not claimed |
| R9 | All fixture files and six installed case workspaces verified; model execution is outside this data build |

## Every source and its rights record

The table preserves the historical source ledger’s claims. `permission-on-file` is a recorded assertion, not proof that a permission document is publicly available. The owner separately confirmed redistribution of the nine web sources on 2026-09-27. Their public dataset card attributes each source. No additional review-status field or semantic-review claim is introduced.

| Source | Rows | Public reconstruction boundary | License recorded | Rights basis recorded |
|---|---:|---|---|---|
| absher | 243 | Pinned external raw input and adapter | cc-by-4.0 | permission-on-file |
| alghafa-native | 150 | Pinned external raw input and adapter | not-declared | permission-on-file |
| almrsal-general-contest | 11 | [Fresh public questions](https://huggingface.co/datasets/najdresearch/arabic-riddles); original extract unavailable | not-declared | permission-on-file |
| almrsal-riddles | 99 | [Fresh public questions](https://huggingface.co/datasets/najdresearch/arabic-riddles); original extract unavailable | not-declared | permission-on-file |
| arabic-agent-eval | 51 | Pinned external raw input and adapter | cc-by-4.0 | upstream-license |
| arabic-exams | 24 | Pinned external raw input and adapter | not-declared | permission-on-file |
| arabic-function-calling | 499 | Pinned external raw input and adapter | apache-2.0 | upstream-license |
| arabic-safety-evaluation | 35 | Pinned external raw input and adapter | not-declared | permission-on-file |
| arabicmmlu | 104 | Pinned external raw input and adapter | cc-by-nc-4.0 | upstream-license |
| arabicragb | 499 | Pinned external raw input and adapter | cc-by-sa-4.0 | upstream-license |
| arasafe | 300 | Pinned external raw input and adapter | not-declared | permission-on-file |
| aratrust | 15 | Pinned external raw input and adapter | mit | upstream-license |
| arbml-arabic-hate-speech | 94 | Pinned external raw input and adapter | not-declared | permission-on-file |
| arbml-arabic-rc | 496 | Pinned external raw input and adapter | not-declared | permission-on-file |
| arbml-arabic_dialects_dataset | 76 | Pinned external raw input and adapter | not-declared | permission-on-file |
| arbml-cidar-eval-100 | 7 | Pinned external raw input and adapter | apache-2.0 | upstream-license |
| arbml-cidar-mcq-100 | 7 | Pinned external raw input and adapter | apache-2.0 | upstream-license |
| arbml-dangerous-dataset | 56 | Pinned external raw input and adapter | not-declared | permission-on-file |
| arbml-quran_hadith | 500 | Pinned external raw input and adapter | not-declared | permission-on-file |
| arbml-saudiirony | 257 | Pinned external raw input and adapter | not-declared | permission-on-file |
| commonsense-validation | 48 | Pinned external raw input and adapter | not-declared | permission-on-file |
| dialectal-arabic-mmlu | 165 | Pinned external raw input and adapter | not-declared | permission-on-file |
| humain-araifeval | 3 | Pinned external raw input and adapter | apache-2.0 | upstream-license |
| humain-aramath | 50 | Pinned external raw input and adapter | apache-2.0 | upstream-license |
| humain-arapro | 363 | Pinned external raw input and adapter | not-declared | permission-on-file |
| humain-aratruthfulqa | 500 | Pinned external raw input and adapter | not-declared | permission-on-file |
| inception-arabic-ifeval | 2 | Pinned external raw input and adapter | cc-by-nc-4.0 | upstream-license |
| mawdoo3-animals | 19 | [Fresh public questions](https://huggingface.co/datasets/najdresearch/arabic-riddles); original extract unavailable | not-declared | permission-on-file |
| mawdoo3-riddles | 18 | [Fresh public questions](https://huggingface.co/datasets/najdresearch/arabic-riddles); original extract unavailable | not-declared | permission-on-file |
| mawdoo3-science | 15 | [Fresh public questions](https://huggingface.co/datasets/najdresearch/arabic-riddles); original extract unavailable | not-declared | permission-on-file |
| mena-values | 500 | Pinned external raw input and adapter | cc-by-4.0 | upstream-license |
| najd-benchmark-v1 | 31 | [Public original selected cases](https://huggingface.co/datasets/najdresearch/najd-legacy-31); authoring history unavailable | other | permission-on-file |
| paired-msa-saudi-tool-use | 150 | Pinned external raw input and adapter | cc-by-4.0 | permission-on-file |
| pico-saudi-v0.01 | 55 | Pinned external raw input and adapter | mit | permission-on-file |
| QCRI/IslamicFaithQA | 476 | Pinned external raw input and adapter | apache-2.0 | upstream-license |
| qusama-riddles | 96 | [Fresh public questions](https://huggingface.co/datasets/najdresearch/arabic-riddles); original extract unavailable | not-declared | permission-on-file |
| sayidaty-children-riddles | 1 | [Fresh public questions](https://huggingface.co/datasets/najdresearch/arabic-riddles); original extract unavailable | not-declared | permission-on-file |
| twinkl-arabic-riddles | 50 | [Fresh public questions](https://huggingface.co/datasets/najdresearch/arabic-riddles); original extract unavailable | not-declared | permission-on-file |
| twinkl-islamic-questions | 24 | [Fresh public questions](https://huggingface.co/datasets/najdresearch/arabic-riddles); original extract unavailable | not-declared | permission-on-file |

## Completion and stop rules

Step 1 is complete when all 39 sources are enumerated, the public execution report records successes/failures, and each unresolved dependency has a concrete closure criterion. This does not mark the full reconstruction project complete. Steps 2 and 3 must not erase these gaps or promote partial checks to a full reproduction claim.

- Fail on duplicate IDs, source-count gaps, checksum drift, changed answers, missing rows or unexpected extra selected rows.
- Never substitute a target published case as its own original input.
- Keep current metadata-free revisions and original historical artifact revisions distinct.
- A fresh snapshot can establish content agreement; it cannot establish the identity of a missing historical file.
- If a historical dependency cannot be recovered, publish a new successor with explicit changes rather than mislabel it as the old artifact.

## References

- [Current revision ledger](../releases/metadata-migration-2026.09.27.json)
- [Historical source ledger](../releases/2026.09.14/sources.json)
- [Public reconstruction gates](public-reconstruction.md)
- [Standalone source publications](standalone-publications.md)
- [Historical replay](reproduction.md)
- [Fresh collector manifest](../sources/arabic-riddles-pages.json)
