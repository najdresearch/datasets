# System One dataset v1 — candidate and public draft

## Public release

Published 5,184 cases in 11 packs at https://huggingface.co/datasets/najdresearch/system-one/tree/84bf0a30ced090e2b552beafa5f0f3c9a3665c0c . Original Najd cases are CC BY 4.0; third-party licenses remain attached. Independent review is pending. Fast Decisions (1,700 cases) remains local pending review of 114 contact-pattern flags. No private evaluation or employer data is included.

`releases/system-one-huggingface.json` pins the public revision. `releases/system-one-public-clearance.json` records the allowlist and rights basis. `system_one_publish` stages a hash-locked public draft and stable JSON-string viewer fields without overwriting the frozen candidate. Sharing permission and evaluation-claim eligibility are separate.

The next experiment uses the public natural-development pack (216 rows) on one remote machine, CPU then CUDA, with per-register and per-task scoring. The rest of this document describes the larger local candidate, which must not be confused with the public subset.


The runnable dataset is complete for the first remote evaluation. It combines 6,884 cases in 12 separately scored packs. This is a provisionally accepted research candidate, not an independently certified or publicly published benchmark.

| Component | Cases | Interpretation |
|---|---:|---|
| Controlled Saudi/government/enterprise policies | 2,400 | 800 scenario families, three language variants, 80 policy specifications |
| Natural-language original development drafts | 216 | 72 families, three language variants |
| Public references and diagnostics | 4,268 | Eight packs; language coverage varies by source |

## Build and verify

From this repository with the pinned inputs already cached:

```sh
PYTHONPATH=src .venv/bin/python -m najd_datasets.system_one_release \
  --output build/system-one-v1-rebuild --include-references
```

Use a new output path. Inputs are pinned in `fixtures/system-one-v1/input-lock.json`; a changed byte blocks the full build. `tasks/system-one-saudi-v0.2/download-lock.json` records exact URLs, revisions and hashes for Fast Decisions, MASSIVE and AISA. Existing source manifests and the source-inspection record pin other inputs. Raw source files and generated cases remain in ignored build storage. For a fresh checkout, restore the packaged candidate for evaluation or reconstruct the caches from these pinned sources and the existing `reproduce-source` commands. The build does not load models or implicitly download data.

Benchmark integration, from the sibling benchmark repository:

```sh
PYTHONPATH=src .venv/bin/python scripts/validate_system_one_suite.py \
  --suite ../datasets/build/system-one-v1-frozen \
  --output build/system-one-v1-capacity.json
```

This validates typed gold, hashes and scorer behavior with mock answers. It is not a model run. The capacity report records whole-case schema eligibility for the current TypeLLM, Sev and Span adapters; context limits and runtime support still need remote testing. ArBanking77 retains 77 choices and MASSIVE 60; do not shrink those candidate sets silently to accommodate a model.

## Original data design

All policies are fictional and explicitly labeled. Eight domains cover government routing, complaints, application prerequisites, banking/payments, telecom/utilities/logistics, enterprise HR/IT, procurement/invoices, and tool/text-UI actions.

The 80-policy controlled component tests conjunction, missing evidence, negation of the question, invalid prerequisites and irrelevant urgency. It uses one shared logical template and ten fact patterns per policy. Therefore 800 families are **not** 800 independent policies, and this component alone cannot establish enterprise generalization. Its outputs include Boolean, action choice and ordinal incompleteness counts. The natural-language component adds thresholds, exceptions, priority rules and more conversational wording.

The controlled split has 200 development, 200 validation and 400 reserved-evaluation families. Policy identifiers and translations stay together; no controlled policy crosses splits. Because the generator and logical template are shared, the reserved set is **not a sealed or contamination-free holdout**. Existing natural drafts remain development-only. A later publication study can add independently authored policies without pretending these exposed cases are secret.

English, MSA and Saudi versions of original scenarios share facts and gold. Policies remain MSA in Arabic conditions. The controlled Saudi requests deliberately use record-style language; they are not a corpus of natural Saudi customer conversations. Dialect claims should primarily be checked on the natural drafts and suitable source data.

## Source decisions

| Source | v1 treatment |
|---|---|
| Fast Decisions | 1,700 public cases; multi-label tasks decomposed into Boolean membership; whole-case exact match differs from original scoring |
| ArBanking77 | Five paired EN/MSA families per intent plus five unpaired Saudi examples per intent; 1,155 cases |
| MASSIVE | Five aligned families per available intent where possible; duplicate/conflicting language pairs filtered; 576 cases; source Arabic register not assumed |
| Paired MSA–Saudi tool use | All 150 records with pinned tool schemas; action-only projection |
| AISA / Arabic Function Calling | 113 stratified schema-enriched cases; all 5,079 AISA test IDs overlap the earlier function-calling source, so counted once |
| Arabic agent eval | 44 single-call name-selection diagnostics; multi-step cases excluded from this projection |
| Absher | 380 MCQ diagnostics; Saudi language/culture, not government service eligibility |
| AraTrust | 150 MCQ diagnostics |
| ArabFuncBench | Excluded until gated access terms are resolved |
| Syntha | Inspiration only; commercial data not acquired |
| SILMA RAG QA / ArabicRAGB | Excluded from decision v1; need a separate reviewed retrieval/answerability task and rights review |
| AraSafe | Excluded because its historical ledger lacks a declared license |

Source URLs and licensing are retained in row provenance and the source records. Share-alike and attribution obligations remain attached to their subsets. No employer data is included. The public subset and current revision are listed in the Public release section above.

## Evidence and scoring

The final audit passes hashes, case identities, typed labels, paired-gold consistency and controlled policy-group isolation. There are zero repeated exact state groups after pair-aware MASSIVE filtering. This does not claim semantic deduplication across all sources. Twelve focused dataset tests and ten benchmark scorer tests passed.

Report quality separately by pack, task, register and output type. Do not average all 6,884 rows into a headline leaderboard. Count invalid outputs and unsupported coverage. Safety annotations exist only on applicable original cases; unannotated reference cases are not proven safe. Language deltas use actual paired families only. Group uncertainty by policy/lineage rather than counting translated rows independently.

The next phase is remote execution: fixed CPU allocation and GPU configuration, identical model revisions and declared precision, hosted APIs as a separate latency lane. Dataset creation is finished for this candidate. Execution evidence belongs to the benchmark repository; the public natural-development experiment is tracked there.

## Viewer and card update

Revision `788bc10036f4e253ff18f0f926b920ce95f1ef73` adds actual English/MSA/Saudi examples and full choice, Boolean and score examples to the card. Viewer exports omit `provenance_json` and `release_rights_json`; join by case `id` to `metadata/<config>/provenance-and-rights.jsonl`. All 5,184 original typed benchmark rows and their hashes are unchanged. Earlier experiments retain their original revision pins.
