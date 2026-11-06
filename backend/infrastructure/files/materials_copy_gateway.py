"""Copy a retained request into a new, exclusively-owned materials directory."""
from __future__ import annotations

import shutil
from pathlib import Path


from backend.application.material_names import validate_material_name

def checked_directory(path: Path) -> Path:
    if not path.is_absolute() or not path.is_dir():
        raise ValueError(f'Materials folder is not available: {path}. Check Settings.')
    for item in (path, *path.parents):
        if item.is_symlink() or (getattr(item.lstat(), 'st_file_attributes', 0) & 0x400):
            raise ValueError(f'Redirected folders cannot be used: {item}')
    return path.resolve()


class MaterialsCopyGateway:
    checked_directory = staticmethod(checked_directory)

    def save(self, root: Path, name: str, files: list[tuple[Path, str]]) -> Path:
        root = checked_directory(root)
        target = root / validate_material_name(name)
        # mkdir is exclusive. Never merge with or replace any pre-existing folder.
        try:
            target.mkdir()
        except FileExistsError as exc:
            raise ValueError('This folder already exists. Choose a different name.') from exc
        identity = (target.stat().st_dev, target.stat().st_ino)
        try:
            for source, destination in files:
                checked_directory(target)
                if (target.stat().st_dev, target.stat().st_ino) != identity:
                    raise ValueError("The target folder changed during copying. Check the destination.")
                output = target / validate_material_name(destination)
                with source.open('rb') as reader, output.open('xb') as writer:
                    shutil.copyfileobj(reader, writer)
            return target
        except Exception as original:
            # Do not delete by pathname after failure: another process may have
            # replaced an item between verification and removal.
            raise ValueError(f"Could not complete copying: {original}. Partial files may remain at {target}; check them before retrying with a new name.") from original
