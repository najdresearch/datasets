"""Command-line entry points for Najd dataset preparation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .adapters import reproduce_source
from .historical import reproduce
from .pipeline import PipelineError, clean, collect, generate, validate
from .reference import render_source_catalog
from .release import check_approval, package, publish
from .review import prepare_review
from .snapshot import sync_release


def main() -> None:
    parser = argparse.ArgumentParser(prog="najd-datasets")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in (
        "collect",
        "clean",
        "generate",
        "validate",
        "package",
        "check-approval",
        "publish",
        "reproduce-historical",
        "render-source-reference",
        "reproduce-source",
        "prepare-review",
        "sync-release",
    ):
        cmd = commands.add_parser(name)
        if name == "clean":
            cmd.add_argument("inputs", nargs="+", type=Path)
        else:
            cmd.add_argument("input", type=Path)
        if name in {
            "collect", "clean", "generate", "package",
            "reproduce-historical", "render-source-reference",
            "reproduce-source",
            "prepare-review",
            "sync-release",
        }:
            cmd.add_argument("--output", required=True, type=Path)
        if name == "reproduce-source":
            cmd.add_argument("--reference", type=Path)
        if name == "prepare-review":
            cmd.add_argument("--per-category", type=int, default=2)
        if name == "package":
            cmd.add_argument("--id", required=True)
            cmd.add_argument("--version", required=True)
        if name in {"check-approval", "publish"}:
            cmd.add_argument("--approval", required=True, type=Path)
            cmd.add_argument("--repo", required=True)
    args = parser.parse_args()
    try:
        if args.command == "collect":
            result = collect(args.input, args.output)
        elif args.command == "clean":
            result = clean(args.inputs, args.output)
        elif args.command == "generate":
            result = generate(args.input, args.output)
        elif args.command == "validate":
            result = validate(args.input)
        elif args.command == "reproduce-historical":
            result = reproduce(args.input, args.output)
        elif args.command == "render-source-reference":
            result = render_source_catalog(args.input, args.output)
        elif args.command == "reproduce-source":
            result = reproduce_source(args.input, args.output, args.reference)
        elif args.command == "prepare-review":
            result = prepare_review(args.input, args.output, args.per_category)
        elif args.command == "sync-release":
            result = sync_release(args.input, args.output)
        elif args.command == "package":
            result = package(args.input, args.output, args.id, args.version)
        elif args.command == "check-approval":
            result = check_approval(args.input, args.approval, args.repo)
        else:
            result = {"commit": publish(args.input, args.approval, args.repo)}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if args.command == "validate" and not result["passed"]:
            raise SystemExit(1)
    except (PipelineError, FileNotFoundError, json.JSONDecodeError) as exc:
        parser.exit(1, f"error: {exc}\n")


if __name__ == "__main__":
    main()
