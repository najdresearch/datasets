# Task generation roadmap

These are design placeholders, not available or approved benchmark packs. The first implementation target is an internal Arabic customer-support version comparison.

| Pack | Candidate data | Quality gate before evaluation |
|---|---|---|
| Arabic customer support | Original fictional policies, conversations, refund and escalation scenarios | Policy-grounded answers, unacceptable actions, Arabic expert review |
| Saudi knowledge | Rights-cleared dated sources and answer citations | Time validity and unambiguous answers |
| Arabic classification | Labels, definitions, balanced natural examples | Agreement and per-label coverage |
| Document / RAG | Licensed documents, queries, answer spans and citations | Retrieval relevance and answer grounding |
| Tool decisions | Tool schemas, call/clarify/abstain decisions and arguments | Executable argument checks, side effects sandboxed |
| Coding agents | Sandboxed repositories and issue tasks | Hidden functional tests; fixed harness version |
| Visual understanding / Arabic OCR | Licensed document images and transcriptions | Layout, reading order and transcription agreement |
| Embedding / reranking | Query-document judgments | Query-level splits, relevance agreement |
| STT | Consented Arabic audio and transcripts | Dialect slices, transcription policy |
| TTS | Licensed text, pronunciation rubric and listening protocol | Blinded human evaluation and consent |

## Common pack proposal

Every proposal supplies: task ID/version, use case, input/output schema, public source manifest, generator version/seed (if synthetic), normalization rules, deduplication lineage, development/evaluation split, leakage checks, rights/privacy record, label rubric, baseline and stop rule. Keep prompt layout meaningful for code, documents and OCR; do not collapse whitespace indiscriminately.

## First support pilot

Use fictional businesses and original policies, never customer records. Cover answer, clarification, escalation, and refusal to invent a policy. Group paraphrases of one scenario in the same split. Keep development examples public; seal pilot cases before comparing versions. Public reconstruction requirements apply to the public dataset release; confidential client task packs remain separate and must not claim public reproducibility.

Acceptance: reproducible generator; scenario lineage; disjoint scenario splits; reviewed gold decisions; pinned policy and rubric; coverage report. Stop if expert disagreement remains unresolved or cases leaked into prompt tuning. No leaderboard claim from toy synthetic examples.
