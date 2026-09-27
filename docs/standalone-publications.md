# Standalone source datasets

Two public datasets now make the requested historical cases accessible without changing the original benchmark release.

| Dataset | Rows | Contents |
|---|---:|---|
| [Najd Legacy 31](https://huggingface.co/datasets/najdresearch/najd-legacy-31) | 31 | Selected original Najd cases, historical row versions and required fixtures |
| [Arabic Riddles and Questions](https://huggingface.co/datasets/najdresearch/arabic-riddles) | 333 | Freshly collected question–answer pairs, with source URLs on every row |

## Legacy cases

Public revision: `dde7eca88d9fe7cc2697502f544f1ebaf953fce3`.
The source package exposes original selected objects in `original/cases.jsonl`, historical row positions in `manifest.json`, and fixtures. The viewer uses a uniform schema with `expected_json` for heterogeneous answer rubrics.

The initial archive export was built using:

```sh
uv run python scripts/build_legacy_subset.py \
  --original private/historical-inputs/m3-saudi-v1/cases.jsonl \
  --reference build/hf-2026.09.14/datasets/najd-benchmark/2026.09.14/quarantine.jsonl \
  --fixtures /path/to/original/suites/m3-saudi-v1/fixtures \
  --output build/najd-legacy-31
```

The script verifies the archived input and historical reference hashes, selects exactly the 31 requested IDs, compares prompts/expected values and packages the three required fixture directories. It does not publish the other 33 archived cases. The selected source objects can now be downloaded publicly; an adapter using that subset instead of the private 64-row input remains to be integrated. Original authoring/generation history is still unavailable.

## Fresh web collection

Public revision: `d21090ba3ad945ae5eb42b999fb5708ff863be70`.
Nine pages produced 488 parsed pairs before selection; all 333 historical selected pairs matched exactly. Source-page categories comprise 298 riddle-labelled pairs, 11 general questions and 24 Islamic knowledge questions. These are not independent human labels.

```sh
uv run python scripts/collect_riddles.py \
  --reference build/hf-2026.09.14/datasets/najd-benchmark/2026.09.14/quarantine.jsonl \
  --output private/riddles-new-snapshot
```

Obtain the pinned historical reference using the existing [release sync instructions](full-release.md). The collector reads `sources/arabic-riddles-pages.json`; parsing functions live in `src/najd_datasets/riddle_parsers.py`. It saves raw snapshots, canonical and retrieval URLs, timestamps, hashes, parsed counts, historical IDs and matching source positions. Any missing pair fails the collection. Live pages may change; the new public dataset is a fixed snapshot, not a guarantee of future live-page equality.

Package a successful collection with a private authorization JSON containing `public_redistribution_confirmed`, `dataset_sha256`, `reviewer`, `date`, and the exact `source_ids` list:

```sh
uv run python scripts/package_riddles.py \
  --snapshot private/riddles-new-snapshot \
  --authorization private/publication-authorization.json \
  --output build/riddles-release
```

The owner explicitly confirmed redistribution permission on 2026-09-27 with source attribution required. This is recorded as owner-confirmed permission, not independently verified licensing. Every source is linked on the card and every row. Raw webpages are not uploaded. No general CC/Apache license is asserted over third-party text.

Both releases preserve `not_reviewed`: content matching and publication are not semantic certification. No original dataset rows, scores, or audit metadata were changed. Historical audit counts in `audit-public-inputs` still describe the old release manifests until public-subset adapters are integrated.
