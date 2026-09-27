# Review metadata removal

Current public rows omit review annotations. No reviewed label or completed-review claim replaces them. Questions, answers, IDs, ordering, task splits, rights records and structural audit outcomes are unchanged.

The Hugging Face migration and current pins are recorded in [the migration ledger](../releases/metadata-migration-2026.09.27.json). It covers Najd Benchmark, Najd Legacy 31 and Arabic Riddles. JSONL rows, Parquet columns, case schemas, cards and checksums were updated together in a new commit for each dataset. Older commit snapshots remain available.

## Reproduce the change

Install the parquet extra, download the previous revision named in the ledger, then run:

```sh
uv sync --extra dev --extra parquet
uv run python scripts/remove_review_metadata.py /path/to/previous-snapshot build/metadata-free --report build/migration-report.json
```

The migration creates a separate output directory. It removes retired review fields recursively, drops Parquet review columns, removes schema requirements, updates cards and recomputes current file checksums. It preserves historical source hashes that describe earlier inputs. The script never uploads by itself.

## Compatibility boundary

Current collection, generation and source-adapter outputs omit annotations; validators no longer require them. Public source manifests omit review status. The historical September 14 adapters opt into a compatibility context only while checking their original pinned output hashes, then strip annotations before returning the current output. Reports distinguish `historical_output_sha256` from the new `sha256`.

The immutable historical replay, archive filenames and `legacy_metadata.py` retain the old representation solely to reproduce old hashes. Migration code necessarily recognizes retired keys and old card text. Do not rename archived paths or rewrite past commits to eliminate those compatibility references.

Benchmark pins the new certified case file hash. A fixed set of 104 ArabicMMLU responses produced identical scores before and after migration. This metadata revision does not change task eligibility or promote structurally quarantined rows.
