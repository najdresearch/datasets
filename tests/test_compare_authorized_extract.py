import json
from pathlib import Path

from najd_datasets.authorized_extract import canonical_case, compare


def test_private_extract_comparison_checks_all_published_fields(tmp_path: Path):
    source = {
        "source_id": "example",
        "source_item_id": "001",
        "category": "puzzles",
        "subcategory": "riddles_general",
        "content_type": "riddles",
        "question_ar": "ما السؤال؟",
        "answer_ar": "الإجابة",
    }
    extract = tmp_path / "authorized-items.jsonl"
    extract.write_text(json.dumps(source, ensure_ascii=False) + "\n", encoding="utf-8")
    published = {
        **canonical_case(source, 1),
        "audit_status": "quarantined",
        "audit_issues": ["unverified_exact_source_link"],
    }
    quarantine = tmp_path / "quarantine.jsonl"
    quarantine.write_text(json.dumps(published, ensure_ascii=False) + "\n", encoding="utf-8")
    assert compare(extract, quarantine)["totals"] == {
        "exact": 1, "changed": 0, "missing": 0,
    }

    published["tags"] = ["different"]
    quarantine.write_text(json.dumps(published, ensure_ascii=False) + "\n", encoding="utf-8")
    assert compare(extract, quarantine)["totals"] == {
        "exact": 0, "changed": 1, "missing": 0,
    }
