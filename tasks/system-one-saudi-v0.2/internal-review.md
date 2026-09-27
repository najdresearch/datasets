# Internal review of the decision draft

This is an author-side review and automated audit, not independent bilingual certification. The latest artifacts are Saudi draft v0.4 (144 cases) and public adapter smoke v0.3 (210 cases). Earlier outputs remain intact.

## Findings and fixes

| Finding | Fix / disposition |
|---|---|
| Choice explanations repeated the action name without identifying decisive facts | Replaced all 40 choice rationales with case-specific policy reasoning |
| Unrequested cancellation/withdrawal was not consistently listed as unsafe | Added labels to service and application cases, including submitting after explicit withdrawal |
| English banking examples inherited the MSA source split | English split now explicitly unknown; MSA keeps its recorded source identifier prefix |
| Source action list was inferred from gold labels | Fixed the public action contract independently and reject unexpected labels |
| Tool adapter lacked explicit action-decision policy | Added a uniform policy distinguishing call, clarify, answer without tool and unsupported; mock environment is explicit |
| Unknown source dialects were silently treated as Saudi | Reject unknown varieties |
| CSV reading split text lines before parsing | Parse complete decoded streams to preserve quoted multiline values |

Original expected decisions were checked against their supplied fictional policies and retained. This does not establish that all language variants are independently equivalent. The original review table contains all versions and the revised rationales.

## Evidence and remaining limits

`internal-audit.json` records case counts, paired gold consistency, exact state duplicates and option counts. Six dataset tests pass; both packs pass the benchmark's hash/schema/request-separation and mock scoring checks. No inference occurred.

| Remaining limitation | Required next work |
|---|---|
| 48 original families share only ten declared template groups; Boolean payment and priority cases also overlap conceptually with earlier workflows | Use conservative cross-template lineage groups; do not claim 48 independent policy tests or split related groups into holdout |
| Boolean and score coverage is concentrated in payment and IT | Add distinct policies and workflows before final sampling |
| Banking keeps 77 intents | Gate incompatible model adapters; never silently reduce choices for a shared ranking |
| Reference subset takes first available examples from 20 intents | Replace inspection sampling with a prespecified stratified sample for the full suite |
| Saudi bank samples lack pairing identifiers | Report an unpaired Saudi slice; do not infer a paired language gap |
| Tool projection only scores the action category | Add tool selection and argument evaluation as separately specified tasks |
| Safety labels cover modeled actions, not all possible operational harms | Review severity and denominators; do not claim production safety |
| Many original cases state the decisive fact directly | Expand with matched boundary cases and realistic distractors after bilingual review |

All packs remain non-publishable. Independent reviewers must adjudicate labels and naturalness before sealing an evaluation set. User approval of the draft is recorded as direction/format feedback, not independent annotation. Current policy text is fictional and must not be represented as actual government or company rules.

## Next release

Prioritize new independent policy families over paraphrase volume. Add Boolean and ordinal examples across government prerequisites, complaint escalation, account access and procurement. Keep all variants and conceptual near-duplicates together. Then sample the public sources by intent/action with separate source scorecards. Model execution remains remote-only for heavy runs.
