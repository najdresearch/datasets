import hashlib
import importlib.util
import json
from pathlib import Path

from jsonschema import Draft7Validator, FormatChecker

ROOT = Path(__file__).parents[1]


def test_example_rebuilds_and_validates(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "support_generator", ROOT / "scripts/generate_support_contract_example.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.generate(tmp_path)
    for name in ("cases.jsonl", "dataset-manifest.json", "task-pack.json"):
        assert (tmp_path / name).read_bytes() == (
            ROOT / "examples/arabic-support-routing-v1" / name
        ).read_bytes()
    manifest = json.loads((tmp_path / "dataset-manifest.json").read_text())
    pack = json.loads((tmp_path / "task-pack.json").read_text())
    for name, value in [("dataset-manifest", manifest), ("task-pack", pack)]:
        schema = json.loads((ROOT / "contracts/v1" / (name + ".schema.json")).read_text())
        Draft7Validator(schema, format_checker=FormatChecker()).validate(value)
    raw = (tmp_path / "cases.jsonl").read_bytes()
    cases = [json.loads(line) for line in raw.decode().splitlines()]
    assert hashlib.sha256(raw).hexdigest() == manifest["cases"]["sha256"]
    assert [c["id"] for c in cases] == manifest["case_ids"]
    assert len(cases) == manifest["cases"]["count"] == 8
    assert sum(c["label"] == "billing" for c in cases) / len(cases) == 0.25
    assert pack["dataset"]["cases_sha256"] == manifest["cases"]["sha256"]
