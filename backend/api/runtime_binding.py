"""Bind one running server to its explicitly selected environment and physical database."""
from hashlib import sha256
import json
import os
from pathlib import Path
from starlette.responses import JSONResponse

class RuntimeChanged(ValueError):
    pass

def _file_identity(path):
    try:
        info = path.stat()
    except OSError as error:
        raise RuntimeChanged("The data instance is unavailable. Restart ConnLab before continuing.") from error
    # Windows ctime is creation time. POSIX ctime changes on ordinary writes.
    created = getattr(info, "st_birthtime_ns", info.st_ctime_ns if os.name == "nt" else None)
    return [info.st_dev, info.st_ino, created]

class RuntimeBinding:
    def __init__(self, settings):
        self.settings = settings
        self.browser_storage = None
        self.database = settings.database_path.resolve()
        self.file_identity = _file_identity(self.database)
        value = [settings.environment, os.path.normcase(str(self.database)), self.file_identity]
        self.instance_id = sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()

    def metadata(self):
        if _file_identity(self.database) != self.file_identity:
            raise RuntimeChanged("The data instance changed while ConnLab was running. Restart ConnLab before continuing.")
        metadata = {"schema_version": 1, "environment": self.settings.environment, "instance_id": self.instance_id,
                "default_output_paths": {purpose: str(self.settings.projects_dir if purpose == "Projects" else self.settings.output_path(purpose)) for purpose in ("Projects", "Materials", "TemporaryMaterials")}}

        if self.browser_storage is not None:
            metadata.update(self.browser_storage.metadata())
            locations = self.browser_storage.locations
            metadata["default_output_paths"] = {
                "Projects": str(locations["Projects"]), "Materials": str(locations["Library"]),
                "TemporaryMaterials": str(locations["TemporaryProjects"]),
            }
        return metadata

    @property
    def cookie_suffix(self):
        return self.instance_id[:24]

class RuntimeBindingMiddleware:
    def __init__(self, app, binding_provider):
        self.app, self.binding_provider = app, binding_provider

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or not scope.get("path", "").startswith("/api/"):
            return await self.app(scope, receive, send)
        headers = dict(scope.get("headers", []))
        from urllib.parse import parse_qs
        query = parse_qs(scope.get("query_string", b"").decode())
        expected = headers.get(b"x-connlab-instance")
        if expected is None and "connlab_instance" in query:
            expected = query["connlab_instance"][0].encode()
        environment = headers.get(b"x-connlab-environment")
        if environment is None and "connlab_environment" in query:
            environment = query["connlab_environment"][0].encode()
        binding = self.binding_provider()
        try:
            metadata = binding.metadata() if binding else None
        except RuntimeChanged as error:
            return await JSONResponse({"detail": {"code": "RUNTIME_INSTANCE_CHANGED", "message": str(error)}}, status_code=503)(scope, receive, send)
        if expected is not None and (metadata is None or expected.decode() != metadata["instance_id"] or environment is not None and environment.decode() != metadata["environment"]):
            return await JSONResponse({"detail": {"code": "RUNTIME_INSTANCE_MISMATCH", "message": "The connected data instance changed. Reload ConnLab before continuing."}}, status_code=409)(scope, receive, send)
        scope["connlab_runtime_binding"] = binding
        async def bound_send(message):
            if message["type"] == "http.response.start" and metadata:
                message["headers"] = [*(item for item in message.get("headers", []) if item[0].lower()!=b"cache-control"), (b"cache-control", b"no-store"), (b"x-connlab-instance", metadata["instance_id"].encode()), (b"x-connlab-environment", metadata["environment"].encode())]
            await send(message)
        return await self.app(scope, receive, bound_send)

def install_runtime_binding(app, binding_provider):
    app.add_middleware(RuntimeBindingMiddleware, binding_provider=binding_provider)

def initialize_runtime_binding(app):
    from backend.api.dependencies import get_engine, get_settings
    if getattr(app.state, "runtime_binding", None) is None:
        get_engine()
        app.state.runtime_binding = RuntimeBinding(get_settings())
    return app.state.runtime_binding


def install_browser_storage_open(app):
    """The browser release may only open a directory this instance registered."""
    from fastapi import HTTPException, Request
    from backend.infrastructure.files.local_folder_open_gateway import LocalFolderOpenGateway
    from backend.infrastructure.project_library.files import checked_path

    @app.post("/api/runtime-storage/open/{purpose}", include_in_schema=False)
    def open_registered_folder(purpose: str, request: Request):
        binding = app.state.runtime_binding
        if (not request.client or request.client.host not in {"127.0.0.1", "::1"}
                or request.url.hostname not in {"localhost", "127.0.0.1", "::1"}
                or request.headers.get("origin", str(request.base_url).rstrip("/")) != str(request.base_url).rstrip("/")):
            raise HTTPException(403, "Open the folder on the computer running ConnLab.")
        if request.headers.get("X-ConnLab-Instance") != binding.instance_id:
            raise HTTPException(409, "Reload ConnLab before opening a folder.")
        storage = binding.browser_storage
        path = storage.common_root if purpose == "Root" else storage.locations.get(purpose)
        if path is None:
            raise HTTPException(404, "Unknown storage location.")
        try:
            checked_path(path)
            result = LocalFolderOpenGateway().open_directory(path)
        except (OSError, ValueError) as error:
            raise HTTPException(409, f"Cannot open {path}. Restore access to the registered folder.") from error
        if result.status != "opened":
            raise HTTPException(409, f"Cannot open {path}: {result.message}")
        return {"opened": True}
