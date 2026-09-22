from __future__ import annotations

from pathlib import Path

import pytest

import backend.desktop.managed_development_launcher as launcher
from backend.desktop.managed_development_launcher import ManagedDevelopmentRuntime


def test_managed_runtime_stops_only_its_started_processes_when_shell_closes(
    tmp_path: Path,
) -> None:
    calls: list[object] = []
    backend = _Process(101)
    frontend = _Process(202)

    def launch(command: tuple[str, ...], working_directory: Path) -> _Process:
        calls.append(("launch", command, working_directory))
        return backend if "uvicorn" in command else frontend

    runtime = ManagedDevelopmentRuntime(
        repo_root=tmp_path,
        launch_process=launch,
        wait_for_ready=lambda url, process: calls.append(("ready", url, process.pid)),
        run_desktop_shell=lambda url: calls.append(("shell", url)),
        stop_process_tree=lambda process: calls.append(("stop", process.pid)),
        python_executable="python",
        npm_executable="npm.cmd",
    )

    runtime.run()

    assert calls == [
        ("launch", backend_command(tmp_path), tmp_path),
        ("ready", "http://127.0.0.1:8000/health", 101),
        ("launch", frontend_command(tmp_path), tmp_path / "frontend"),
        ("ready", "http://127.0.0.1:5173/", 202),
        ("shell", "http://127.0.0.1:5173"),
        ("stop", 202),
        ("stop", 101),
    ]


def test_managed_runtime_releases_started_processes_after_shell_failure(
    tmp_path: Path,
) -> None:
    stopped: list[int] = []
    backend = _Process(101)
    frontend = _Process(202)

    def launch(command: tuple[str, ...], _working_directory: Path) -> _Process:
        return backend if "uvicorn" in command else frontend

    runtime = ManagedDevelopmentRuntime(
        repo_root=tmp_path,
        launch_process=launch,
        wait_for_ready=lambda _url, _process: None,
        run_desktop_shell=lambda _url: (_ for _ in ()).throw(RuntimeError("shell failed")),
        stop_process_tree=lambda process: stopped.append(process.pid),
        python_executable="python",
        npm_executable="npm.cmd",
    )

    with pytest.raises(RuntimeError, match="shell failed"):
        runtime.run()

    assert stopped == [202, 101]


def test_process_tree_stop_targets_only_the_owned_process_pid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[object] = []
    monkeypatch.setattr(
        launcher.subprocess,
        "run",
        lambda command, **kwargs: calls.append((command, kwargs)),
    )

    launcher._stop_process_tree(_Process(4242))

    assert calls == [
        (
            ["taskkill", "/PID", "4242", "/T", "/F"],
            {"check": False, "capture_output": True, "text": True},
        )
    ]


class _Process:
    def __init__(self, pid: int) -> None:
        self.pid = pid

    def poll(self) -> None:
        return None


def backend_command(repo_root: Path) -> tuple[str, ...]:
    return (
        "python",
        "-m",
        "uvicorn",
        "backend.api.development:create_app",
        "--factory",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
        "--reload",
    )


def frontend_command(repo_root: Path) -> tuple[str, ...]:
    del repo_root
    return ("npm.cmd", "run", "dev", "--", "--host", "127.0.0.1")
