# Shared contract contribution guide

The benchmark repository owns contract v1. This repository owns source collection,
normalization, synthesis and dataset manifests. Vendored schemas in `contracts/v1` must
match the immutable benchmark revision and hashes in `contracts.lock.json`.

| Contribution | Include before review |
|---|---|
| New source | Source URL/revision, applicable data terms, attribution, transformation and deterministic builder |
| Generated data | Generator version, inputs/settings, lineage, privacy boundary and license evidence |
| Dataset release | Versioned manifest, exact file hash, unique ordered case IDs, count and explicit split |
| Task example | Input/output contract, frozen task pack, baseline and known limitations |
| Changed cases | New dataset version and correction ledger; preserve previous artifacts and result pins |
| Schema change | Propose in benchmark first; pin merged revision here, then update fixtures and CI |

## Working example

`examples/arabic-support-routing-v1` contains eight original CC0 synthetic development
messages, a dataset manifest and a task pack. These are integration examples, not reviewed
production evaluation cases or a sealed test set. No existing Hugging Face rows are changed.

```sh
uv sync --locked --extra dev
uv run python scripts/generate_support_contract_example.py
uv run python scripts/check_contracts.py
uv run pytest -q
```

The tests rebuild exact bytes, validate both schemas and check the 25% constant baseline.
Use the benchmark package's `najd-contract validate-pack` and `najd-contract run` commands
for execution. Arena's admin-only contract preview can inspect a resulting private bundle,
without importing it into the publication workflow.

[Canonical contract and metric guide](https://github.com/najdresearch/benchmark/blob/main/docs/shared-contracts-v1.md).
