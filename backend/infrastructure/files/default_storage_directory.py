"""Create only an unconfigured default root; never recreate an offline configured root."""
from pathlib import Path
import tempfile
from backend.infrastructure.project_library.files import checked_path

class DefaultStorageDirectory:
    def existing(self, value: Path) -> Path:
        try:
            root = checked_path(value)
            if not root.is_dir():
                raise ValueError("Expected a folder")
            return root
        except (OSError, ValueError) as error:
            raise ValueError("The configured folder is unavailable. Choose another location in Settings.") from error

    def create(self, value: Path) -> Path:
        try:
            root = checked_path(value, must_exist=False)
            if not Path(root.anchor).is_dir():
                raise OSError("The default drive is unavailable")
            root.mkdir(parents=True, exist_ok=True)
            root = checked_path(root)
            with tempfile.TemporaryFile(dir=root):
                pass
            return root
        except (OSError, ValueError) as error:
            raise ValueError("The default folder cannot be created. Choose another location in Settings.") from error
