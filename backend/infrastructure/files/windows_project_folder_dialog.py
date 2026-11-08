"""Windows Common Item Dialog for a single existing project directory.

Use the native IFileOpenDialog folder mode instead of SHBrowseForFolder's old tree.
The vtable slots below follow the Windows SDK IFileDialog and IShellItem ABI.
"""
from __future__ import annotations

import ctypes
from ctypes import wintypes
from pathlib import Path
from uuid import UUID

from backend.infrastructure.files.windows_dialog_layout import compact_folder_dialog


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
        # PICKFOLDERS | FORCEFILESYSTEM | PATHMUSTEXIST | NOCHANGEDIR | DONTADDTORECENT
        flags = (options.value | 0x20 | 0x40 | 0x800 | 0x8 | 0x02000000) & ~0x200
        _check(_call(dialog, 9, wintypes.LONG, (wintypes.DWORD,), flags))
        _check(_call(dialog, 17, wintypes.LONG, (wintypes.LPCWSTR,), "Import Projects — choose one project folder"))
        _check(_call(dialog, 18, wintypes.LONG, (wintypes.LPCWSTR,), "Select folder"))
        with compact_folder_dialog():
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
