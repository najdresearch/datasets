# Every published Najd Benchmark data point

> Historical provenance and original pinned artifacts are described below. The 31 selected legacy cases and 333 fresh questions are now public: see [standalone publications](standalone-publications.md). Current public revisions omit review annotations: see [metadata migration](metadata-migration.md). Availability of those subsets does not yet establish a complete end-to-end public rebuild.

The Arabic Agent Eval page explains just one source. The complete Najd Benchmark 2026.09.14 release has 5,717 certified cases and 372 quarantined cases from 39 recorded source IDs. This repo can fetch and verify **all 14 files** at the pinned Hugging Face commit, then account for every one of the 6,089 case IDs.

```bash
uv run najd-datasets sync-release releases/2026.09.14/snapshot.json --output build/hf-2026.09.14
```

The command checks the exact remote file list, SHA-256 of every release file, unique case IDs, per-source counts against `sources.json`, and source provenance. It writes a `verification-report.json` and `case-index.csv` next to the downloaded release. Both and all dataset files remain under ignored `build/`; no case text is committed to Git. The release includes the two JSONL files, two Parquet viewers, a source ledger, repair log, audit, schemas, manifests, and the dataset card.

| Coverage question | Verified answer |
|---|---:|
| Published case rows | 5,717 |
| Quarantined rows | 372 |
| Distinct case IDs accounted for | 6,089 |
| Source IDs reconciled with ledger | 39 of 39 |
| Files matched to pinned hashes | 14 of 14 |
| Cases without `sourceFile` | 0 |
| Cases without `sourceRow` | 150 |
| Cases without `sourceRevision` | 333 |

The 150 without `sourceRow` come from the paired MSA/Saudi tool-use source. The 333 without `sourceRevision` are the nine [private-extract dependencies](private-extract-dependencies.md), all quarantined. The index preserves these gaps rather than inventing provenance.

The index also labels the upstream rebuild state of each case: **5,725 rows from 29 pinned external sources**, **31 internal-copy rows from a hash-checked private archive file**, and **333 rows whose original private extract is absent**. A fresh extraction matched all published non-audit fields of the last 333 rows, but it is a new source snapshot rather than the missing original file. All 6,089 rows remain available and hash-verified in the local snapshot.

## Rebuilding from sources

The [historical reproduction](reproduction.md) starts from a preserved 178,517-row pre-audit export and rebuilds both public JSONL case files byte for byte. The [source adapters](source-catalog.md) cover the 29 pinned external sources and the one private-archive copy, accounting for **5,756 published rows**. Some adapters generate larger candidate pools; their selected public rows match field for field after recorded transformations. The [remaining-source guide](remaining-source-reproduction.md) explains the 14 adapters added after the initial release reconstruction. For the nine private-extract sources, a fresh extraction reproduces every non-audit field of their 333 published rows; the original extract bytes remain missing, and the rows retain their historical quarantine status.

The published copy is evidence of what was released; the missing historical private extract remains the only original-input gap. No source-content verification changes the historical audit status or certifies answer correctness.
