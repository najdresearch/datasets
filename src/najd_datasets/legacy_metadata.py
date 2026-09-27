"""Compatibility only for hash-verifying the immutable September 14 artifacts.

Current outputs remove this field. Never interpret this legacy label as an eligibility gate.
"""

from contextvars import ContextVar

historical_mode = ContextVar("historical_metadata_mode", default=False)


def historical_review_fields():
    return {"review_status": "not_reviewed"} if historical_mode.get() else {}
