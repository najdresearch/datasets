# Every published Najd Benchmark data point

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

The index also labels the upstream rebuild state of each case: 4,982 rows reproduced directly from 16 upstream sources, 333 rows whose original private extract is absent, and 774 rows with a recorded source but no upstream adapter yet. A fresh extraction matched all published non-audit fields of the 333 affected rows, but it is a new source snapshot rather than the missing original file. All 6,089 rows remain available and hash-verified in the local snapshot. Four of the reproduced Arabic Reading Comprehension rows are quarantined for Unicode replacement characters.

## Rebuilding from sources

The [historical reproduction](reproduction.md) starts from a preserved 178,517-row pre-audit export and rebuilds both public JSONL case files byte for byte. Sixteen [source adapters](source-catalog.md) start from pinned original files and account for 4,982 corresponding public rows. Some adapters generate larger candidate pools; their selected public rows match field for field after the recorded audit, review-copy, or explicit case-correction transformation. The other 23 source IDs do not yet have verified upstream-to-public adapters in this repo. For the nine private-extract sources, a fresh extraction reproduces every non-audit field of their 333 published rows; the original extract bytes remain missing, and the rows retain their historical quarantine status.

For each remaining public source, the work is: pin the original artifact and hash, implement its format and field mapping, reproduce its public subset case by case, and document repairs. A published copy is evidence of what was released; it is not a substitute for original-source reconstruction.
