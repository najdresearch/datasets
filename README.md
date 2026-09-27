# Najd Datasets

Code and source manifests for collecting, cleaning, normalizing, generating and reproducing Najd Research datasets. Consumers download data from Hugging Face; this repository owns how it is built.

## Published datasets

| Dataset | Rows | Purpose |
|---|---:|---|
| [Najd Benchmark](https://huggingface.co/datasets/najdresearch/najd-benchmark) | 6,089 | Historical Arabic/Saudi evaluation collection: 5,717 structurally certified and 372 quarantined cases |
| [Najd Legacy 31](https://huggingface.co/datasets/najdresearch/najd-legacy-31) | 31 | Selected original Najd cases, required fixtures and historical row mapping |
| [Arabic Riddles and Questions](https://huggingface.co/datasets/najdresearch/arabic-riddles) | 333 | Freshly collected question–answer pairs, with source attribution on every row and the dataset card |

The standalone datasets overlap with Najd Benchmark; do not add their counts as independent cases. Current public versions omit review annotations. Questions, answers, IDs, splits and scoring were not changed by that metadata migration. Structural certification is not a claim of semantic correctness.

Current immutable revisions and hashes are in the [migration ledger](releases/metadata-migration-2026.09.27.json). See [standalone dataset builds](docs/standalone-publications.md) and [metadata migration](docs/metadata-migration.md).

## Repository responsibilities

| Repository | Responsibility |
|---|---|
| datasets | Sources, collection, normalization, synthetic generation, provenance and dataset releases |
| [benchmark](https://github.com/najdresearch/benchmark) | Task contracts, shared evaluation/scoring, local reports and pinned execution package |
| [najd-arena](https://github.com/najdresearch/najd-arena) | Website, organizations, managed jobs, private reports, publication and public results |

## Reconstruction audit

See the [complete source dependency audit](docs/reconstruction-audit.md) for all 39 sources, the public-only execution command, and evidence required to close each remaining gap.

## Start locally

```sh
uv sync --extra dev --extra parquet --extra excel
uv run pytest
uv run najd-datasets audit-public-inputs releases/2026.09.14/sources.json --sources sources
```

The offline audit inventories original manifests. To rebuild all 6,089 cases from public sources, use the [public release builder](docs/public-release-builder.md):

```sh
uv run python scripts/reconstruct_public_release.py --output build/public-release
uv run python scripts/verify_public_release.py build/public-release
```

Both JSONL files reproduce the published bytes. Parquet exports reproduce values and schema. Historical audit documents are preserved separately. Original authoring/extract history and some redistribution permission evidence remain unavailable; see the documented reconstruction boundary and [source attribution](docs/source-attribution.md).

## Choose a workflow

| Job | Entry point |
|---|---|
| Download every historical published file | [Pinned release inventory](docs/full-release.md) |
| Reproduce historical bytes | [Historical replay](docs/reproduction.md) |
| Rebuild an individual source | [Source catalog](docs/source-catalog.md) and `najd-datasets reproduce-source` |
| Collect a new dataset | [Source standard](docs/source-standard.md) and `najd-datasets collect` |
| Clean or generate | `najd-datasets clean` / `generate`; small original specs in `fixtures/specs/` |
| Recollect the 333 questions | [Standalone publications](docs/standalone-publications.md) |
| Package/publish a new version | `package`, `check-approval`, `publish`; [release protocol](docs/review-protocol.md) |
| Propose a new task family | [Task roadmap](tasks/README.md) |
| Contribute | [CONTRIBUTING.md](CONTRIBUTING.md) |

For example:

```sh
uv run najd-datasets reproduce-source sources/arabic-agent-eval.json --output build/arabic-agent-eval
uv run najd-datasets generate fixtures/specs/reminder-variants.json --output build/generated.jsonl
uv run najd-datasets validate build/generated.jsonl
```

Source adapters verify the historical expected hashes in a compatibility context, then emit current rows without review annotations. Reports distinguish the historical checksum from the new output checksum. Historical replay commands intentionally retain the original artifact representation.

## Release and contribution policy

Every source needs its origin, pinned revision/hash, redistribution basis, transformation and split. Keep credentials, private cases and large artifacts out of Git. Builds go in ignored `build/`; private permission records remain private. Attribution is preserved on dataset cards and rows.

The generic publication command requires a hash-bound approval record and refuses to overwrite an existing version. Omission of review metadata does not disable rights/privacy controls or record a completed review. See the [public reconstruction gates](docs/public-reconstruction.md).

## Next implementation milestone

Build the internal Arabic customer-support version-comparison task pack using original fictional policies and scenario-level splits. Other task families are documented placeholders, not released benchmark packs.
