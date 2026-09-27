# Public reconstruction

All 6,089 published case records can now be rebuilt from public inputs. Follow the [public release builder](public-release-builder.md) for commands, verified artifacts and the precise reconstruction boundary.

| Requirement | Evidence |
|---|---|
| Public inputs | Pinned source files, public legacy subset and fresh riddle snapshot |
| No target answers as input | Candidate-only adapters plus a committed selection manifest without question/answer content |
| Complete records | Both JSONL SHA-256 values match the published metadata-free revision |
| Full packaging | Equivalent Parquet tables and preserved historical JSON documents |
| Fixture setup | Hash-verified fixture files installed into all six relevant case workspaces |
| Future regressions | Unit tests and a clean Linux public-reconstruction CI job |
| Rights evidence | Source attribution recorded; some historical permission assertions remain unverified |

The original web extract, original legacy authoring process and private intermediate export are not recovered. The builder documents its public input boundary instead of claiming those histories were recovered. Historical metadata is preserved as historical metadata.

The offline `audit-public-inputs` command inventories old source manifests; it is not the current end-to-end build. The [dependency ledger](../releases/reconstruction-dependencies.json) tracks current closure scopes. Research purpose does not substitute for redistribution permission; see [source attribution](source-attribution.md).
