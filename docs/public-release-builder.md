# Rebuild the public Najd Benchmark

A new checkout can rebuild every published question, answer and case metadata field using public inputs. The build does not download the target case files. A separate verification step downloads the target only after reconstruction.

## Current default collection

After the historical build below, run `uv run python scripts/build_unified_release.py build/public-release/release build/current` to produce version `2026.09.27`: one 6,089-case collection without `audit_status`. The input hashes are checked before conversion; only that field is removed. Specific issue notes remain. Historical artifacts and their verification below retain their original representation.

## Run it

```sh
uv sync --locked --extra dev --extra parquet --extra excel
uv run python scripts/reconstruct_public_release.py --output build/public-release
uv run python scripts/verify_public_release.py build/public-release
```

Use a new output directory on each run. No credentials, private archive, Drive files or model calls are required. Network access to the pinned upstream repositories is required. The build fails on source hash drift, missing IDs, duplicate selections, changed case bytes or missing fixtures.

## What is reconstructed

| Artifact | Method | Equality requirement |
|---|---|---|
| `cases.jsonl` — 5,717 rows | 29 upstream adapters plus committed selection and repair rules | Exact published SHA-256 |
| `quarantine.jsonl` — 372 rows | Upstream cases, public archived legacy cases and fresh public riddles, with preserved historical annotations | Exact published SHA-256 |
| Two Parquet exports | Serialize rebuilt cases using an explicit schema | Every value, row order and schema match; serialization bytes may differ |
| 11 fixtures | Fetch pinned public legacy fixture files and copy into six case workspaces using historical directory layout | Every downloaded and installed file hash matches |
| Seven historical JSON documents | Preserve pinned schema, manifests, source ledger and audit/repair records | Exact published SHA-256; these historical records are copied, not newly performed audits |
| `checksums.json` | Generate from reconstructed artifacts | Describes this build, including its Parquet serialization |

The separate verifier checks all 11 release payload files. Output also includes `evidence.json`, `verification.json`, and the installed fixture workspaces. It does not run models or reproduce historical model scores.

## Public reconstruction boundary

The [selection manifest](../releases/2026.09.14/public-selection.json) records IDs, split membership, order, historical audit labels and metadata for the web questions. It was recovered from published revision `43674ef228c1461d6fd34e20c20f51efcbdce56d`. It contains no target prompts or expected answers. This is an explicit recovered release specification, not a claim to have recovered the original selection process.

| Cases | Public input | What remains unknown |
|---|---|---|
| 5,725 | Immutable external source files with verified hashes and adapters | None required for rebuilding these selected case contents |
| 31 | [Public original legacy subset](https://huggingface.co/datasets/najdresearch/najd-legacy-31), revision `ccbf837af54611fa8106e4355302fa2b4d4660f9` | Original authoring history |
| 333 | [Fresh question snapshot](https://huggingface.co/datasets/najdresearch/arabic-riddles), revision `96dd7b99b31233f83325307c778e756501afb8fc` | Original extract bytes and original page snapshots |

The 333 questions and answers come from the fresh snapshot. Their old provenance fields come from the recovered metadata specification so the historical release remains identical. This reconstructs the published records; it does not transform fresh retrieval evidence into proof of the missing original extract. Live recollection must be compared against this pinned snapshot before any update.

The private 178,517-row intermediate export is no longer a build dependency. The current public builder assembles the selected release directly. Old private replay commands remain for historical investigation only.

## Sources and research use

This collection is used for research into Arabic and Saudi model evaluation. All sources are attributed in the [source attribution register](source-attribution.md), the release source ledger and each case's provenance. Research use is an intended purpose, not a replacement for upstream terms or redistribution permission.

The nine web sources have owner-confirmed redistribution permission recorded in this project's publication history. For other sources with historical `permission-on-file` assertions, the permission documents have not been located or verified. That rights evidence remains open and must not be represented as a completed legal review. This build does not publish a new dataset or broaden anyone's license.
