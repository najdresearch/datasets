# Saudi System One decision study v0.2

This suite should reveal which models make useful business decisions in English, formal Arabic and Saudi Arabic. Counts in `study.json` are targets, not generated or reviewed data. No release is eligible yet.

## Three separately reported parts

| Part | Contents | What it establishes |
|---|---|---|
| Public reference | Fast Decisions, ArBanking77, MASSIVE, existing paired tool-use and Arabic agent/function/RAG sources, eligible new sources | Comparability with known tasks; exposure to training data is possible |
| Original Saudi workflows | 800 scenario families across eight workflows, each in EN/MSA/Saudi | Primary enterprise decision evidence after review and sealing |
| Diagnostics | Dialect meaning, safety, perturbations, context length and candidate-count tests | Explains failures; does not silently change the primary score |

The existing 48-case pilot remains an adapter regression test. Syntha is inspiration-only until suitable rights are established. Gated ArabFuncBench remains pending access; do not silently drop it from reports. Absher-Benchmark tests Saudi language/culture; its name does not establish government-service coverage.

## Sample targets

For each of eight workflows: 25 development, 25 validation and 50 held-out families. Total: 800 families, 2,400 base language variants; primary holdout: 400 families, 1,200 variants. This supersedes the smaller 240-family design in the source review. Author and review the first 40 development families before scaling.

More translated rows do not create more independent evidence. With 400 independent families, a simple single-proportion calculation at 50% accuracy has an approximate 95% margin of 4.9 percentage points. That is an illustrative bound, not power for a paired model comparison or a guarantee: model disagreement and template clustering change uncertainty. Fifty held-out families per workflow support exploratory slices, not confident small-gap rankings. Extend a later frozen study if those slices are too uncertain.

Before sealing, simulate paired-comparison power using development disagreement rates for a prespecified practically meaningful gap (initial planning target: 5 percentage points). Freeze sample size and hypotheses before seeing holdout model rankings. Do not repeatedly add cases until a favored difference becomes significant.

## Case design

Use original policies or dated official reference material with an explicit source and rights record. Supply decisive policy evidence to every model. Keep closed-book knowledge separate. Enterprise-company scenarios use fictional policies and names unless actual public material is cleared; they must not imply real company behavior.

Each family has a concrete decision, plausible competing choices, a rationale, a negative or boundary condition where relevant, and aligned EN/MSA/Saudi renderings. Review full state, policy and option text, not only the query. Track Saudi register and reviewer rather than labeling all Gulf text Saudi. A separate mixed-language condition keeps English tool schemas fixed.

| Dimension | Required coverage |
|---|---|
| Output | Boolean, single choice, ordinal score; multi-label and arguments separately |
| Appropriate action | Proceed, refuse, clarify, abstain, escalate, confirm |
| Difficulty | Direct cases, close alternatives, missing facts, conflicting facts, exceptions |
| Robustness | Negation, spelling, digits, code-switching, irrelevant context, injected instructions, option order |
| Context | Short and longer policies; fixed published token/character buckets |
| Candidate set | Small and larger choice lists; unsupported sizes declared |

Preserve original label spaces on public benchmarks. A restricted-choice adaptation is a new task, with distractor selection recorded, not an equivalent source score. Tool selection and argument generation are distinct capability tracks. Text-UI next actions do not measure screenshot understanding.

## Data controls

Record source URL/revision, source row ID, upstream lineage, license and redistribution basis, transformation, domain, decision type, register, template group, split, gold rationale, reviewer and adjudication. Keep answer/review metadata out of requests sent to models.

Audit AISA against its credited Arabic-function-calling upstream; audit RAG collections against constituent sources. Use source IDs and normalized text for exact overlap, then review near-duplicates. Union translations, paraphrases, templates and overlapping source records into split groups before allocation. Preserve upstream splits; publicly exposed source tests are never described as newly sealed Najd holdout.

Two independent qualified reviewers label held-out cases; adjudicate disagreements and record agreement before adjudication. Do not let the evaluated model provide the final gold. Unresolved rights, ambiguous gold or translated meaning changes block a case. Sealed content lives outside the public Git repository; public code stores only its contract and permitted metadata.

## Reporting contract

Report accuracy and macro-F1 where appropriate, invalid/error rate, unsafe-action rate on applicable cases, language gaps, paired disagreement and coverage. For abstaining models, report coverage versus error on answered cases; abstention must not hide missed decisions. Calibrate probabilities on validation only when genuinely available; distinguish logits, generated probability estimates and unsupported probabilities.

Primary original-workflow summary: equal weight per workflow, with separate EN/MSA/Saudi results. Public sources and diagnostics keep separate scorecards. Use paired family/group bootstrap intervals for model differences. Predeclare primary contrasts; label other pairwise comparisons exploratory or correct for multiplicity. Display ties/inconclusive differences rather than forcing a rank. Publish aggregate weighting and unsupported-task counts.

On the remote server, run CPU and GPU separately with fixed allocations, model revisions and declared precision/runtime. Compare matched settings separately from optimized deployment settings. Repeat quality checks per hardware/precision. At concurrency 1/4/16 measure complete-response p50/p95/p99, throughput, errors and quality; document queueing, warmup, cold start and sample counts. Hosted endpoints retain a separate latency lane. Timing repetitions are not extra quality examples.

## Implementation milestones

| Milestone | Acceptance evidence |
|---|---|
| Source inventory | `study.json`, existing pinned manifests, unresolved rights/access explicit |
| First development slice | 40 authored families, reviewed language alignment, source adaptation samples |
| Dataset build | Reproducible manifests/hashes; no cross-split lineage; coverage and rights reports |
| Local validation | Schema and mock scorer checks; no model loading |
| Remote smoke | One EN/MSA/Saudi family per supported output type, real adapter evidence |
| Full study | Reviewed sealed cases, frozen protocol, fixed CPU/GPU runs and independent timing repetitions |

Source URLs and declared reuse status are in `study.json` and [the source review](../../docs/saudi-decision-source-review.md). Existing source metadata is evidence of reconstruction, not completed semantic validation.
