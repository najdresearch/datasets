#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 <historical-evidence-directory> <output-cases.jsonl>" >&2
  exit 2
fi

archive_dir=$1
output=$2
expected=a6dbfcabaaa0eb2945bcd4b0c978afccd3e038e44103cbc017eb7af4cb8fa5a6
command -v zstd >/dev/null || { echo "zstd is required" >&2; exit 2; }
chunks=("$archive_dir"/*.tar.zst.chunk-*)
[[ -f "${chunks[0]}" ]] || { echo "archive chunks not found" >&2; exit 2; }
mkdir -p "$(dirname "$output")"
temporary=$(mktemp "${output}.tmp.XXXXXX")
trap 'rm -f "$temporary"' EXIT
cat "${chunks[@]}" | zstd -dc | tar -xOf - exports/20260906-cleaned-not_reviewed/cases.jsonl > "$temporary"
actual=$(shasum -a 256 "$temporary" | awk '{print $1}')
[[ "$actual" == "$expected" ]] || { echo "input SHA-256 mismatch: $actual" >&2; exit 1; }
mv "$temporary" "$output"
echo "$actual  $output"
