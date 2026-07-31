"""Bounded launcher regressions for TASK_368C."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
LAUNCHER = ROOT / "scripts" / "run_frontend.ps1"


def _run_fake_frontend_launcher(
    tmp_path: Path,
    *,
    vite_shim_exists: bool,
    install_creates_shim: bool,
) -> tuple[subprocess.CompletedProcess[str], list[str]]:
    """Run a copied launcher with a recording fake npm command."""
    fake_repo = tmp_path / "fake-repo"
    scripts_dir = fake_repo / "scripts"
    frontend_dir = fake_repo / "frontend"
    fake_bin = tmp_path / "fake-bin"
    scripts_dir.mkdir(parents=True)
    frontend_dir.mkdir()
    fake_bin.mkdir()

    copied_launcher = scripts_dir / "run_frontend.ps1"
    copied_launcher.write_text(LAUNCHER.read_text(encoding="utf-8"), encoding="utf-8")

    node_modules = frontend_dir / "node_modules"
    node_modules.mkdir()
    vite_shim = node_modules / ".bin" / "vite.cmd"
    if vite_shim_exists:
        vite_shim.parent.mkdir()
        vite_shim.write_text("@exit /b 0\n", encoding="utf-8")

    invocation_log = tmp_path / "npm-invocations.txt"
    fake_npm = fake_bin / "npm.cmd"
    fake_npm.write_text(
        "\n".join(
            [
                "@echo off",
                'echo %*>>"%FAKE_NPM_LOG%"',
                'if /I "%~1"=="install" (',
                '  if "%FAKE_NPM_CREATE_VITE%"=="1" (',
                '    if not exist "%CD%\\node_modules\\.bin" mkdir "%CD%\\node_modules\\.bin"',
                '    type nul > "%CD%\\node_modules\\.bin\\vite.cmd"',
                "  )",
                ")",
                "exit /b 0",
            ]
        ),
        encoding="utf-8",
    )

    environment = os.environ.copy()
    environment["PATH"] = f"{fake_bin}{os.pathsep}{environment['PATH']}"
    environment["FAKE_NPM_LOG"] = str(invocation_log)
    environment["FAKE_NPM_CREATE_VITE"] = "1" if install_creates_shim else "0"
    completed = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-File",
            str(copied_launcher),
        ],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    invocations = (
        invocation_log.read_text(encoding="utf-8").splitlines()
        if invocation_log.exists()
        else []
    )
    return completed, invocations


def test_missing_vite_shim_installs_before_starting_dev_server(tmp_path: Path) -> None:
    completed, invocations = _run_fake_frontend_launcher(
        tmp_path,
        vite_shim_exists=False,
        install_creates_shim=True,
    )

    assert completed.returncode == 0
    assert invocations == ["install", "run dev"]


def test_existing_vite_shim_skips_install(tmp_path: Path) -> None:
    completed, invocations = _run_fake_frontend_launcher(
        tmp_path,
        vite_shim_exists=True,
        install_creates_shim=False,
    )

    assert completed.returncode == 0
    assert invocations == ["run dev"]


def test_successful_install_without_vite_shim_fails_closed(tmp_path: Path) -> None:
    completed, invocations = _run_fake_frontend_launcher(
        tmp_path,
        vite_shim_exists=False,
        install_creates_shim=False,
    )

    assert completed.returncode != 0
    assert invocations == ["install"]
    assert "Vite command is still unavailable" in completed.stderr
