"""Windows Common Item Dialog for existing local files and folders.

Use the native IFileOpenDialog folder mode instead of SHBrowseForFolder's old tree.
The vtable slots below follow the Windows SDK IFileDialog and IShellItem ABI.
"""
from __future__ import annotations

import ctypes
from ctypes import wintypes
from pathlib import Path
from uuid import UUID

from backend.infrastructure.files.windows_dialog_layout import compact_folder_dialog


_PROJECT_TITLE = "Import Projects — choose one project folder"
_OFFICE_FILTER = "*.doc;*.docx;*.xls;*.xlsx;*.ppt;*.pptx"


class _FilterSpec(ctypes.Structure):
    _fields_ = [("name", wintypes.LPCWSTR), ("pattern", wintypes.LPCWSTR)]


class _Guid(ctypes.Structure):
    _fields_ = [("data1", wintypes.DWORD), ("data2", wintypes.WORD),
                ("data3", wintypes.WORD), ("data4", ctypes.c_ubyte * 8)]


def _ole32():
    library = ctypes.WinDLL("ole32")
    library.CoCreateInstance.argtypes = [ctypes.POINTER(_Guid), ctypes.c_void_p,
        wintypes.DWORD, ctypes.POINTER(_Guid), ctypes.POINTER(ctypes.c_void_p)]
    library.CoCreateInstance.restype = wintypes.LONG
    library.CoTaskMemFree.argtypes = [ctypes.c_void_p]
    library.CoTaskMemFree.restype = None
    return library


def _call(interface, index, result_type, argtypes=(), *args):
    table = ctypes.cast(interface, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
    method = ctypes.WINFUNCTYPE(result_type, ctypes.c_void_p, *argtypes)(table[index])
    return method(interface, *args)


def _check(result):
    if result < 0:
        raise ctypes.WinError(result)


def pick_project_folder() -> Path | None:
    return _pick_existing_path(_PROJECT_TITLE, "Select folder", folder=True)


def pick_encryption_source(*, folder: bool) -> Path | None:
    """Choose an Office source in front of the window that launched the picker."""
    import pywintypes

    title = "Select folder to encrypt files" if folder else "Select Office file to encrypt"
    try:
        return _pick_existing_path(title, "Select folder" if folder else "Select file", folder=folder, topmost=True)
    except (pywintypes.com_error, pywintypes.error) as exc:
        raise OSError("Could not open the Windows encryption picker.") from exc


def _pick_existing_path(title: str, button: str, *, folder: bool, topmost: bool = False) -> Path | None:
    import pythoncom
    import win32gui

    owner = win32gui.GetForegroundWindow()
    # API work runs in a worker thread. Each invocation owns its STA and interfaces.
    pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)
    dialog, item, name = ctypes.c_void_p(), ctypes.c_void_p(), ctypes.c_void_p()
    library = None
    try:
        library = _ole32()
        clsid = _Guid.from_buffer_copy(UUID("dc1c5a9c-e88a-4dde-a5a1-60f82a20aef7").bytes_le)
        iid = _Guid.from_buffer_copy(UUID("d57c7288-d4ad-4768-be02-9d969532d960").bytes_le)
        _check(library.CoCreateInstance(ctypes.byref(clsid), None, 1, ctypes.byref(iid), ctypes.byref(dialog)))
        options = wintypes.DWORD()
        _check(_call(dialog, 10, wintypes.LONG, (ctypes.POINTER(wintypes.DWORD),), ctypes.byref(options)))
        # FORCEFILESYSTEM | PATHMUSTEXIST | NOCHANGEDIR | DONTADDTORECENT,
        # then choose exactly one existing file or directory.
        flags = (options.value | 0x40 | 0x800 | 0x8 | 0x02000000) & ~(0x200 | 0x20 | 0x1000)
        flags |= 0x20 if folder else 0x1000  # PICKFOLDERS or FILEMUSTEXIST
        _check(_call(dialog, 9, wintypes.LONG, (wintypes.DWORD,), flags))
        if not folder:
            filters = (_FilterSpec * 1)(_FilterSpec("Word, Excel and PowerPoint files", _OFFICE_FILTER))
            _check(_call(dialog, 4, wintypes.LONG, (wintypes.UINT, ctypes.POINTER(_FilterSpec)), len(filters), filters))
        _check(_call(dialog, 17, wintypes.LONG, (wintypes.LPCWSTR,), title))
        _check(_call(dialog, 18, wintypes.LONG, (wintypes.LPCWSTR,), button))
        with compact_folder_dialog(title, topmost=topmost):
            result = _call(dialog, 3, wintypes.LONG, (wintypes.HWND,), owner)
        if result & 0xFFFFFFFF == 0x800704C7:
            return None
        _check(result)
        _check(_call(dialog, 20, wintypes.LONG, (ctypes.POINTER(ctypes.c_void_p),), ctypes.byref(item)))
        # SIGDN_FILESYSPATH returns an allocated UTF-16 path, not a shell display name.
        _check(_call(item, 5, wintypes.LONG,
            (wintypes.DWORD, ctypes.POINTER(ctypes.c_void_p)), 0x80058000, ctypes.byref(name)))
        return Path(ctypes.wstring_at(name))
    finally:
        if name.value and library is not None:
            library.CoTaskMemFree(name)
        if item.value:
            _call(item, 2, wintypes.ULONG)
        if dialog.value:
            _call(dialog, 2, wintypes.ULONG)
        pythoncom.CoUninitialize()
