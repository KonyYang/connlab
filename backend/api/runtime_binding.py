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
        self.database = settings.database_path.resolve()
        self.file_identity = _file_identity(self.database)
        value = [settings.environment, os.path.normcase(str(self.database)), self.file_identity]
        self.instance_id = sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()

    def metadata(self):
        if _file_identity(self.database) != self.file_identity:
            raise RuntimeChanged("The data instance changed while ConnLab was running. Restart ConnLab before continuing.")
        return {"schema_version": 1, "environment": self.settings.environment, "instance_id": self.instance_id,
                "default_output_paths": {purpose: str(self.settings.projects_dir if purpose == "Projects" else self.settings.output_path(purpose)) for purpose in ("Projects", "Materials", "TemporaryMaterials")}}

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
