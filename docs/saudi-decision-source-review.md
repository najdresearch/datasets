# Saudi enterprise decision data — source review

Research checked 2026-09-27. This is a proposed expansion, not an imported dataset or completed rights review. No model inference was run.

## Recommended sources

| Source | Fit | Reuse status and next check |
|---|---|---|
| [ArBanking77](https://github.com/SinaLab/ArBanking77) | 77 banking intents; English, MSA and Saudi variants, with source question IDs | [CC BY-SA 4.0](https://github.com/SinaLab/ArBanking77/blob/main/LICENSE). Preserve attribution and share-alike terms for adaptations; keep this subset separately identified. Audit actual paired coverage and original splits before sampling |
| [MASSIVE](https://huggingface.co/datasets/AmazonScience/massive) | Multilingual intent and slot baseline, useful for paired language controls | CC BY 4.0. Verify Arabic/English alignment by ID. General assistant tasks, not evidence of Saudi government competence |
| [ArabFuncBench](https://huggingface.co/datasets/lsadouk1111/ArabFuncBench) | Native MSA tool selection, government and enterprise-adjacent domains, negative/no-tool examples | Card declares CC BY 4.0; files gated behind contact-sharing agreement. Not downloaded. Inspect terms and rows before reuse |
| [AISA-AR-FunctionCall](https://huggingface.co/datasets/AISA-Framework/AISA-AR-FunctionCall) | Arabic/Gulf tool calls including government, banking, utilities and commerce | Card declares Apache 2.0 and credits upstream data. Audit upstream provenance. Card split counts and viewer presentation differ; derive counts from pinned files. Gulf is not equivalent to Saudi |
| [SILMA RAG QA](https://huggingface.co/datasets/silma-ai/silma-rag-qa-benchmark-v1.0) | Ideas for decisions grounded in supplied evidence | Card declares Apache 2.0, but constituent sources need individual provenance checks. Adapted decision labels require new review |
| [Syntha Saudi support](https://synthabase.com/en/datasets/saudi-support) | Saudi dialect and sector coverage ideas | Vendor page labels full dataset commercial. Do not treat public samples or third-party posts as permission to redistribute full data. Inspiration only for now |

Public datasets are useful regression sets, not a contamination-free holdout. Keep source benchmark scores distinct from newly authored Saudi scenarios.

## Government reference sources

Use official descriptions to design original scenarios. A public web page is not automatically a licensed dataset. Do not scrape individual service records.

| Source | Proposed use |
|---|---|
| [Balady commercial-license renewal](https://balady.gov.sa/en/services/renewal-commercial-license?switch=en) | Service routing, document prerequisites, conflicting request state |
| [HRSD beneficiary complaints](https://www.hrsd.gov.sa/ministry-services/services/client-page) | Complaint versus inquiry, escalation conditions, missing information |
| [ZATCA e-invoicing FAQ](https://zatca.gov.sa/en/E-Invoicing/Introduction/FAQ/Pages/default.aspx) | Invoice-support routing and checks against supplied requirements |
| [Saudi national open-data policy](https://my.gov.sa/content/open-Data) | Discover licensed government datasets; inspect each resource and underlying content rights |
| [BALSAM](https://benchmarks.ksaa.gov.sa/b/balsam) | Discover additional Arabic task families; platform access does not itself establish redistribution rights |

Snapshot and date any policy used for labels. Supply the decisive rule to every model. Separate policy-following from closed-book knowledge tests. Synthetic enterprise rules must be labeled fictional, never attributed to an actual company.

## Proposed original set

Start with 240 distinct scenario families, each rendered in English, MSA and Saudi Arabic: 720 base cases. Review in batches of 40 families before expanding. These numbers are design targets, not statistical guarantees.

| Workflow | Families | Decision |
|---|---:|---|
| Government service routing | 30 | Correct service or clarification |
| Government complaint handling | 30 | Inquiry, complaint, escalation or missing evidence |
| Policy and application prerequisites | 30 | Proceed, reject or request information from supplied rule |
| Banking and payment support | 30 | Intent, fraud escalation or ordinary support |
| Telecom, utilities and logistics | 30 | Outage, billing, delivery, appointment or cancellation |
| Enterprise HR and IT | 30 | Ticket route, priority, authorization or clarification |
| Procurement and invoice operations | 30 | Evidence sufficiency, exception queue, approval boundary |
| Tool and text-UI next actions | 30 | Read, clarify, confirm, execute or abstain |

Add selected perturbations only after the base labels are reviewed: negation, missing fields, conflicting facts, Arabic/Western digits, code-switching, irrelevant context, malicious instructions inside documents and candidate-order changes. Keep translations and all perturbations in the same split. Do not count them as independent scenarios.

Example authored scenario: a requester asks for supplier payment, but the supplied fictional policy requires two approvals and only one is recorded. The correct action is request the missing approval. A Saudi rendering could be: «الفاتورة جاهزة، بس ناقص اعتماد المدير الثاني، حوّلوا للمورد اليوم». The English and MSA versions must preserve that contradiction. This tests authorization and instruction following, not knowledge of an actual firm's process.

## Dataset and evaluation contract

Record family ID, source/revision, original versus adapted status, rights, domain, task, language/register, policy version, expected decision, rationale, reviewer and split. Localize policy/context and tool descriptions as well as the query for a full-language condition; separately test Arabic queries with fixed English tool schemas.

Split by underlying scenario/template/source group before model-driven iteration. A proposed 240-family allocation is 120 development, 40 validation and 80 sealed evaluation; small per-domain holdout slices remain exploratory. Public imported sets retain source splits. Development outputs may be inspected locally; sealed cases must stay outside the public repository.

Score task/domain/register separately, paired language disagreement, abstention, unsafe actions and invalid outputs. Bootstrap uncertainty by scenario family. Report candidate counts and context lengths. Preserve a common decision-only comparison; argument generation is a separate capability track.

Local work is limited to builders, schema tests, duplicate/split checks and mock scoring. CPU/GPU quality and latency run remotely on fixed hardware. Dataset size does not substitute for enough independent timed requests when estimating p95/p99.
