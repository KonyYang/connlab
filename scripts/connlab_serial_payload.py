#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if not sys.path or Path(sys.path[0]).resolve() != SCRIPT_REPOSITORY_ROOT:
    sys.path.insert(0, str(SCRIPT_REPOSITORY_ROOT))

from scripts.connlab_serial_board import BOARD_REL, Blocked, now, parse_board, resolve_primary
from scripts.connlab_serial_complex import ACTION_ROLES, SerialContractError
from scripts.connlab_serial_phase2 import (
    COMMAND_ARGUMENTS,
    build_git_reference,
    build_native_action,
    command_contract,
    prompt_bytes,
)


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description="Build canonical governance JSON from durable facts.")
    commands = value.add_subparsers(dest="command", required=True)
    action = commands.add_parser("native-action")
    action.add_argument("--repo-root", required=True)
    action.add_argument("--action", required=True, choices=tuple(ACTION_ROLES))
    action.add_argument("--prompt-file", required=True)
    action.add_argument("--title", required=True)
    reference = commands.add_parser("git-reference")
    reference.add_argument("--repo-root", required=True)
    reference.add_argument("--path", required=True)
    reference.add_argument("--commit", default="HEAD")
    contract = commands.add_parser("contract")
    contract.add_argument("--command", dest="writer_command", required=True, choices=tuple(COMMAND_ARGUMENTS))
    return value


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        args = parser().parse_args()
        if args.command == "contract":
            print(json.dumps(command_contract(args.writer_command), ensure_ascii=False, separators=(",", ":")))
            return 0
        root = resolve_primary(args.repo_root)
        if args.command == "git-reference":
            print(build_git_reference(root, args.path, args.commit))
            return 0
        _, control, _ = parse_board((root / BOARD_REL).read_bytes())
        active = control.get("active")
        if not isinstance(active, dict):
            raise Blocked("BLOCKED_TASK_MISMATCH", "No durable active task exists.")
        action = build_native_action(active, args.action, prompt_bytes(args.prompt_file), args.title, now())
        print(json.dumps(action, ensure_ascii=False, separators=(",", ":")))
        return 0
    except (Blocked, SerialContractError, OSError) as exc:
        print(json.dumps({"code": getattr(exc, "code", "BLOCKED_ARGUMENT_COMBINATION"), "reason": str(exc)}, ensure_ascii=False, separators=(",", ":")))
        return 2


if __name__ == "__main__":
    sys.exit(main())
