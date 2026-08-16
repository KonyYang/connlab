#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path, PurePosixPath
from typing import Any


ROLES = {"Developer", "Reviewer", "QA", "Integrator"}
KINDS = {"targeted", "full", "ui", "static"}
PERMISSIONS = {"workspace", "pytest_temp", "browser"}
CHECK_KEYS = {
    "id", "kind", "run_for", "cwd", "argv", "timeout_seconds", "permission", "required",
}


class ManifestError(ValueError):
    pass


def _fail(reason: str) -> None:
    raise ManifestError(reason)


def validate_manifest(value: Any, *, task_id: str | None = None) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {"schema", "version", "task_id", "checks"}:
        _fail("Validation manifest keys are invalid.")
    if value.get("schema") != "connlab.validation-manifest" or value.get("version") != 1:
        _fail("Validation manifest identity is invalid.")
    if not isinstance(value.get("task_id"), str) or not value["task_id"].strip():
        _fail("Validation manifest task_id is required.")
    if task_id is not None and value["task_id"] != task_id:
        _fail("Validation manifest task_id differs from the active task.")
    checks = value.get("checks")
    if not isinstance(checks, list) or not checks:
        _fail("Validation manifest checks are required.")
    seen: set[str] = set()
    for check in checks:
        if not isinstance(check, dict) or set(check) != CHECK_KEYS:
            _fail("Validation check keys are invalid.")
        check_id = check.get("id")
        if not isinstance(check_id, str) or not check_id.strip() or check_id in seen:
            _fail("Validation check id is empty or duplicated.")
        seen.add(check_id)
        if check.get("kind") not in KINDS or check.get("permission") not in PERMISSIONS:
            _fail(f"Validation check kind or permission is invalid: {check_id}.")
        roles = check.get("run_for")
        if not isinstance(roles, list) or not roles or len(set(roles)) != len(roles) or any(role not in ROLES for role in roles):
            _fail(f"Validation check run_for is invalid: {check_id}.")
        cwd = check.get("cwd")
        path = PurePosixPath(cwd) if isinstance(cwd, str) and cwd else None
        if path is None or path.is_absolute() or ".." in path.parts or ":" in cwd or "\\" in cwd:
            _fail(f"Validation check cwd must stay inside the repository: {check_id}.")
        argv = check.get("argv")
        if (
            not isinstance(argv, list)
            or not argv
            or any(not isinstance(item, str) or not item for item in argv)
            or (len(argv) == 1 and any(char.isspace() for char in argv[0]))
        ):
            _fail(f"Validation check argv must be an argument array, not a shell string: {check_id}.")
        timeout = check.get("timeout_seconds")
        if type(timeout) is not int or not 1 <= timeout <= 3600 or type(check.get("required")) is not bool:
            _fail(f"Validation check timeout or required flag is invalid: {check_id}.")
    return value


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args], text=True, encoding="utf-8",
        capture_output=True, check=False, shell=False,
    )
    if result.returncode != 0:
        _fail(f"Git fact cannot be read: {' '.join(args)}.")
    return result.stdout.strip()


def manifest_from_board(
    authority_root: Path,
) -> tuple[dict[str, Any], dict[str, str], dict[str, Any]]:
    authority_root = authority_root.resolve()
    board_bytes = (authority_root / "docs/task_board.md").read_bytes()
    from scripts.connlab_serial_board import parse_board

    _, control, _ = parse_board(board_bytes)
    active = control.get("active")
    context = active.get("complex_context") if isinstance(active, dict) else None
    if not isinstance(context, dict) or "validation_manifest" not in context:
        _fail("Active task has no structured validation manifest.")
    manifest = validate_manifest(context["validation_manifest"], task_id=active["task_id"])
    task_worktree = context.get("task_worktree")
    current_role = context.get("current_role")
    current_attempt = context.get("current_attempt")
    recorded_subject = context.get("head_sha")
    if not isinstance(task_worktree, str) or not task_worktree.strip():
        _fail("Active task has no recorded task worktree.")
    if current_role not in ROLES:
        _fail("Active task has no valid current validation role.")
    if type(current_attempt) is not int or current_attempt < 1:
        _fail("Active task has no valid current validation attempt.")
    if not isinstance(recorded_subject, str) or not recorded_subject.strip():
        _fail("Active task has no recorded subject.")
    if _git(authority_root, "status", "--porcelain=v1", "--untracked-files=all"):
        _fail("Authority worktree must be clean before validation.")
    canonical_manifest = json.dumps(
        manifest, ensure_ascii=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")
    authority = {
        "root": str(authority_root),
        "head": _git(authority_root, "rev-parse", "HEAD"),
        "board_sha256": hashlib.sha256(board_bytes).hexdigest(),
        "manifest_sha256": hashlib.sha256(canonical_manifest).hexdigest(),
    }
    binding = {
        "task_id": active["task_id"],
        "role": current_role,
        "attempt": current_attempt,
        "repo_root": str(Path(task_worktree).resolve()),
        "recorded_subject": recorded_subject,
    }
    return manifest, authority, binding


def run_manifest(
    root: Path,
    manifest: dict[str, Any],
    *,
    role: str,
    allowed_permissions: set[str],
    check_ids: set[str] | None = None,
    authority: dict[str, str] | None = None,
    binding: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    validate_manifest(manifest)
    if role not in ROLES:
        _fail("Validation role is invalid.")
    if binding is not None:
        if binding.get("task_id") != manifest["task_id"] or binding.get("role") != role:
            _fail("Validation binding differs from the requested task or role.")
        bound_root = binding.get("repo_root")
        if not isinstance(bound_root, str) or not bound_root or Path(bound_root).resolve() != root:
            _fail("Validation binding differs from the requested repository root.")
        if not isinstance(binding.get("recorded_subject"), str) or not binding["recorded_subject"]:
            _fail("Validation binding has no recorded subject.")
    if allowed_permissions - PERMISSIONS:
        _fail("Unknown validation permission was supplied.")
    allowed_permissions = set(allowed_permissions) | {"workspace"}
    selected = [
        check for check in manifest["checks"]
        if role in check["run_for"] and (check_ids is None or check["id"] in check_ids)
    ]
    if check_ids is not None and check_ids - {check["id"] for check in selected}:
        _fail("Requested check id is absent or not approved for this role.")
    missing = sorted({check["permission"] for check in selected} - allowed_permissions)
    subject_before = _git(root, "rev-parse", "HEAD")
    dirty_before = _git(root, "status", "--porcelain=v1", "--untracked-files=all").splitlines()
    base = {
        "schema": "connlab.validation-result",
        "version": 1,
        "task_id": manifest["task_id"],
        "role": role,
        "subject_before": subject_before,
    }
    if authority is not None:
        base["authority"] = authority
    if binding is not None:
        base["binding"] = binding
    if binding is not None and role != "Developer" and binding["recorded_subject"] != subject_before:
        return {
            **base, "status": "blocked", "code": "BLOCKED_SUBJECT_MISMATCH",
            "required_permissions": [], "checks": [],
        }
    if dirty_before:
        return {**base, "status": "blocked", "code": "BLOCKED_DIRTY_WORKTREE", "required_permissions": [], "checks": []}
    if missing:
        return {**base, "status": "blocked", "code": "BLOCKED_PERMISSION_REQUIRED", "required_permissions": missing, "checks": []}
    results: list[dict[str, Any]] = []
    suite_started = time.monotonic()
    for check in selected:
        cwd = (root / PurePosixPath(check["cwd"])).resolve()
        try:
            cwd.relative_to(root)
        except ValueError as exc:
            raise ManifestError(f"Validation cwd escaped the repository: {check['id']}.") from exc
        started = time.monotonic()
        try:
            completed = subprocess.run(
                check["argv"], cwd=cwd, capture_output=True, check=False,
                timeout=check["timeout_seconds"], shell=False,
            )
            exit_code = completed.returncode
            stdout, stderr = completed.stdout, completed.stderr
            status = "passed" if exit_code == 0 else "failed"
        except subprocess.TimeoutExpired as exc:
            exit_code = None
            stdout, stderr = exc.stdout or b"", exc.stderr or b""
            status = "timed_out"
        results.append({
            "id": check["id"],
            "kind": check["kind"],
            "argv": check["argv"],
            "status": status,
            "exit_code": exit_code,
            "duration_ms": round((time.monotonic() - started) * 1000),
            "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
            "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
        })
        if check["required"] and status != "passed":
            break
    subject_after = _git(root, "rev-parse", "HEAD")
    dirty_after = _git(root, "status", "--porcelain=v1", "--untracked-files=all").splitlines()
    if subject_after != subject_before or dirty_after:
        return {
            **base, "status": "blocked", "code": "BLOCKED_VALIDATION_STATE_CHANGED",
            "subject_after": subject_after, "duration_ms": round((time.monotonic() - suite_started) * 1000),
            "required_permissions": [], "checks": results,
        }
    passed = all(item["status"] == "passed" for item in results)
    return {
        **base, "status": "passed" if passed else "failed",
        "code": "ALLOW_VALIDATION" if passed else "BLOCKED_VALIDATION_FAILED",
        "subject_after": subject_after,
        "duration_ms": round((time.monotonic() - suite_started) * 1000),
        "required_permissions": [],
        "checks": results,
    }


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    value.add_argument("command", choices=("validate", "run"))
    source = value.add_mutually_exclusive_group(required=True)
    source.add_argument("--manifest")
    source.add_argument("--from-board", action="store_true")
    value.add_argument("--authority-root")
    value.add_argument("--repo-root")
    value.add_argument("--role", choices=sorted(ROLES))
    value.add_argument("--allow-permission", action="append", default=[])
    value.add_argument("--check-id", action="append")
    return value


def main() -> int:
    args = parser().parse_args()
    try:
        authority = None
        binding = None
        if args.authority_root and not args.from_board:
            _fail("--authority-root is valid only with --from-board.")
        if args.from_board:
            authority_root = args.authority_root or args.repo_root
            if not authority_root:
                _fail("--from-board requires --authority-root or --repo-root.")
            manifest, authority, binding = manifest_from_board(Path(authority_root))
        else:
            manifest = validate_manifest(json.loads(Path(args.manifest).read_text(encoding="utf-8")))
        if args.command == "validate":
            result = {"schema": "connlab.validation-manifest-result", "version": 1, "status": "valid"}
            if authority is not None:
                result["authority"] = authority
        else:
            if not args.role:
                _fail("run requires --role.")
            if binding is not None and args.role != binding["role"]:
                _fail("Requested role differs from the active board role.")
            recorded_root = Path(binding["repo_root"]) if binding is not None else None
            requested_root = Path(args.repo_root).resolve() if args.repo_root else None
            if requested_root is not None and recorded_root is not None and requested_root != recorded_root:
                _fail("Requested repository root differs from the recorded task worktree.")
            repo_root = requested_root or recorded_root
            if repo_root is None:
                _fail("run requires --repo-root when no task worktree is available from the board.")
            result = run_manifest(
                repo_root, manifest, role=args.role,
                allowed_permissions=set(args.allow_permission),
                check_ids=set(args.check_id) if args.check_id else None,
                authority=authority,
                binding=binding,
            )
    except (ManifestError, OSError, json.JSONDecodeError) as exc:
        result = {"schema": "connlab.validation-result", "version": 1, "status": "blocked", "code": "BLOCKED_MANIFEST_INVALID", "reason": str(exc)}
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    return 0 if result.get("status") in {"valid", "passed"} else 2


if __name__ == "__main__":
    sys.exit(main())
