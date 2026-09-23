"""Portable ConnLab local web release launcher."""

from __future__ import annotations

import argparse
import errno
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
    prepare_packaged_runtime_environment(paths)
    configure_packaged_logging(log_path=paths.logs_dir / "connlab.log")
    app = create_packaged_server_app(paths)

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
