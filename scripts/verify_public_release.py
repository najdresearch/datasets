"""Compare a completed reconstruction with the published target, after building."""

import argparse
import hashlib
import json
from pathlib import Path

from audit_public_reconstruction import BENCHMARK_REVISION, fetch


def verify(output):
    import pyarrow.parquet as pq

    checks = json.loads((output / "release/checksums.json").read_text())["files"]
    records = {}
    for name, digest in checks.items():
        actual = output / "release" / name
        if hashlib.sha256(actual.read_bytes()).hexdigest() != digest:
            raise ValueError(f"Local artifact modified: {name}")
        reference = output / "verification-reference" / name
        data = fetch(
            "najd-benchmark",
            BENCHMARK_REVISION,
            "datasets/najd-benchmark/2026.09.14/" + name,
            reference,
        )
        exact = hashlib.sha256(data).hexdigest() == digest
        equal = exact or (
            name.endswith(".parquet") and pq.read_table(actual).equals(pq.read_table(reference))
        )
        if not equal:
            raise ValueError(f"Published artifact differs: {name}")
        records[name] = {"byte_identical": exact, "content_equal": equal}
    (output / "verification.json").write_text(json.dumps(records, indent=2) + "\n")
    return records


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    print(json.dumps(verify(parser.parse_args().output), indent=2))
