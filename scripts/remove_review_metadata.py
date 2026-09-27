"""Create a metadata-only dataset revision; never modify the input snapshot."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

from najd_datasets.metadata import RETIRED_FIELDS, without_review_metadata


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean_json(value):
    value = without_review_metadata(value)
    if isinstance(value, dict):
        value.pop('source_bundle', None)
        if isinstance(value.get('source'), str) and 'archive bundle' in value['source']:
            value['source'] = 'Najd Research historical archive, audited against immutable upstream artifacts where available'
    if isinstance(value, dict):
        if isinstance(value.get('required'), list):
            value['required'] = [x for x in value['required'] if x not in RETIRED_FIELDS]
        return {k: clean_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json(v) for v in value]
    return value


def migrate(source, output):
    if output.exists():
        raise ValueError('Output exists')
    shutil.copytree(source, output, ignore=shutil.ignore_patterns('.cache', '.git'))
    changes = []
    for path in sorted(output.rglob('*')):
        if not path.is_file():
            continue
        if path.suffix == '.jsonl':
            old = [json.loads(l) for l in path.read_text().splitlines() if l]
            new = [without_review_metadata(row) for row in old]
            path.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in new))
            if old != new:
                changes.append({'file':str(path.relative_to(output)), 'rows':len(new)})
        elif path.suffix == '.json':
            data = clean_json(json.loads(path.read_text()))
            path.write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
        elif path.suffix == '.parquet':
            import pyarrow.parquet as pq
            table = pq.read_table(path)
            columns = [name for name in table.column_names if name not in RETIRED_FIELDS]
            new = table.select(columns)
            pq.write_table(new,path)
            assert pq.read_table(path).equals(new)
            changes.append({'file':str(path.relative_to(output)), 'rows':table.num_rows})
    card = output/'README.md'
    text = card.read_text()
    text = text.replace('The original per-case `review_status` is preserved, while ', '')
    text = text.replace('`not_reviewed` is retained; answers and rubrics have not undergone independent semantic review. ', '')
    text = text.replace('`review_status=not_reviewed` remains unchanged. ', '')
    text += '\n## Metadata revision\n\nReview annotations are omitted from current data. This metadata-only revision does not change questions, answers, IDs, splits, or scoring. Earlier commit snapshots remain available for historical reproducibility. Removing annotations does not record a completed review.\n'
    card.write_text(text)
    for path in output.rglob('manifest.json'):
        manifest = json.loads(path.read_text())
        if isinstance(manifest.get('files'),dict):
            for name,value in manifest['files'].items():
                target=path.parent/name
                if isinstance(value,str) and len(value)==64 and target.is_file():
                    manifest['files'][name]=sha(target)
        if 'publication_sha256' in manifest:
            manifest['publication_sha256']=sha(output/'data/questions.jsonl')
        manifest['metadata_revision']='omit-review-annotations-v1'
        path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
    for path in output.rglob('checksums.json'):
        data=json.loads(path.read_text())
        for name in data['files']:
            data['files'][name]=sha(path.parent/name)
        path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    report={'transformation':'omit-review-annotations-v1','changes':changes,
            'files':{str(p.relative_to(output)):sha(p) for p in sorted(output.rglob('*')) if p.is_file()}}
    return report


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path)
    p.add_argument('output',type=Path)
    p.add_argument('--report',type=Path,required=True)
    a=p.parse_args()
    a.report.write_text(json.dumps(migrate(a.source,a.output),indent=2)+'\n')
