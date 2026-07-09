"""Portable ConnLab desktop release launcher."""

from __future__ import annotations

import socket
import threading
import time
from dataclasses import dataclass
from pathlib import Path

import uvicorn

from backend.desktop.path_picker_api import DesktopPathPickerApi, PyWebViewPathPicker
from backend.desktop.packaged_static import mount_packaged_frontend
from backend.desktop.runtime_paths import (
    PackagedRuntimePaths,
    build_packaged_runtime_paths,
    prepare_packaged_runtime_environment,
)
from backend.desktop.shell import desktop_bridge_script


@dataclass(slots=True)
class DesktopServerHandle:
    """Own the in-process Uvicorn server used by the packaged desktop app."""

    server: uvicorn.Server
    thread: threading.Thread
    url: str

    def stop(self) -> None:
        """Request server shutdown and wait briefly for it to exit."""
        self.server.should_exit = True
        self.thread.join(timeout=5)


def find_available_port(host: str = "127.0.0.1") -> int:
    """Ask the OS for a currently available local TCP port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind((host, 0))
        return int(probe.getsockname()[1])


def create_packaged_app(paths: PackagedRuntimePaths):
    """Create the FastAPI app after packaged environment defaults are active."""
    from backend.api.main import app

    mount_packaged_frontend(app, paths.frontend_dist)
    return app


def start_packaged_api_server(
    *,
    paths: PackagedRuntimePaths,
    host: str = "127.0.0.1",
    port: int | None = None,
) -> DesktopServerHandle:
    """Start the local API server in a background thread."""
    selected_port = port or find_available_port(host)
    app = create_packaged_app(paths)
    config = uvicorn.Config(
        app,
        host=host,
        port=selected_port,
        log_level="info",
        access_log=False,
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, name="connlab-packaged-api", daemon=True)
    thread.start()
    _wait_for_server_start(server, thread)
    return DesktopServerHandle(
        server=server,
        thread=thread,
        url=f"http://{host}:{selected_port}/",
    )


def run_packaged_desktop(
    *,
    app_root: Path | None = None,
    frontend_dist: Path | None = None,
) -> None:
    """Run ConnLab as a portable packaged desktop application."""
    try:
        import webview  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError(
            "ConnLab desktop runtime requires PyWebView and Microsoft Edge WebView2."
        ) from exc

    paths = build_packaged_runtime_paths(app_root=app_root, frontend_dist=frontend_dist)
    prepare_packaged_runtime_environment(paths)
    server_handle = start_packaged_api_server(paths=paths)
    window_holder: dict[str, object] = {}
    picker = PyWebViewPathPicker(window_provider=lambda: window_holder.get("window"))
    api = DesktopPathPickerApi(picker=picker)
    window = webview.create_window(
        "ConnLab",
        server_handle.url,
        js_api=api,
        width=1280,
        height=820,
        min_size=(1024, 680),
    )
    window_holder["window"] = window
    try:
        webview.start(_install_desktop_bridge, window)
    finally:
        server_handle.stop()


def _install_desktop_bridge(window: object) -> None:
    window.evaluate_js(desktop_bridge_script())


def _wait_for_server_start(server: uvicorn.Server, thread: threading.Thread) -> None:
    """Wait for Uvicorn startup to complete or fail."""
    for _ in range(100):
        if server.started:
            return
        if not thread.is_alive():
            raise RuntimeError("ConnLab packaged API server exited during startup.")
        time.sleep(0.05)
    raise RuntimeError("ConnLab packaged API server did not start within 5 seconds.")


def main() -> None:
    """Console script entry point for PyInstaller."""
    run_packaged_desktop()


if __name__ == "__main__":
    main()
