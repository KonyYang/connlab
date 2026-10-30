"""Folder uploads are isolated copies, never client-addressed server directories."""
import json
import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from backend.api.dependencies import get_settings, get_tools_service
from backend.application.tools_service import ToolsError, ToolsService
from backend.application.tools_folder_encryption_service import ToolsFolderEncryptionService, validate_folder_paths
from backend.infrastructure.files.tools_folder_archive_gateway import ToolsFolderArchiveGateway
from backend.shared.config import Settings

router = APIRouter()
MAX_FILE_BYTES = 100 * 1024 * 1024
MAX_TOTAL_BYTES = 500 * 1024 * 1024


@router.post("/encrypt-folder")
def encrypt_folder(files: list[UploadFile] = File(...), relative_paths: str = Form(...),
                   tools: ToolsService = Depends(get_tools_service), settings: Settings = Depends(get_settings)):
    try:
        paths = validate_folder_paths(json.loads(relative_paths))
        if len(paths) != len(files) or any(file.filename != path.name for file, path in zip(files, paths)):
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
