"""Run the local development stack as one desktop-owned session."""

from __future__ import annotations

import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from urllib.error import URLError
from urllib.request import urlopen


BACKEND_URL = "http://127.0.0.1:8000/health"
FRONTEND_URL = "http://127.0.0.1:5173/"
DESKTOP_URL = "http://127.0.0.1:5173"
STARTUP_TIMEOUT_SECONDS = 30


class DevelopmentProcess(Protocol):
    """Minimal process ownership required by the managed development runtime."""

    pid: int

    def poll(self) -> int | None: ...


LaunchProcess = Callable[[tuple[str, ...], Path], DevelopmentProcess]
WaitForReady = Callable[[str, DevelopmentProcess], None]
RunDesktopShell = Callable[[str], None]
StopProcessTree = Callable[[DevelopmentProcess], None]


@dataclass(slots=True)
class ManagedDevelopmentRuntime:
    """Own backend and frontend children for the lifetime of one desktop window."""

    repo_root: Path
    launch_process: LaunchProcess
    wait_for_ready: WaitForReady
    run_desktop_shell: RunDesktopShell
    stop_process_tree: StopProcessTree
    python_executable: str = sys.executable
    npm_executable: str = "npm.cmd"

    def run(self) -> None:
        """Start children, show the desktop shell, then release only owned children."""
        backend: DevelopmentProcess | None = None
        frontend: DevelopmentProcess | None = None
        try:
            backend = self.launch_process(self._backend_command(), self.repo_root)
            self.wait_for_ready(BACKEND_URL, backend)
            frontend = self.launch_process(self._frontend_command(), self.repo_root / "frontend")
            self.wait_for_ready(FRONTEND_URL, frontend)
            self.run_desktop_shell(DESKTOP_URL)
        finally:
            if frontend is not None:
                self.stop_process_tree(frontend)
            if backend is not None:
                self.stop_process_tree(backend)

    def _backend_command(self) -> tuple[str, ...]:
        return (
            self.python_executable,
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

    def _frontend_command(self) -> tuple[str, ...]:
        return (self.npm_executable, "run", "dev", "--", "--host", "127.0.0.1")


def run_managed_development_desktop(repo_root: Path) -> None:
    """Launch the regular development stack under a desktop window owner."""
    runtime = ManagedDevelopmentRuntime(
        repo_root=Path(repo_root),
        launch_process=_launch_process,
        wait_for_ready=_wait_for_ready,
        run_desktop_shell=_run_desktop_shell,
        stop_process_tree=_stop_process_tree,
    )
    runtime.run()


def _launch_process(command: tuple[str, ...], working_directory: Path) -> DevelopmentProcess:
    return subprocess.Popen(command, cwd=working_directory)


def _wait_for_ready(url: str, process: DevelopmentProcess) -> None:
    deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Development process exited before serving {url}.")
        try:
            with urlopen(url, timeout=1) as response:  # noqa: S310 - loopback only
                if response.status < 500:
                    return
        except URLError:
            time.sleep(0.2)
    raise RuntimeError(f"Timed out waiting for development service: {url}")


def _run_desktop_shell(url: str) -> None:
    from backend.desktop.shell import run_desktop_shell

    run_desktop_shell(url)


def _stop_process_tree(process: DevelopmentProcess) -> None:
    """Stop one known child and descendants without inspecting unrelated listeners."""
    if process.poll() is not None:
        return
    subprocess.run(
        ["taskkill", "/PID", str(process.pid), "/T", "/F"],
        check=False,
        capture_output=True,
        text=True,
    )


def main() -> int:
    """Console entry point used by the PowerShell development launcher."""
    run_managed_development_desktop(Path(__file__).resolve().parents[2])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
