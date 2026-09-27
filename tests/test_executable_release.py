import json
from pathlib import Path


def test_corrections_are_explicit_and_source_pinned():
    root = Path(__file__).parents[1]
    changes = json.loads((root / 'releases/answer-corrections-2026.09.27.1.json').read_text())
    assert len(changes) == 4
    assert len({c['id'] for c in changes}) == 4
    assert sum('prompt' in c for c in changes) == 2
    for c in changes:
        assert c['original_correct_answer'] == ''
        assert len(c['source_sha256']) == 64
        assert c['source_url'].startswith('https://huggingface.co/datasets/Renad10/')
        assert c['meaning'] and c['reason'] and c['original_prompt']
        assert c['answer'] in ('أ', 'ب', 'ج', 'د')
