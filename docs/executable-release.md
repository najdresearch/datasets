# Fixture and answer completion

The remaining ten cases now have an execution or answer contract. This does not change
historical scores or establish new model scores without running the new release.

| Cases | Change | Evidence |
|---|---|---|
| agentic-02 | Virtual read/write tools, output file checked before semantic judging | contacts.csv |
| document-02,03,05,08 | Virtual reads and evidence-grounded judging | Public brief, policy and meeting files |
| rag-02 | Virtual corpus reads and citation/binding checks by judge | Public corpus including distractor |
| Two Absher true/false items | Derive keys from recorded meanings | Pinned CSV meaning fields |
| Two ambiguous Absher items | Replace cultural-purpose/country claims with meaning questions | Original prompts and corrections in ledger |

```sh
uv run python scripts/reconstruct_public_release.py --output build/historical
uv run python scripts/build_unified_release.py build/historical/release build/unified
uv run python scripts/build_executable_release.py build/unified build/historical/release build/current
```

The last builder checks base bytes, pinned Absher CSV hashes and records, and the public
legacy fixture manifest. Every output file is checksummed. It never invents a missing
upstream answer. Annotations are AI-assisted Najd source interpretations, not independent
expert review. Contributions correcting an annotation must include source evidence and
produce a new release. The original 6,089-case version remains reconstructible.

Sources: [Absher](https://huggingface.co/datasets/Renad10/Absher-Benchmark/tree/554f7457e9f91290f204ac56ab82e707f302944e),
[public legacy fixtures](https://huggingface.co/datasets/najdresearch/najd-legacy-31/tree/ccbf837af54611fa8106e4355302fa2b4d4660f9).
