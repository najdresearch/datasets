# Public reconstruction acceptance criteria

A reader must be able to rebuild the release using this repository and public inputs, without Najd's private archive. Downloading our own Hugging Face output is artifact recovery, not source reconstruction.

## Current audit

Run from the repository root:

```sh
uv sync --extra dev
uv run najd-datasets audit-public-inputs releases/2026.09.14/sources.json --sources sources
```

This offline command inventories every source and counts every published row. It does not download sources or certify reconstruction. A zero exit code means the inventory is internally consistent, not that the release is complete.

| Historical rows | Input status | Remaining evidence |
|---|---|---|
| 5,725 | Public raw URLs, hashes and adapters declared | Fresh clean-room execution, selection and full output verification |
| 31 | Private predecessor input | Public rights-cleared original input or successor replacement |
| 333 | Original authorized extract missing | Public original reconstruction path or successor removal/replacement |
| 6,089 | All published rows accounted for | Historical public reconstruction remains incomplete |

The 333 rows have fresh content-match evidence. That does not recover the missing original extract. See [private extract dependencies](private-extract-dependencies.md) and [remaining-source adapters](remaining-source-reproduction.md).

## Completion gates

| Gate | Required evidence | Stop rule |
|---|---|---|
| Public inputs | Pinned public original URLs, raw hashes, license and redistribution basis | No private files, credentials, or output-as-input substitution |
| Transformation | Versioned adapter, normalization, corrections and deterministic ordering | Stop on any unexplained field difference |
| Selection | Public selection algorithm or ID manifest and split rules | No selection silently borrowed from the target output |
| Reconstruction | Clean checkout builds every row and metadata field; artifact hashes match where byte identity is claimed | Content-only comparisons cannot claim full artifact reproduction |
| Rights | Documented public redistribution permission | Public accessibility alone is insufficient |
| Release | CI evidence, source coverage, change log and immutable release manifest | Never overwrite the historical release |

If a historical source cannot satisfy these gates, retain its incomplete status. Create a new successor release with an explicit ID-level removal/replacement mapping, reason, counts, rights, split changes and fresh scores. Do not carry old scores across changed datasets.

`review_status=not_reviewed` remains informational under the existing policy; this audit does not change inclusion or publish anything.
