# First source inspection

Small text downloads only; no models or inference. Revisions and hashes are recorded in `source-inspection.json`; raw upstream files remain in ignored `build/source-inspection/`.

| Source | Observed evidence | Consequence |
|---|---|---|
| [Paired MSA–Saudi tool use](https://github.com/aalsaedi/paired-msa-saudi-tool-use-dataset) | 150 rows, 75 explicit pairs; pinned SHA-256 matches; original split is test | Eligible for a separate public-reference adaptation after semantic review; not a new private holdout |
| [ArBanking77](https://github.com/SinaLab/ArBanking77) | Full CSV has 13,083 rows with EN/MSA/PAL columns. Separate Saudi test CSV has 3,580 rows with label/text only | README and inspected full-file coverage differ. Do not align Saudi by row order or label alone |

ArBanking's English/MSA rows can be used for paired testing after audit. Saudi rows can be evaluated as an unpaired source slice, or missing alignment can be obtained from maintainers. A newly authored Saudi rendering must be marked as Najd adaptation, not an upstream translation.

The paired tool source's first inspected family requires asking for a missing city for a weather query. A decision-only adaptation can retain that action; tool arguments and execution correctness require the source's fuller contract. The Saudi bank sample concerns card delivery; preserve the source's full intent taxonomy when reporting its original task.

Do not merge these sources into the 120 original development drafts. They retain separate provenance, splits and licensing. ArBanking declares CC BY-SA 4.0; the pinned tool-use ledger records CC BY 4.0 and a historical permission claim, which must be checked for a new release.
