"""Resolve the current user's Documents folder without creating or moving files."""
import ctypes
import os
from pathlib import Path
from uuid import UUID


def user_documents_directory() -> Path:
    if os.name != "nt":
        return Path.home() / "Documents"
    from ctypes import wintypes
    folder_id = (ctypes.c_byte * 16).from_buffer_copy(UUID("FDD39AD0-238F-46AF-ADB4-6C85480369C7").bytes_le)
    pointer = ctypes.c_void_p()
    shell = ctypes.WinDLL("shell32", use_last_error=True)
    shell.SHGetKnownFolderPath.argtypes = [ctypes.c_void_p, wintypes.DWORD, wintypes.HANDLE, ctypes.POINTER(ctypes.c_void_p)]
    shell.SHGetKnownFolderPath.restype = ctypes.c_long
    result = shell.SHGetKnownFolderPath(ctypes.byref(folder_id), 0, None, ctypes.byref(pointer))
    try:
        if result != 0 or not pointer.value:
            raise ValueError("Documents is unavailable. Set the Materials library folder in Settings.")
        return Path(ctypes.wstring_at(pointer))
    finally:
        if pointer.value:
            ole = ctypes.WinDLL("ole32")
            ole.CoTaskMemFree.argtypes = [ctypes.c_void_p]
            ole.CoTaskMemFree.restype = None
            ole.CoTaskMemFree(pointer)
