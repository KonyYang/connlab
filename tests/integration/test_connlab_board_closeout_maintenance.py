from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

import pytest

from tests.unit.test_connlab_active_context import HELPER, invoke, make_repo


def forge_generation_two_authority_archive(fx: dict[str, object]) -> None:
    repo = Path(fx["repo"]); board = Path(fx["board"])
    index_path = repo / "docs/archive/task_board_history/index.v1.jsonl"
    records = [json.loads(line) for line in index_path.read_text(encoding="utf-8").splitlines()]
    record = records[1]; archive = repo / record["archive_path"]
    payload = json.loads(archive.read_text(encoding="utf-8"))
    source = subprocess.run(["git", "-C", str(repo), "show", f"{record['source_commit']}:docs/task_board.md"], check=True, capture_output=True).stdout.decode("utf-8")
    lines = source.splitlines(keepends=True)
    protected = [
        "- `TASK_CURRENT_AUTHORITY`: complete/accepted; current authority must remain.\n",
        "- `TASK_ACTIVE_AUTHORITY`: complete/accepted; active authority must remain.\n",
        "- `TASK_QUEUE_AUTHORITY`: complete/accepted; FIFO queue authority must remain.\n",
        "- `TASK_PAUSE_AUTHORITY`: complete/accepted; paused owner authority must remain.\n",
        "- `TASK_QF_AUTHORITY`: complete/accepted; Quick Fix owner authority must remain.\n",
        "- `TASK_PARALLEL_AUTHORITY`: complete/accepted; parallel exception authority must remain.\n",
        "- `TASK_RESIDUAL_AUTHORITY`: complete/accepted; residual owner authority must remain.\n",
        "- `TASK_PROPOSAL_AUTHORITY`: complete/accepted; proposal authority must remain.\n",
    ]
    insert_at = len(lines)
    lines.extend(protected)
    forged_source = "".join(lines)
    board.write_text(forged_source, encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "docs/task_board.md"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", "authority-bearing generation two source"], check=True, capture_output=True)
    source_commit = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    source_blob = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD:docs/task_board.md"], check=True, capture_output=True, text=True).stdout.strip()
    records_to_remove = [{"line": insert_at + index, "text": text} for index, text in enumerate(protected)]
    compact_lines = forged_source.splitlines(keepends=True)
    for item in records_to_remove: compact_lines[item["line"]] = ""
    compact = "".join(compact_lines).encode()
    payload = {"schema": "connlab.task-board-history-index", "version": 1, "generation": 2, "archive_mode": "terminal_records", "records": records_to_remove}
    archive_raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    record.update({
        "source_commit": source_commit, "source_blob_sha": source_blob,
        "source_board_sha256": hashlib.sha256(forged_source.encode()).hexdigest(), "source_bytes": len(forged_source.encode()),
        "source_record_count": 38, "archive_sha256": hashlib.sha256(archive_raw).hexdigest(), "archive_record_count": 8,
        "compact_board_sha256": hashlib.sha256(compact).hexdigest(), "compact_bytes": len(compact), "compact_record_count": 30,
        "rollback_sha256": hashlib.sha256(forged_source.encode()).hexdigest(),
        "moved_record_ids": sorted(line.split("`")[1] for line in protected),
    })
    record["archive_path"] = f"docs/archive/task_board_history/generation-000002-{source_commit}.md"
    old_archive = archive; archive = repo / record["archive_path"]
    old_archive.unlink(); archive.write_bytes(archive_raw)
    facts = {"generation": 2, "head": source_commit, "source": record["source_board_sha256"], "archive": record["archive_sha256"], "compact": record["compact_board_sha256"], "previous": record["previous_index_sha256"]}
    record["plan_digest"] = hashlib.sha256(json.dumps(facts, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    index_path.write_bytes("".join(json.dumps(item, sort_keys=True, separators=(",", ":")) + "\n" for item in records).encode())
    board.write_bytes(compact)
    subprocess.run(["git", "-C", str(repo), "add", "docs/task_board.md", "docs/archive/task_board_history"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", "forged canonical authority archive"], check=True, capture_output=True)
    fx["head"] = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()


def commit_next_closeout(fx: dict[str, object], generation: int) -> None:
    repo = Path(fx["repo"])
    board = Path(fx["board"])
    text = board.read_text(encoding="utf-8")
    details = "\n".join(
        f"- `TASK_CLOSEOUT_{generation}_{index:03d}`: complete/accepted. Evidence: `g{generation}-{index}.md`."
        for index in range(30)
    )
    board.write_text(text + details + "\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "docs/task_board.md"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", f"closeout {generation}"], check=True, capture_output=True)
    fx["head"] = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()


def test_second_and_third_closeouts_append_contiguous_incremental_generations(tmp_path: Path) -> None:
    fx = make_repo(tmp_path)
    assert invoke(fx, "apply-maintenance")[0] == 0
    repo = Path(fx["repo"])
    subprocess.run(["git", "-C", str(repo), "add", "docs/task_board.md", "docs/archive/task_board_history"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", "generation one"], check=True, capture_output=True)

    for generation in (2, 3):
        commit_next_closeout(fx, generation)
        code, applied = invoke(fx, "apply-maintenance")
        assert code == 0 and applied["generation"] == generation
        archive = repo / applied["archive_path"]
        assert archive.read_bytes() != Path(fx["board"]).read_bytes()
        payload = json.loads(archive.read_text(encoding="utf-8"))
        assert payload["archive_mode"] == "terminal_records"
        assert payload["records"]
        subprocess.run(["git", "-C", str(repo), "add", "docs/task_board.md", "docs/archive/task_board_history"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-m", f"generation {generation}"], check=True, capture_output=True)

    lines = (repo / "docs" / "archive" / "task_board_history" / "index.v1.jsonl").read_text(encoding="utf-8").splitlines()
    assert [json.loads(line)["generation"] for line in lines] == [1, 2, 3]


def test_second_and_third_generation_rollback_is_byte_exact_in_safe_temp_root(tmp_path: Path) -> None:
    fx = make_repo(tmp_path)
    repo = Path(fx["repo"]); sources: dict[int, bytes] = {}
    for generation in (1, 2, 3):
        if generation > 1:
            commit_next_closeout(fx, generation)
        sources[generation] = Path(fx["board"]).read_bytes()
        assert invoke(fx, "apply-maintenance")[0] == 0
        subprocess.run(["git", "-C", str(repo), "add", "docs/task_board.md", "docs/archive/task_board_history"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-m", f"generation {generation}"], check=True, capture_output=True)
        fx["head"] = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    temp_root = tmp_path / "rollback-temp"; temp_root.mkdir()
    for generation in (1, 2, 3):
        output = temp_root / f"generation-{generation}.md"
        done = subprocess.run(
            ["py", str(HELPER), "prove-rollback", "--repo-root", str(repo), "--generation", str(generation),
             "--temp-root", str(temp_root), "--output", str(output), "--json"],
            check=False, capture_output=True, text=True,
        )
        assert done.returncode == 0, done.stdout
        assert output.read_bytes() == sources[generation]


@pytest.mark.parametrize("fault", ["archive", "index", "board"])
def test_partial_failure_restores_board_index_and_exact_archive_state(tmp_path: Path, fault: str) -> None:
    fx = make_repo(tmp_path)
    repo = Path(fx["repo"])
    board = Path(fx["board"])
    before = board.read_bytes()
    plan = invoke(fx, "plan-maintenance")[1]
    archive = repo / str(plan["archive_path"])
    index = repo / "docs" / "archive" / "task_board_history" / "index.v1.jsonl"
    env = os.environ.copy()
    env["CONNLAB_MAINTENANCE_FAIL_AFTER"] = fault
    args = [
        "py", str(HELPER), "apply-maintenance", "--repo-root", str(repo),
        "--expected-head", str(fx["head"]), "--expected-board-sha256", hashlib.sha256(before).hexdigest(),
        "--expected-plan-digest", str(plan["plan_digest"]), "--json",
    ]
    done = subprocess.run(args, env=env, check=False, capture_output=True, text=True)
    result = json.loads(done.stdout)
    assert done.returncode != 0 and "BLOCKED_MAINTENANCE_WRITE_FAILED" in result["reason_codes"]
    assert board.read_bytes() == before
    assert not archive.exists()
    assert not index.exists()


def test_conflicting_archive_and_corrupt_index_fail_closed(tmp_path: Path) -> None:
    fx = make_repo(tmp_path / "conflict")
    plan = invoke(fx, "plan-maintenance")[1]
    archive = Path(fx["repo"]) / str(plan["archive_path"])
    archive.parent.mkdir(parents=True)
    archive.write_text("conflict", encoding="utf-8")
    code, result = invoke(fx, "apply-maintenance")
    assert code != 0 and "BLOCKED_ARCHIVE_CONFLICT" in result["reason_codes"]

    fx = make_repo(tmp_path / "corrupt")
    index = Path(fx["repo"]) / "docs" / "archive" / "task_board_history" / "index.v1.jsonl"
    index.parent.mkdir(parents=True)
    index.write_text("not json\n", encoding="utf-8")
    code, result = invoke(fx, "plan-maintenance")
    assert code != 0 and "BLOCKED_INDEX_CORRUPT" in result["reason_codes"]


@pytest.mark.parametrize(
    ("field", "value"),
    [("schema", "wrong"), ("version", 2), ("source_blob_sha", "0" * 40),
     ("generation", 2), ("compact_record_count", 999), ("rollback_sha256", "0" * 64),
     ("archive_path", "docs/archive/task_board_history/../escape.md")],
)
def test_index_schema_blob_count_and_rollback_tampering_fail_closed(tmp_path: Path, field: str, value: object) -> None:
    fx = make_repo(tmp_path)
    assert invoke(fx, "apply-maintenance")[0] == 0
    repo = Path(fx["repo"]); board = Path(fx["board"])
    index = repo / "docs/archive/task_board_history/index.v1.jsonl"
    record = json.loads(index.read_text(encoding="utf-8")); record[field] = value
    index.write_text(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    before = {"board": board.read_bytes(), "index": index.read_bytes()}
    code, result = invoke(fx, "plan-maintenance")
    assert code != 0 and set(result["reason_codes"]) & {"BLOCKED_INDEX_CORRUPT", "BLOCKED_ARCHIVE_CORRUPT", "BLOCKED_ARCHIVE_PATH"}
    assert board.read_bytes() == before["board"] and index.read_bytes() == before["index"]


def test_history_directory_junction_is_rejected_before_any_write(tmp_path: Path) -> None:
    fx = make_repo(tmp_path); repo = Path(fx["repo"]); board = Path(fx["board"])
    history = repo / "docs/archive/task_board_history"; history.parent.mkdir(parents=True)
    outside = tmp_path / "outside-history"; outside.mkdir()
    junction = subprocess.run(["cmd", "/c", "mklink", "/J", str(history), str(outside)], check=False, capture_output=True)
    if junction.returncode: pytest.skip("directory junctions are unavailable on this Windows host")
    before = board.read_bytes(); code, result = invoke(fx, "plan-maintenance")
    assert code != 0 and "BLOCKED_ARCHIVE_PATH" in result["reason_codes"]
    assert board.read_bytes() == before and not any(outside.iterdir())


def test_recomputed_generation_two_cannot_archive_authority_lines_before_generation_three(tmp_path: Path) -> None:
    fx = make_repo(tmp_path); repo = Path(fx["repo"])
    assert invoke(fx, "apply-maintenance")[0] == 0
    subprocess.run(["git", "-C", str(repo), "add", "docs/task_board.md", "docs/archive/task_board_history"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", "generation one"], check=True, capture_output=True)
    commit_next_closeout(fx, 2); assert invoke(fx, "apply-maintenance")[0] == 0
    subprocess.run(["git", "-C", str(repo), "add", "docs/task_board.md", "docs/archive/task_board_history"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", "generation two"], check=True, capture_output=True)
    forge_generation_two_authority_archive(fx)
    before = Path(fx["board"]).read_bytes()
    code, result = invoke(fx, "plan-maintenance")
    assert code != 0 and "BLOCKED_ARCHIVE_CORRUPT" in result["reason_codes"], result
    assert Path(fx["board"]).read_bytes() == before
