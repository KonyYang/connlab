"""Use extended Windows paths for disk access; keep ordinary paths in the catalog."""
import os
import ntpath
from pathlib import Path

from .files import checked_path


def material_io_path(value) -> Path:
    path = Path(value).expanduser()
    if os.name != "nt" or not path.is_absolute():
        return path
    name = str(path)
    # Verbatim paths do not interpret '..' like ordinary Win32 paths.
    if ".." in path.parts:
        raise ValueError("Choose a material path without parent traversal.")
    if name.startswith("\\\\?\\") and (name[:8].upper() == "\\\\?\\UNC\\" or
                                       len(path.drive) == 6 and path.drive.endswith(":")):
        return path
    if name.startswith(("\\\\?\\", "\\\\.\\")):
        raise ValueError("Choose a drive or shared folder for materials.")
    if name.startswith("\\\\"):
        return Path("\\\\?\\UNC\\" + name[2:])
    return Path("\\\\?\\" + name)


def checked_material_path(value, *, must_exist=True):
    return checked_path(material_io_path(value), must_exist=must_exist)


def display_path(path: Path) -> Path:
    if os.name == "nt":
        # A verbatim-only name can refer to a different file or device in the shell.
        for part in path.parts[1:]:
            reserved = ntpath.isreserved(part) if hasattr(ntpath, "isreserved") else Path(part).is_reserved()
            if reserved or part.endswith((".", " ")):
                raise ValueError("Windows cannot address this name normally. Open its parent folder instead.")
        name = str(path)
        if name[:8].upper() == "\\\\?\\UNC\\":
            return Path("\\\\" + name[8:])
        if name.startswith("\\\\?\\") and len(path.drive) == 6 and path.drive.endswith(":"):
            return Path(name[4:])
    return path


def shell_path(path: Path) -> str:
    """Prefer an existing short alias for Windows applications with legacy path limits."""
    name = str(path)
    if os.name != "nt" or len(name.encode("utf-16-le")) // 2 < 260:
        return name

    import ctypes
    from ctypes import wintypes

    native = str(material_io_path(path))
    short_name = ctypes.WinDLL("kernel32").GetShortPathNameW
    short_name.argtypes = (wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD)
    short_name.restype = wintypes.DWORD
    size = short_name(native, None, 0)
    if size:
        buffer = ctypes.create_unicode_buffer(size)
        if 0 < short_name(native, buffer, size) < size:
            alias = display_path(Path(buffer.value))
            # An 8.3 alias can give .docx the .DOC extension. Keep the file association.
            for candidate in (alias.parent / path.name, alias):
                if candidate.suffix.casefold() == path.suffix.casefold() and len(str(candidate).encode("utf-16-le")) // 2 < 260:
                    return str(candidate)
    return native
