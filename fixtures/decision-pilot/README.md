# Original decision-model development fixture

These are the original synthetic Najd pilot scenarios and question definitions, copied without changing their bytes from `exp/decision-model-benchmark`. No employer data, private evaluation set or user screenshot is included.

Build via `python -m najd_datasets.decision_pilot --source fixtures/decision-pilot --output build/decision-pilot-dev-v0.1` from the datasets repository (use `uv run`). Output contains a checksummed 48-case development pack and provenance manifest. All translations of a scenario share a family ID. Builds refuse to overwrite existing output directories.

Independent bilingual review and dataset publication review have not been completed. Redistribution approval and a release license must be recorded before publication. T01's wrong-color parcel category is disputed; it remains unchanged to preserve pilot evidence. None of these cases constitutes an unseen holdout. Review decisions belong in the release process; the generated case rows carry no review annotations.
