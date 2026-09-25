"""Prepare a release folder and require explicit review before upload."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from .pipeline import PipelineError, digest, read_json, validate, write_json


def package(cases_path: Path, output: Path, dataset_id: str, version: str) -> dict:
    if not all(
        re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]*", value) for value in (dataset_id, version)
    ):
        raise PipelineError("dataset ID and version must be safe path components")
    if output.exists():
        raise PipelineError("release folder already exists; versions are immutable")
    result = validate(cases_path)
    if not result["passed"]:
        raise PipelineError("dataset validation failed: " + "; ".join(result["failures"]))
    source_manifest = cases_path.with_suffix(".manifest.json")
    if not source_manifest.exists():
        raise PipelineError("input manifest missing")
    output.mkdir(parents=True)
    shutil.copyfile(cases_path, output / "cases.jsonl")
    shutil.copyfile(source_manifest, output / "build-manifest.json")
    manifest = {
        "id": dataset_id,
        "version": version,
        "status": "candidate",
        "case_count": result["rows"],
        "cases_sha256": result["sha256"],
        "build_manifest_sha256": digest((output / "build-manifest.json").read_bytes()),
        "tracks": result["tracks"],
        "semantic_review": "not_performed",
    }
    write_json(output / "manifest.json", manifest)
    (output / "README.md").write_text(
        f"---\nlanguage:\n- ar\n- en\nlicense: other\n---\n\n# {dataset_id} {version}\n\n"
        "Candidate data from Najd Research. Structural checks alone do not establish "
        "answer correctness. "
        "Read `manifest.json` and `build-manifest.json` for provenance. "
        "No public benchmark claim should be made until independent semantic review is complete.\n",
        encoding="utf-8",
    )
    return manifest


def check_approval(folder: Path, approval_path: Path, repo_id: str) -> dict:
    manifest = read_json(folder / "manifest.json")
    build = read_json(folder / "build-manifest.json")
    rights = [item["source"]["rights_status"] for item in build.get("sources", [])]
    if "generation_spec" in build:
        rights.append(build["generation_spec"]["rights_status"])
    if not rights or any(status != "approved" for status in rights):
        raise PipelineError(
            "all source or generation rights must be approved in the build manifest"
        )
    approval = read_json(approval_path)
    required = (
        "reviewer",
        "reviewed_at",
        "rights_approved",
        "privacy_approved",
        "semantic_review_approved",
        "target_repo",
        "dataset_id",
        "version",
        "cases_sha256",
    )
    if any(approval.get(key) in (None, "") for key in required):
        raise PipelineError("approval missing required fields")
    if not all(
        approval[key] is True
        for key in ("rights_approved", "privacy_approved", "semantic_review_approved")
    ):
        raise PipelineError("rights, privacy, and semantic review must be approved")
    if (
        approval["target_repo"] != repo_id
        or approval["dataset_id"] != manifest["id"]
        or approval["version"] != manifest["version"]
        or approval["cases_sha256"] != manifest["cases_sha256"]
    ):
        raise PipelineError("approval target or dataset hash mismatch")
    if manifest["cases_sha256"] != digest((folder / "cases.jsonl").read_bytes()):
        raise PipelineError("release cases changed after packaging")
    if manifest["build_manifest_sha256"] != digest((folder / "build-manifest.json").read_bytes()):
        raise PipelineError("build manifest changed after packaging")
    return manifest


def publish(folder: Path, approval_path: Path, repo_id: str) -> str:
    manifest = check_approval(folder, approval_path, repo_id)
    from huggingface_hub import HfApi

    api = HfApi()
    api.repo_info(repo_id=repo_id, repo_type="dataset")
    prefix = f"datasets/{manifest['id']}/{manifest['version']}"
    existing = api.list_repo_files(repo_id=repo_id, repo_type="dataset")
    if any(path == prefix or path.startswith(prefix + "/") for path in existing):
        raise PipelineError("target version already exists; refusing overwrite")
    result = api.upload_folder(
        folder_path=str(folder),
        repo_id=repo_id,
        repo_type="dataset",
        path_in_repo=prefix,
        commit_message=f"Add reviewed {manifest['id']} {manifest['version']}",
    )
    return str(result)
