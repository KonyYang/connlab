"""Exercise the Windows development entry without using the live port or database."""

import os
from pathlib import Path
import socket
import subprocess
import sys
import time

import pytest


pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Windows development launcher")
SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
BACKEND = "run_backend.ps1"
DESKTOP = "run_mvp_dev.ps1"


def copy_launchers(directory, port):
    scripts = directory / "scripts"
    scripts.mkdir()
    desktop = directory / "backend" / "desktop"
    desktop.mkdir(parents=True)
    # Substitute only the fixed machine addresses in the isolated copy.
    source = (SCRIPTS / BACKEND).read_text(encoding="utf-8-sig").replace("8000", str(port))
    source = source.replace(r"C:\PythonEnvs\connlab\.venv\Scripts\python.exe", sys.executable)
    (scripts / BACKEND).write_text(source, encoding="utf-8-sig")
    (scripts / DESKTOP).write_bytes((SCRIPTS / DESKTOP).read_bytes())
    (directory / "py.cmd").write_text(f'@"{sys.executable}" %*\n', encoding="utf-8")
    (desktop / "managed_development_launcher.py").write_text(
        "import runpy\nrunpy.run_module('uvicorn', run_name='__main__')\n", encoding="utf-8",
    )
    for package in (directory / "backend", desktop):
        (package / "__init__.py").touch()
    (directory / "uvicorn.py").write_text(
        "from pathlib import Path\n"
        "import os, sys, time\n"
        "name = os.environ['TEST_INVOCATION']\n"
        "Path(name).write_text('\\n'.join(sys.argv[1:]), encoding='utf-8')\n"
        "if name == 'hold':\n"
        "    deadline = time.monotonic() + 30\n"
        "    while not Path('release').exists() and time.monotonic() < deadline:\n"
        "        time.sleep(0.05)\n"
        "    sys.exit(9)\n",
        encoding="utf-8",
    )
    return scripts


def start(launcher, invocation):
    return subprocess.Popen(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(launcher)],
        env={
            **os.environ, "TEST_INVOCATION": invocation,
            "PATH": str(launcher.parent.parent) + os.pathsep + os.environ["PATH"],
        },
        cwd=launcher.parent.parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


@pytest.mark.parametrize("entry", [BACKEND, DESKTOP])
def test_refuses_port_already_held_by_another_process(tmp_path, entry):
    with socket.socket() as occupied:
        # Uvicorn opts into address sharing on Windows, so a plain bind or a second
        # Uvicorn startup does not reliably detect this existing service.
        occupied.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        occupied.bind(("127.0.0.1", 0))
        occupied.listen()
        port = occupied.getsockname()[1]
        process = start(copy_launchers(tmp_path, port) / entry, "unexpected")
        message = process.communicate(timeout=15)[0]
        assert process.returncode != 0 and str(port) in message
        assert not (tmp_path / "unexpected").exists()
        with socket.create_connection(("127.0.0.1", port), timeout=2):
            with occupied.accept()[0]:
                pass


@pytest.mark.parametrize("first_entry,second_entry", [
    (BACKEND, BACKEND), (BACKEND, DESKTOP), (DESKTOP, BACKEND), (DESKTOP, DESKTOP),
])
def test_blocks_parallel_launch_before_binding_and_allows_restart_after_failure(
    tmp_path, first_entry, second_entry,
):
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    scripts = copy_launchers(tmp_path, port)
    first = start(scripts / first_entry, "hold")
    try:
        deadline = time.monotonic() + 12
        while not (tmp_path / "hold").exists() and time.monotonic() < deadline:
            assert first.poll() is None
            time.sleep(0.05)
        assert (tmp_path / "hold").exists()
        second = start(scripts / second_entry, "duplicate")
        message = second.communicate(timeout=12)[0]
        assert second.returncode != 0 and str(port) in message
        assert first.poll() is None and not (tmp_path / "duplicate").exists()
    finally:
        (tmp_path / "release").touch()
        first.communicate(timeout=12)
    assert first.returncode == 9
    restarted = start(scripts / BACKEND, "restart")
    output = restarted.communicate(timeout=12)[0]
    assert restarted.returncode == 0, output
    args = (tmp_path / "restart").read_text(encoding="utf-8").splitlines()
    assert args[args.index("--port") + 1] == str(port)
    assert (tmp_path / args[args.index("--reload-dir") + 1]).resolve() == tmp_path / "backend"
