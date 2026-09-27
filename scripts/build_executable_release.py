"""Build the next release with sourced answer corrections and verified public fixtures."""
import argparse
import csv
import hashlib
import io
import json
import shutil
import urllib.request
from pathlib import Path

from reconstruct_public_release import export_parquet, write_rows

VERSION = '2026.09.27.1'
BASE_SHA = '8b8bcbee213726333292976a0efa5152bfba8b003a84137244db7879767bb8ae'


def build(source, historical, output, root):
    import pyarrow.parquet as pq

    if output.exists():
        raise ValueError('Use a new output directory')
    if hashlib.sha256((source / 'cases.jsonl').read_bytes()).hexdigest() != BASE_SHA:
        raise ValueError('Wrong base release')
    records = [json.loads(line) for line in (source / 'cases.jsonl').read_text().splitlines()]
    changes = json.loads((root / f'releases/answer-corrections-{VERSION}.json').read_text())
    by_id = {r['id']: r for r in records}
    for change in changes:
        with urllib.request.urlopen(change['source_url'], timeout=60) as response:
            raw = response.read()
        if hashlib.sha256(raw).hexdigest() != change['source_sha256']:
            raise ValueError('Source checksum mismatch')
        source_row = list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))[
            change['csv_record_index']]
        if (source_row['Term'] != change['term']
                or source_row['Meaning_of_term'] != change['meaning']
                or source_row['correct_answer'] != change['original_correct_answer']):
            raise ValueError('Source evidence differs')
        row = by_id[change['id']]
        if row['prompt'] != change['original_prompt'] or row['expected'] != {'answer': None}:
            raise ValueError('Unexpected correction input')
        row['prompt'] = change.get('prompt', row['prompt'])
        row['expected'] = {'answer': change['answer']}
        row['audit_issues'] = [x for x in row['audit_issues'] if x != 'missing_expected_answer']
        row['answer_recovery_status'] = 'source_based_annotation'
        row['answer_recovery_evidence'] = change
        row['provenance']['correction_version'] = VERSION
    output.mkdir(parents=True)
    write_rows(output / 'cases.jsonl', records)
    export_parquet(records, output / 'viewer.parquet')
    pq.write_table(pq.read_table(output / 'viewer.parquet').drop(['audit_status']),
                   output / 'viewer.parquet')
    # Fixture bytes are pinned in the public legacy release reconstruction manifest.
    manifest_path = historical.parent / 'inputs/najd-legacy-31/manifest.json'
    manifest_sha = '03018d10e0212f03131c664914007d0ceda764e9444549c22b7bdf6c74ae6df1'
    if hashlib.sha256(manifest_path.read_bytes()).hexdigest() != manifest_sha:
        raise ValueError('Legacy fixture manifest differs from pinned public input')
    fixture_manifest = json.loads(manifest_path.read_text())
    # The reconstruction already verifies these against the immutable HF revision.
    fixture_checks = fixture_manifest['files']
    for name, digest in fixture_checks.items():
        if name.startswith('fixtures/'):
            data = (historical / name).read_bytes()
            if hashlib.sha256(data).hexdigest() != digest:
                raise ValueError(f'Fixture checksum mismatch: {name}')
            target = output / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    for name in ('manifest.json', 'case.schema.json', 'suite.json', 'sources.json'):
        value = json.loads((source / name).read_text())
        if name != 'sources.json':
            if 'version' in value:
                value['version'] = VERSION
            if '$id' in value:
                value['$id'] = value['$id'].replace('2026.09.27/', VERSION + '/')
        if name == 'manifest.json':
            value['transformation'] = (
                'Four source-based answer corrections; public fixtures included.')
            value['input_revision'] = 'e2dcd2aac116da180835ce9eacc7572bc7cec2f7'
            value['fixture_protocol'] = 'fixture-tools-v1'
        (output / name).write_text(json.dumps(value, ensure_ascii=False, indent=2,
                                            sort_keys=True) + '\n')
    shutil.copyfile(root / f'releases/answer-corrections-{VERSION}.json',
                    output / 'answer-corrections.json')
    checks = {str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(output.rglob('*')) if p.is_file()}
    (output / 'checksums.json').write_text(json.dumps({'algorithm': 'sha256', 'files': checks},
                                                     indent=2, sort_keys=True) + '\n')
    return checks


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'historical', 'output'):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.source, args.historical, args.output,
                           Path(__file__).resolve().parents[1]), indent=2))
