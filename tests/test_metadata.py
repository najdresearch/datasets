from najd_datasets.metadata import without_review_metadata


def test_removal_preserves_content_and_does_not_claim_review():
    original = {
        "id": "one",
        "review_status": "legacy",
        "prompt": "Question?",
        "expected": {"answer": "Answer"},
        "audit_status": "quarantined",
        "sources": [{"review_status": "legacy", "url": "https://example.org"}],
    }
    cleaned = without_review_metadata(original)
    assert cleaned == {
        "id": "one",
        "prompt": "Question?",
        "expected": {"answer": "Answer"},
        "audit_status": "quarantined",
        "sources": [{"url": "https://example.org"}],
    }
    assert original["review_status"] == "legacy"
