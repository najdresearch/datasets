# Review protocol for a trusted evaluation set

The existing public release is a collection of candidate cases. Structural certification checked fields and source links; it did not establish that questions or answers are correct. A trusted set needs independent rights and Arabic/domain review.

| Gate | Reviewer records | Stop rule |
|---|---|---|
| Source rights | Exact artifact, license or written permission, attribution terms, reviewer, date | Do not publish a new derivative when the basis is unclear. |
| Privacy | Scan source and case text for personal or employer material; record disposition | Quarantine any case requiring private data. |
| Semantic pilot | Two independent reviewers judge a small, stratified sample of prompts, answers, ambiguity, dialect, and tool schema | Revise or exclude a source if errors cluster; do not score models yet. |
| Full case review | Reviewer ID, decision, corrected answer or exclusion reason, evidence URL, adjudication | Hold a case until disagreements are resolved. |
| Split freeze | Case IDs and hashes for development and sealed evaluation partitions | Do not tune on sealed cases. |

Review decisions belong in a private, access-controlled record until publication rights are established. A release manifest should cite only approved reviewer IDs, counts, and artifact hashes. No review approval is implied by reproducibility; current public data omits review annotations.

For the first source, generate a deterministic two-per-category packet (12 cases from six categories) in the ignored `build/` directory:

```bash
uv run najd-datasets prepare-review build/arabic-agent-eval/cases.jsonl --output build/arabic-agent-eval-review.csv
```

Give separate copies to two independent Arabic/tool-use reviewers. Record their decisions separately before adjudication. The CSV is a working record and should remain private; do not commit it. A rights reviewer should verify the pinned data license and required attribution independently of the semantic reviewers.
