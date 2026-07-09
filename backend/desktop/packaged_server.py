"""Portable ConnLab local web release launcher."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import uvicorn

from backend.desktop.packaged_static import mount_packaged_frontend
from backend.desktop.runtime_paths import (
    PackagedRuntimePaths,
    build_packaged_runtime_paths,
    prepare_packaged_runtime_environment,
)


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
FEE_EXPORT_CHILD_FLAG = "--connlab-fee-export-child"


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
) -> None:
    """Run ConnLab as a local browser-accessible server."""
    paths = build_packaged_runtime_paths(app_root=app_root, frontend_dist=frontend_dist)
    prepare_packaged_runtime_environment(paths)
    app = create_packaged_server_app(paths)
    print("")
    print("ConnLab local web server is starting.")
    print(f"Open http://{host}:{port}/ in Microsoft Edge or another browser.")
    print("Close this window to stop ConnLab.")
    print("")
    uvicorn.run(app, host=host, port=port, log_level="info", access_log=False)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse local web server command-line options."""
    parser = argparse.ArgumentParser(description="Run ConnLab local web server.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", default=DEFAULT_PORT, type=int)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Console script entry point for PyInstaller."""
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments and arguments[0] == FEE_EXPORT_CHILD_FLAG:
        from backend.infrastructure.office.fee_evaluation_export_child import (
            main as fee_export_child_main,
        )

        return fee_export_child_main(arguments[1:])
    args = parse_args(arguments)
    run_packaged_web_server(host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
