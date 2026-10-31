"""Native-selected local files/folders and the compatible isolated-upload endpoint."""
import json
import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from backend.api.dependencies import get_settings, get_tools_service
from backend.application.tools_service import ToolsError, ToolsService
from backend.application.tools_folder_encryption_service import ToolsFolderEncryptionService, ToolsLocalFolderEncryptionService, validate_folder_paths
from backend.infrastructure.files.tools_folder_archive_gateway import ToolsFolderArchiveGateway
from backend.infrastructure.files.tools_local_folder_gateway import ToolsLocalFolderGateway
from backend.infrastructure.files.windows_path_picker import WindowsPathPicker
from backend.shared.config import Settings

router = APIRouter()
MAX_FILE_BYTES = 100 * 1024 * 1024
MAX_TOTAL_BYTES = 500 * 1024 * 1024


def get_local_encryption_picker():
    return WindowsPathPicker().pick_encryption_directory


def get_local_file_encryption_picker():
    return WindowsPathPicker().pick_encryption_file


def _require_local_encryption_request(request: Request) -> None:
    origin = request.headers.get("origin", "")
    if (request.url.hostname not in {"localhost", "127.0.0.1", "::1"} or not request.client
        or request.client.host not in {"localhost", "127.0.0.1", "::1"}
        or origin != f"{request.url.scheme}://{request.url.netloc}"
        or urlsplit(origin).hostname not in {"localhost", "127.0.0.1", "::1"}
        or request.headers.get("x-connlab-local-encryption") != "1"):
        raise HTTPException(403, "Choose the file or folder from ConnLab on this computer.")


@router.post("/encrypt-local-file")
def encrypt_local_file(request: Request, picker=Depends(get_local_file_encryption_picker),
                       tools: ToolsService = Depends(get_tools_service)):
    _require_local_encryption_request(request)
    try:
        source = picker()
        if source is None:
            return {"cancelled": True}
        source = Path(source)
        return ToolsLocalFolderEncryptionService(tools=tools,
            files=ToolsLocalFolderGateway(source.parent)).encrypt_file(source)
    except (ToolsError, OSError, RuntimeError) as exc:
        message = str(exc) if isinstance(exc, ToolsError) else "Could not read the selected file. Check file and folder access and try again."
        raise HTTPException(422, message) from exc


@router.post("/encrypt-local-folder")
def encrypt_local_folder(request: Request, picker=Depends(get_local_encryption_picker),
                         tools: ToolsService = Depends(get_tools_service)):
    _require_local_encryption_request(request)
    try:
        folder = picker()
        if folder is None:
            return {"cancelled": True}
        return ToolsLocalFolderEncryptionService(tools=tools, files=ToolsLocalFolderGateway(folder)).encrypt()
    except (ToolsError, OSError, RuntimeError) as exc:
        message = str(exc) if isinstance(exc, ToolsError) else "Could not read the selected folder. Check folder access and try again."
        raise HTTPException(422, message) from exc


@router.post("/encrypt-folder")
def encrypt_folder(files: list[UploadFile] = File(...), relative_paths: str = Form(...),
                   tools: ToolsService = Depends(get_tools_service), settings: Settings = Depends(get_settings)):
    try:
        paths = validate_folder_paths(json.loads(relative_paths))
        # Directory pickers send the relative path as multipart filename; ordinary
        # file clients send only the basename. Never trust either as a disk path.
        if len(paths) != len(files) or any(
            file.filename not in {path.name, path.as_posix()} for file, path in zip(files, paths)
        ):
            raise ToolsError("The folder file list changed. Select the folder again.")
    except (ValueError, TypeError) as exc:
        detail = str(exc) if isinstance(exc, ToolsError) else "The folder file list is invalid. Select it again."
        raise HTTPException(422, detail) from exc
    root = Path(tempfile.mkdtemp(prefix="tools-encrypt-folder-", dir=settings.data_dir))
    output = root / "Encrypted_Folder.zip"
    try:
        sources = []
        total = 0
        for index, (file, relative) in enumerate(zip(files, paths)):
            source = root / "uploads" / str(index) / relative.name
            source.parent.mkdir(parents=True)
            size = 0
            with source.open("xb") as stream:
                while block := file.file.read(1024 * 1024):
                    size += len(block)
                    total += len(block)
                    if size > MAX_FILE_BYTES or total > MAX_TOTAL_BYTES:
                        raise HTTPException(413, "Folder uploads allow up to 100 MB per file and 500 MB in total.")
                    stream.write(block)
            sources.append((source, relative))
        service = ToolsFolderEncryptionService(tools=tools, archives=ToolsFolderArchiveGateway())
        summary = service.encrypt(sources, output=output)
    except Exception as exc:
        shutil.rmtree(root)
        if isinstance(exc, ToolsError):
            raise HTTPException(422, str(exc)) from exc
        raise
    return FileResponse(output, filename=output.name, media_type="application/zip",
        headers={"X-Encryption-Summary": json.dumps(summary),
                 "Access-Control-Expose-Headers": "Content-Disposition, X-Encryption-Summary"},
        background=BackgroundTask(shutil.rmtree, root))
