from __future__ import annotations

import argparse
import re
import shutil
from dataclasses import dataclass
from datetime import date
from pathlib import Path


TASK_ID_PATTERN = re.compile(r"^TASK_\d+[A-Z]*$")
ARCHIVED_STATUS_PATTERN = re.compile(r"\b(complete|completed|done|corrected|accepted)\b", re.IGNORECASE)
OPEN_STATUS_PATTERN = re.compile(r"\b(planned|proposed|pending|awaiting|paused)\b", re.IGNORECASE)


@dataclass(frozen=True)
class ArchiveMove:
    source: Path
    destination: Path
    kind: str


@dataclass(frozen=True)
class ArchivePlan:
    repo_root: Path
    task_id: str
    year: str
    moves: tuple[ArchiveMove, ...]
    task_files: tuple[Path, ...]
    plan_files: tuple[Path, ...]


class ArchiveError(RuntimeError):
    pass


def normalize_task_id(raw_task_id: str) -> str:
    task_id = raw_task_id.strip().upper()
    if not TASK_ID_PATTERN.match(task_id):
        raise ArchiveError(f"Invalid task id: {raw_task_id!r}. Expected TASK_XXX.")
    return task_id


def relative_posix(repo_root: Path, path: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def read_task_board(repo_root: Path) -> str:
    board_path = repo_root / "docs" / "task_board.md"
    if not board_path.exists():
        raise ArchiveError("docs/task_board.md was not found.")
    return board_path.read_text(encoding="utf-8")


def task_has_completed_board_status(board_text: str, task_id: str) -> bool:
    status_pattern = re.compile(rf"\b{re.escape(task_id)}(?:_|\b)[^\n]*", re.IGNORECASE)
    return any(ARCHIVED_STATUS_PATTERN.search(match.group(0)) for match in status_pattern.finditer(board_text))


def assert_task_is_not_active(board_text: str, task_id: str) -> None:
    active_match = re.search(r"^>\s*Current Active Task:\s*(.+)$", board_text, re.MULTILINE)
    active_text = active_match.group(1).strip() if active_match else ""
    active_task_pattern = re.compile(rf"\b{re.escape(task_id)}(?:_|\b)", re.IGNORECASE)
    if active_task_pattern.search(active_text) and "complete" not in active_text.lower():
        raise ArchiveError(f"{task_id} is still the current active task.")


def assert_task_is_archivable(board_text: str, task_id: str) -> None:
    assert_task_is_not_active(board_text, task_id)

    if not task_has_completed_board_status(board_text, task_id):
        raise ArchiveError(f"{task_id} is not marked complete in docs/task_board.md.")


def file_has_completed_status(path: Path) -> bool:
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines[:40]):
        if "status" not in line.lower():
            continue
        status_window = " ".join(lines[index : index + 4])
        if OPEN_STATUS_PATTERN.search(status_window):
            return False
        if ARCHIVED_STATUS_PATTERN.search(status_window):
            return True
    return False


def task_files_have_completed_status(task_files: tuple[Path, ...]) -> bool:
    return bool(task_files) and all(file_has_completed_status(path) for path in task_files)


def collect_candidates(repo_root: Path, task_id: str) -> tuple[tuple[Path, ...], tuple[Path, ...]]:
    task_file_pattern = re.compile(rf"^{re.escape(task_id)}(?:_|\.md$)", re.IGNORECASE)
    plan_file_pattern = re.compile(rf"^{re.escape(task_id.lower())}(?:_).*_plan\.md$", re.IGNORECASE)
    task_files = tuple(
        sorted(
            path
            for path in (repo_root / "tasks").glob("*.md")
            if task_file_pattern.match(path.name)
            and path.suffix.lower() == ".md"
            if "completed" not in path.relative_to(repo_root).parts
        )
    )
    plan_files = tuple(
        sorted(
            path
            for path in (repo_root / "docs").glob("*.md")
            if plan_file_pattern.match(path.name)
            if "completed_plans" not in path.relative_to(repo_root).parts
        )
    )
    return task_files, plan_files


def discover_root_task_ids(repo_root: Path) -> tuple[str, ...]:
    task_ids: set[str] = set()
    for path in (repo_root / "tasks").glob("TASK_*.md"):
        match = re.match(r"^(TASK_\d+[A-Z]*)_", path.name, re.IGNORECASE)
        if match:
            task_ids.add(match.group(1).upper())
    for path in (repo_root / "docs").glob("task_*_plan.md"):
        match = re.match(r"^(task_\d+[a-z]*)_", path.name, re.IGNORECASE)
        if match:
            task_ids.add(match.group(1).upper())
    return tuple(sorted(task_ids, key=task_sort_key))


def task_sort_key(task_id: str) -> tuple[int, str]:
    match = re.match(r"^TASK_(\d+)([A-Z]*)$", task_id)
    if not match:
        return (999999, task_id)
    return (int(match.group(1)), match.group(2))


def build_all_completed_archive_plans(repo_root: Path, year: str | None = None) -> tuple[ArchivePlan, ...]:
    resolved_root = repo_root.resolve()
    board_text = read_task_board(resolved_root)
    plans: list[ArchivePlan] = []
    for task_id in discover_root_task_ids(resolved_root):
        task_files, _ = collect_candidates(resolved_root, task_id)
        if not task_has_completed_board_status(board_text, task_id) and not task_files_have_completed_status(task_files):
            continue
        try:
            plans.append(build_archive_plan(resolved_root, task_id, year))
        except ArchiveError as exc:
            if "No task or plan files found" in str(exc):
                continue
            raise
    return tuple(plans)


def build_archive_plan(repo_root: Path, raw_task_id: str, year: str | None = None) -> ArchivePlan:
    resolved_root = repo_root.resolve()
    task_id = normalize_task_id(raw_task_id)
    board_text = read_task_board(resolved_root)
    assert_task_is_not_active(board_text, task_id)

    archive_year = year or str(date.today().year)
    task_files, plan_files = collect_candidates(resolved_root, task_id)
    if not task_files and not plan_files:
        raise ArchiveError(f"No task or plan files found for {task_id}.")
    if not task_has_completed_board_status(board_text, task_id) and not task_files_have_completed_status(task_files):
        raise ArchiveError(f"{task_id} is not marked complete in docs/task_board.md or its task file.")

    moves: list[ArchiveMove] = []
    for source in task_files:
        moves.append(
            ArchiveMove(
                source=source,
                destination=resolved_root / "tasks" / "completed" / archive_year / source.name,
                kind="task",
            )
        )
    for source in plan_files:
        moves.append(
            ArchiveMove(
                source=source,
                destination=resolved_root / "docs" / "completed_plans" / archive_year / source.name,
                kind="plan",
            )
        )

    for move in moves:
        if move.destination.exists():
            raise ArchiveError(f"Archive destination already exists: {relative_posix(resolved_root, move.destination)}")

    return ArchivePlan(
        repo_root=resolved_root,
        task_id=task_id,
        year=archive_year,
        moves=tuple(moves),
        task_files=task_files,
        plan_files=plan_files,
    )


def infer_title(task_file: Path | None, task_id: str) -> str:
    if task_file and task_file.exists():
        for line in task_file.read_text(encoding="utf-8").splitlines():
            stripped = line.strip("# ").strip()
            if stripped.startswith(task_id):
                return stripped
    return task_id


def ensure_index(path: Path, title: str, header: str) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {title}\n\n{header}\n", encoding="utf-8")


def append_unique_line(path: Path, line: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if line in text:
        return
    if text and not text.endswith("\n"):
        text += "\n"
    path.write_text(text + line + "\n", encoding="utf-8")


def update_indexes(plan: ArchivePlan, archived_on: str | None = None) -> None:
    archived_date = archived_on or date.today().isoformat()
    task_index = plan.repo_root / "docs" / "task_archive_index.md"
    plan_index = plan.repo_root / "docs" / "plan_archive_index.md"
    ensure_index(
        task_index,
        "Task Archive Index",
        "| Task ID | Title | Status | Archived Task File | Archived Plan File | Archived On |\n| --- | --- | --- | --- | --- | --- |",
    )
    ensure_index(
        plan_index,
        "Plan Archive Index",
        "| Task ID | Plan File | Archived Path | Related Task File | Archived On |\n| --- | --- | --- | --- | --- |",
    )

    archived_task_paths = [move.destination for move in plan.moves if move.kind == "task"]
    archived_plan_paths = [move.destination for move in plan.moves if move.kind == "plan"]
    first_task = archived_task_paths[0] if archived_task_paths else None
    first_plan = archived_plan_paths[0] if archived_plan_paths else None
    title = infer_title(first_task, plan.task_id)

    task_line = (
        f"| {plan.task_id} | {title} | complete | "
        f"{relative_posix(plan.repo_root, first_task) if first_task else ''} | "
        f"{relative_posix(plan.repo_root, first_plan) if first_plan else ''} | {archived_date} |"
    )
    append_unique_line(task_index, task_line)

    related_task = relative_posix(plan.repo_root, first_task) if first_task else ""
    for archived_plan in archived_plan_paths:
        plan_line = (
            f"| {plan.task_id} | {archived_plan.name} | "
            f"{relative_posix(plan.repo_root, archived_plan)} | {related_task} | {archived_date} |"
        )
        append_unique_line(plan_index, plan_line)


def render_plan(plan: ArchivePlan, dry_run: bool) -> str:
    mode = "DRY RUN" if dry_run else "APPLY"
    lines = [f"{mode}: archive {plan.task_id}", ""]
    for move in plan.moves:
        lines.append(
            f"MOVE {relative_posix(plan.repo_root, move.source)} -> "
            f"{relative_posix(plan.repo_root, move.destination)}"
        )
    lines.extend(["", "UPDATE docs/task_archive_index.md", "UPDATE docs/plan_archive_index.md"])
    return "\n".join(lines)


def render_plans(plans: tuple[ArchivePlan, ...], dry_run: bool) -> str:
    mode = "DRY RUN" if dry_run else "APPLY"
    move_count = sum(len(plan.moves) for plan in plans)
    lines = [f"{mode}: archive all completed root task Markdown", f"Tasks: {len(plans)}", f"Moves: {move_count}", ""]
    for plan in plans:
        lines.append(render_plan(plan, dry_run=dry_run))
        lines.append("")
    return "\n".join(lines).rstrip()


def apply_archive_plan(plan: ArchivePlan) -> None:
    for move in plan.moves:
        move.destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(move.source), str(move.destination))
    update_indexes(plan)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Archive completed ConnLab task Markdown files.")
    task_group = parser.add_mutually_exclusive_group(required=True)
    task_group.add_argument("--task", help="Task id, for example TASK_267.")
    task_group.add_argument("--all-completed", action="store_true", help="Archive all completed root task Markdown files.")
    parser.add_argument("--repo-root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--year", default=None, help="Archive year folder. Defaults to current year.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Print planned moves without changing files.")
    mode.add_argument("--apply", action="store_true", help="Move files and update archive indexes.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.all_completed:
            plans = build_all_completed_archive_plans(Path(args.repo_root), args.year)
            print(render_plans(plans, dry_run=args.dry_run))
            if args.apply:
                for plan in plans:
                    apply_archive_plan(plan)
        else:
            plan = build_archive_plan(Path(args.repo_root), args.task, args.year)
            print(render_plan(plan, dry_run=args.dry_run))
            if args.apply:
                apply_archive_plan(plan)
    except ArchiveError as exc:
        print(f"ERROR: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
