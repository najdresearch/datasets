# Saudi decision development drafts

40 original fictional scenarios, five per workflow, rendered in English, MSA and general Saudi Arabic. Formal policies and action descriptions use MSA in both Arabic conditions. These are agent-authored drafts, not independently reviewed labels or real government/company rules.

Build without models:

```sh
PYTHONPATH=src python3 -m najd_datasets.saudi_decisions \
  --source fixtures/saudi-decisions/families.json \
  --output build/saudi-decisions-draft-v0.2
```

The output includes `cases.jsonl`, a hash manifest, and `review.md` containing all three versions, draft answers and policies. Use a new output directory for each revision. All cases remain development-only. The eight workflow templates must not be split across development and holdout. Future held-out scenarios need independent templates and review.

This slice is choice-only. Boolean and ordinal-score coverage, unsafe-action annotations, detailed per-case adjudication, dialect review and held-out data remain pending. No redistribution license has been assigned to this draft.

## v0.3 extension

Build `families-v0.3.json` with the same command into a new `build/saudi-decisions-draft-v0.3` directory. It contains the original 40 choice families plus four Boolean payment-policy families and four IT-priority ordinal families: 144 cases. Boolean outcomes are balanced and ordinal levels cover 0–3. New questions remain concentrated in two workflows; this is contract coverage, not a balanced final study.

Unsafe choices are explicitly annotated where the available actions include bypassing a prerequisite or an unrequested cancellation. Boolean permission cases also use typed `unsafe_values`. Empty annotations on routing tasks mean no directly unsafe option was modeled, not that routing errors are harmless. All safety labels remain drafts. User approval of the previous slice was a direction/format review, not independent label certification.

## Current reviewed draft revision

Use `families-v0.4.json` for the latest author-side fixes: explicit case rationales and expanded unsafe-action annotations. The generated `build/saudi-decisions-draft-v0.4/review.md` remains unreviewed by an independent bilingual reviewer. Gold decisions are unchanged from v0.3. See `tasks/system-one-saudi-v0.2/internal-review.md` for review scope and limitations.

## Latest expansion: v0.5

`families-v0.5.json` contains 72 families / 216 cases across 15 conservative policy groups. The original 48 families carry provisional user acceptance; 24 additions remain new drafts. Build into `build/saudi-decisions-draft-v0.5`. Details and reproducible commands: `tasks/system-one-saudi-v0.2/expansion-v0.5.md`.
