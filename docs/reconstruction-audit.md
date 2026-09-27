# Public reconstruction dependency audit

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

R1 is closed for those verification scopes. R2's private-input dependency is closed for the selected 31 cases through the new runner; the older standalone adapter still supports private historical replay. R3 has content evidence but the original file is still missing. R4–R9 remain explicit reconstruction/rights gates. No complete end-to-end byte reconstruction claim is made.

## Unresolved dependencies and closure evidence

| ID | Dependency | Evidence needed to close |
|---|---|---|
| R1 | End-to-end clean anonymous reconstruction execution | Run scripts/audit_public_reconstruction.py from a clean checkout; account for every source and inspect the per-source comparison scope. Resolve every failure. |
| R2 | Private historical 64-row input in the old adapter | Replace local-raw dependency with the pinned public original 31-case subset plus published source-row mapping; compare all non-audit fields. The original authoring process is undocumented. |
| R3 | Missing original authorized-items extract and original snapshots | For historical byte identity recover original bytes plus hashes. For content reconstruction explicitly use the pinned fresh public snapshot and preserve the distinction; compare all expected fields. |
| R4 | Published target rows are still used to select and validate upstream candidates | Commit a versioned selection ID/split manifest or deterministic selection algorithm with provenance; build without reading target case content, then use the target only for comparison. |
| R5 | Full byte-for-byte replay starts from a private 178517-row pre-audit export | Replace that export with public input assembly or define a new public-source successor. Document exclusions/replacements if the historical artifact cannot be rebuilt. |
| R6 | Public-source full release assembly, metadata and Parquet reproduction are not implemented | Assemble source outputs, apply published selection/repair/audit/metadata-removal rules, create JSONL/Parquet/schema/manifests, verify pinned checksums or explicitly version a content-equivalent serialization. |
| R7 | Public rights evidence is incomplete and historical ledger labels are not permission documents | Record per-source scope and attribution obligations, license or permission reference, and publication authority. Nine web sources now have explicit owner-confirmed redistribution permission; do not silently extend it to unrelated sources. |
| R8 | Live pages and Jina-rendered text are mutable; raw snapshots are local-only | Publish rights-cleared immutable collection inputs or retain the pinned fresh question snapshot as the explicit reconstruction boundary. Require a content-diff report on future recollection. |

| R9 | Legacy document, RAG and agent fixtures are outside row-content checks | Verify all public fixture hashes and required paths, then demonstrate equivalent harness setup. Public fixture availability alone does not prove executable task equivalence. |

Machine-readable inventory: [reconstruction-dependencies.json](../releases/reconstruction-dependencies.json).

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
