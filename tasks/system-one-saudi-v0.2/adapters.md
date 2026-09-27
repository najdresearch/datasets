# Reference adapters and typed draft

These are local development artifacts. Source files remain in ignored build storage; no source data or results were pushed.

| Pack | Cases | Scope |
|---|---:|---|
| Saudi draft v0.3 | 144 | 40 choice, 4 Boolean and 4 ordinal families, each EN/MSA/Saudi |
| Public adapter smoke v0.2 | 210 | 150 paired tool-action records, 40 EN/MSA bank records, 20 unpaired Saudi bank records |

Build source adaptations from the previously inspected local files:

```sh
PYTHONPATH=src python3 -m najd_datasets.decision_sources \
  --raw-dir build/source-inspection \
  --inspection tasks/system-one-saudi-v0.2/source-inspection.json \
  --output build/public-decision-adapter-smoke-v0.2
```

The builder verifies raw SHA-256 values against the pinned records. See `source-inspection.json` for exact revisions and `sources/paired-msa-saudi-tool-use.json` for its raw URL. A clean machine must first retrieve those exact files; the adapter does not download implicitly.

Banking uses a deterministic first-available sample of 20 intents and retains all 77 candidate intents. It is not representative; some decision models cannot handle this many options. Report unsupported capacity instead of reducing the candidate set silently. The Arabic source file has no aligned English/Saudi identifiers. Source tests retain their original split in provenance and are exposed public references, never a new holdout.

Tool-use mapping is action-only and includes the pinned tool schemas and reference context. The initial v0.1 artifact lacked these schemas and is superseded by v0.2. Semantic review remains pending. Tool names, arguments and execution are not scored. Keep this pack blocked from public results until reviewed and completed.

Validation to date checks hashes, identities, gold output types, mock scoring and request metadata separation. It does not establish label correctness, safety performance or model quality. Sources and licenses remain as recorded in the source review; publication eligibility is false.
