# Policy expansion v0.5

The next dataset slice adds different decision rules, not only different wording. It remains local development data built from fictional policies. No model was loaded.

| Measure | Current count |
|---|---:|
| Scenario families | 72 |
| EN / MSA / Saudi cases | 72 each, 216 total |
| Conservative policy groups | 15 |
| Choice families | 40 |
| Boolean families | 16: eight true, eight false |
| Ordinal families | 16: four per level 0–3 |
| Previously provisionally accepted families | 48 |
| Newly authored families | 24 |

Earlier Boolean payment and IT scoring families are grouped with their related original workflows. That reduces the old ten nominal groups to eight conservative groups; seven new groups bring the total to fifteen. Families within a policy group are dependent and must stay together when future splits are assigned. All current cases remain development-only.

| New policy group | Decision tested | Boundary or exception |
|---|---|---|
| Municipal grant eligibility | Boolean | Inclusive 12-month threshold and unresolved applications |
| Complaint reopening | Boolean | Inclusive 10-day window plus new evidence |
| Temporary contractor access | Boolean | Sponsor approval, expiry limit, no export privilege |
| Procurement exception | Boolean | Three quotes or documented exception, with conflict-of-interest veto |
| Invoice follow-up | Ordinal | 0, 7, 30 and 31 days; urgency/amount distractors |
| Application completeness | Ordinal | Missing versus invalid documents |
| Municipal report priority | Ordinal | Highest applicable severity rule |

The policy text explicitly marks these as fictional. Arabic policies remain MSA while requests vary between MSA and Saudi Arabic. Original rationales accompany all cases. New variants are author-checked drafts; independent bilingual review remains pending. The user's provisional acceptance applies to the earlier 48 families, not retroactively to unseen additions.

## Reproduce

```sh
PYTHONPATH=src python3 -m najd_datasets.saudi_decisions \
  --source fixtures/saudi-decisions/families-v0.5.json \
  --output build/saudi-decisions-draft-v0.5
```

Use a fresh output directory. The builder emits the case file, source/case hashes, counts and a review table. From the benchmark repository, run `scripts/validate_saudi_draft.py` against this directory for mock-only scorer validation.

Builder checks now reject language-misaligned ordinal scales, unsafe labels equal to gold, incompatible unsafe value types and unavailable unsafe choice labels. The pack passes builder tests and benchmark mock scoring. None of these checks is a model-quality result.

## Remaining before a strong-signal full suite

This release expands contract and policy coverage; it is not a representative enterprise sample or a sealed holdout. Domain counts are deliberately uneven during development. Future sampling must balance the declared workflows, expand independent policy groups and retain separate reference-dataset scorecards. Existing-source adapter samples remain unchanged by this release. Remote CPU/GPU configuration is not provisioned.
