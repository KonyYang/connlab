"""Portable ConnLab local web release launcher."""

from __future__ import annotations

import argparse
import errno
import json
import os
import tomllib
import socket
import sys
import webbrowser
from pathlib import Path
from typing import Any

import uvicorn

from backend.desktop.packaged_static import mount_packaged_frontend
from backend.desktop.runtime_paths import (
    PackagedRuntimePaths,
    build_packaged_runtime_paths,
    prepare_packaged_runtime_environment,
)
from backend.shared.logging import configure_packaged_logging


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
FEE_EXPORT_CHILD_FLAG = "--connlab-fee-export-child"
CUSTOMER_REPORT_CHILD_FLAG = "--connlab-customer-report-child"


def create_packaged_server_app(paths: PackagedRuntimePaths):
    """Create the FastAPI app after packaged environment defaults are active."""
    from backend.api.main import app
    from backend.api.runtime_binding import initialize_runtime_binding, install_browser_storage_open
    initialize_runtime_binding(app)
    install_browser_storage_open(app)
    mount_packaged_frontend(app, paths.frontend_dist)
    return app


def run_packaged_web_server(
    *,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    app_root: Path | None = None,
    frontend_dist: Path | None = None,
    open_browser: bool = False,
) -> bool:
    """Run ConnLab as a local browser-accessible server."""
    paths = build_packaged_runtime_paths(app_root=app_root, frontend_dist=frontend_dist)

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        listener.bind((host, port))
        listener.listen(socket.SOMAXCONN)
        listener.setblocking(False)
    except OSError as error:
        listener.close()
        print("")
        if error.errno == errno.EADDRINUSE:
            print(f"ConnLab cannot start because {host}:{port} is already in use.")
            print(
                "If another ConnLab server window is open, close that window and "
                "run Start_ConnLab.bat again."
            )
            print("No other process was stopped, and the browser was not opened.")
        else:
            print(f"ConnLab could not reserve {host}:{port}: {error}")
        if open_browser:
            try:
                input("Press Enter to close this window...")
            except EOFError:
                pass
        return False

    try:
        executable = Path(sys.executable) if getattr(sys, "frozen", False) else app_root or paths.app_root
        app = _initialize_browser_app(paths, executable)
    except (OSError, ValueError) as error:
        listener.close()
        print(f"ConnLab could not prepare its storage: {error}")
        if open_browser:
            try:
                input("Press Enter to close this window...")
            except EOFError:
                pass
        return False
    except BaseException:
        listener.close()
        raise

    print("")
    print("ConnLab local web server is starting.")
    print(f"Open http://{host}:{port}/ in Microsoft Edge or another browser.")
    print("Close this window to stop ConnLab.")
    print("")

    server_app: Any = app
    if open_browser:
        target_url = f"http://{host}:{port}/"

        async def open_browser_after_lifespan_startup(
            scope: dict[str, Any], receive: Any, send: Any
        ) -> None:
            if scope["type"] != "lifespan":
                await app(scope, receive, send)
                return

            async def open_after_startup(message: dict[str, Any]) -> None:
                if message["type"] == "lifespan.startup.complete":
                    try:
                        webbrowser.open(target_url)
                    except Exception as error:  # Browser launch should not stop the server.
                        print(f"Could not open the browser automatically: {error}")
                        print(f"Open {target_url} manually.")
                await send(message)

            await app(scope, receive, open_after_startup)

        server_app = open_browser_after_lifespan_startup

    config = uvicorn.Config(
        server_app,
        host=host,
        port=port,
        log_level="info",
        access_log=False,
        log_config=None,
    )
    server = uvicorn.Server(config)
    try:
        server.run(sockets=[listener])
    finally:
        listener.close()
    return True


def _initialize_browser_app(paths, executable_location):
    """Start storage only after the server owns its port."""
    prepare_packaged_runtime_environment(paths, legacy_template_directory=False)
    configure_packaged_logging(log_path=paths.logs_dir / "connlab.log")
    from backend.api.dependencies import get_settings, get_session_factory
    from backend.desktop.browser_storage import register_browser_storage, uses_legacy_defaults
    from backend.infrastructure.files.browser_template_seed import seed_browser_templates

    settings = get_settings()
    upgrading = uses_legacy_defaults(settings)
    app = create_packaged_server_app(paths)
    # Preserve the user's actual drive letter, even when it is a substituted volume.
    drive_root = Path(executable_location.absolute().anchor)
    if not drive_root.drive.endswith(":"):
        raise ValueError(f"Start ConnLab from a local drive: {executable_location}")
    overrides = _browser_storage_overrides(settings)
    storage = register_browser_storage(settings, get_session_factory(), drive_root / "ConnLabFiles",
                                       overrides, upgrading=upgrading)
    _apply_browser_storage_paths(settings, storage.locations)
    if "Template" not in storage.unavailable:
        storage.warnings.extend(seed_browser_templates(
            storage.locations["Template"], paths.app_root / "browser_templates.zip", overrides=storage.template_overrides
        ))
    app.state.runtime_binding.browser_storage = storage
    for warning in storage.warnings:
        print(warning)
    return app


def _browser_storage_overrides(settings):
    """Detect explicit existing configuration before selecting release defaults."""
    config_path = Path(os.environ["CONNLAB_LOCAL_CONFIG_PATH"])
    configured = {}
    if config_path.is_file():
        with config_path.open("rb") as handle:
            configured = tomllib.load(handle).get("paths", {})
    inherited = json.loads(os.environ.get("CONNLAB_MANAGED_ENV_DEFAULTS", "{}"))
    def configured_path(name, fallback):
        # Settings normalizes paths with resolve(); inspect the original spelling
        # so a junction in an operator-selected template path remains detectable.
        value = os.environ.get(name)
        if not value:
            return fallback
        return Path(__file__).resolve().parents[2] / Path(value).expanduser()

    overrides = {}
    if settings.projects_directory_explicit or settings.library_root:
        overrides["Projects"] = configured_path("CONNLAB_PROJECTS_DIR", settings.projects_dir)
    if (configured.get("templates_dir") or settings.library_root
            or os.getenv("CONNLAB_TEMPLATES_DIR") != inherited.get("CONNLAB_TEMPLATES_DIR")):
        overrides["Template"] = configured_path("CONNLAB_TEMPLATES_DIR", settings.templates_dir)
    return overrides


def _apply_browser_storage_paths(settings, locations):
    # Older features read Settings directly instead of consulting the registration tables.
    managed = json.loads(os.environ.get("CONNLAB_MANAGED_ENV_DEFAULTS", "{}"))
    for name, purpose in (("CONNLAB_PROJECTS_DIR", "Projects"), ("CONNLAB_TEMPLATES_DIR", "Template")):
        path = locations[purpose]
        if purpose == "Projects" and settings.library_root and not path.resolve().is_relative_to(settings.library_root):
            continue  # Keep the existing isolated project-library runtime lease valid.
        if os.environ.get(name) == managed.get(name):
            managed[name] = os.environ[name] = str(path)
    os.environ["CONNLAB_MANAGED_ENV_DEFAULTS"] = json.dumps(managed)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse local web server command-line options."""
    parser = argparse.ArgumentParser(description="Run ConnLab local web server.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", default=DEFAULT_PORT, type=int)
    parser.add_argument(
        "--open-browser",
        action="store_true",
        help="Open the browser after the server has started successfully.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Console script entry point for PyInstaller."""
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments and arguments[0] == FEE_EXPORT_CHILD_FLAG:
        from backend.infrastructure.office.fee_evaluation_export_child import (
            main as fee_export_child_main,
        )

        return fee_export_child_main(arguments[1:])
    if arguments and arguments[0] == CUSTOMER_REPORT_CHILD_FLAG:
        from backend.infrastructure.office.customer_report_subprocess_child import (
            main as customer_report_child_main,
        )

        return customer_report_child_main(arguments[1:])
    args = parse_args(arguments)
    started = run_packaged_web_server(
        host=args.host,
        port=args.port,
        open_browser=args.open_browser,
    )
    return 0 if started else 1


if __name__ == "__main__":
    raise SystemExit(main())
