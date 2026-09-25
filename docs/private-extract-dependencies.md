# Historical private extract dependencies

The original upstream builder read `private/authorized-source-extracts/authorized-items.jsonl`. That file is absent from the preserved Git and evidence bundles. We do not copy it into this repo or infer its contents from public cases.

The public [source ledger](../releases/2026.09.14/sources.json) records nine source IDs using that path. All 333 of their selected cases were quarantined; none entered the 5,717 certified case file.

On 2026-09-25, an exact-filename search of the user home, Projects, local Drive sync, and connected Drive metadata found no separate `authorized-items.jsonl`. The preserved evidence-file inventory lists an example file but not this private input. This is a search result, not proof the original no longer exists in another location.

The original file was still absent after checking the local recovery bundles and macOS Time Machine availability. The archived collector was then rerun for the nine recorded source pages into the Git-ignored `private/authorized-source-extracts/fresh-2026-09-25/`. All nine pages responded successfully. It produced 487 fresh candidate items, with SHA-256 `89979ad0625c6ee2c0b5a044f2edb44b387d7f2567541cc546c3c7e9d4d0b970`. A comparison against the historical quarantine found **333 exact matches out of 333** on source ID, item ID, Arabic question, and answer; zero changed or missing. The private folder holds the new extract, page manifest, item comparison report, and a snapshot verification report.

All nine page responses now have private snapshots. Seven snapshots match the collector manifest's byte hashes. Two pages changed at the byte level on refetch; their newly saved snapshots still produce all 50 Twinkl Arabic riddle items and all 15 Mawdoo3 science items with identical question and answer text. The Qusama page parses 97 pairs; one duplicate was removed by the archived collector, leaving 96 matching extract items. Keep the original manifest and the refetch hashes distinct.

The archived importer's field mapping now reproduces **all non-audit fields of all 333 published rows exactly**, including IDs, track, language, prompt, expected answer, tags, provenance, source-row position, and review-status value. The audit fields are release metadata and are excluded from the source-content comparison. This verifies published row content against a fresh extraction, not the missing historical file's bytes. The fresh extraction must not be presented as the original artifact.

| Source | Selected | Certified | Quarantined |
|---|---:|---:|---:|
| almrsal-general-contest | 11 | 0 | 11 |
| almrsal-riddles | 99 | 0 | 99 |
| mawdoo3-animals | 19 | 0 | 19 |
| mawdoo3-riddles | 18 | 0 | 18 |
| mawdoo3-science | 15 | 0 | 15 |
| qusama-riddles | 96 | 0 | 96 |
| sayidaty-children-riddles | 1 | 0 | 1 |
| twinkl-arabic-riddles | 50 | 0 | 50 |
| twinkl-islamic-questions | 24 | 0 | 24 |

Before reconsidering one of these sources, obtain an authorized item-level artifact outside Git, verify its origin and reuse terms, build a pinned collector, and run independent rights and semantic review. If that evidence is unavailable, keep the cases quarantined. The historical byte-for-byte replay can still run from the preserved pre-audit export; it does not need the missing extract.

## Recovery path

The preserved archive contains `scripts/scrape_authorized_question_sources.py`, the collector that wrote this exact path, and `scripts/validate_authorized_questions.py`, which generated a human-review queue. The collector records canonical page URLs, retrieval URLs, content hashes, and fetch times in a sidecar manifest. Its source list includes the nine affected source IDs, but a fresh run may see changed pages and produce different rows.

| Step | Evidence required | Stop rule |
|---|---|---|
| Search backups for the original file and its `.manifest.json` sidecar | Original bytes, source snapshots or URLs, timestamps, and hashes | If only derived public cases survive, do not call this original-source reproduction. |
| If absent, rerun the archived collector into `private/` after checking source access and reuse terms | New raw snapshots and manifest with pinned hashes | If access or reuse is uncertain, do not collect or republish. |
| Match candidates to the 333 historical rows using `sourceId` and `sourceItemId`, then compare question and answer fields | Per-row match report, including mismatches and missing IDs | Do not silently replace a historical row with today's page content. |
| Review matched or replacement items | Exact source links, reuse decision, bilingual review, and specialist review for religious claims | Keep unreviewed or unverified rows quarantined. |
| Publish a new version only if all release gates pass | Pinned inputs, deterministic builder, counts, checksums, and review record | Preserve the 2026.09.14 release as an immutable historical snapshot. |

`private/` is Git-ignored. Store authorized raw files and review records there or in a controlled private store; commit only non-sensitive manifests, code, and aggregate verification reports. A new scrape is a new source snapshot, not a recovery of the original missing file.

For another comparison, run `uv run python scripts/compare_authorized_extract.py <private-extract.jsonl> <published-quarantine.jsonl> --output <private-report.json>` after syncing the pinned public release. The command reconstructs each selected row using the archived mapping and checks every field except audit metadata. It reports counts and hashes, never row text.
