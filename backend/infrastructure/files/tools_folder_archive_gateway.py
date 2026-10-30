"""Package only verified encrypted copies and a password-free outcome report."""
import csv
from io import StringIO
from pathlib import Path, PurePosixPath
from typing import Sequence
from zipfile import ZIP_DEFLATED, ZipFile

from backend.application.tools_folder_encryption_service import FolderEncryptionEntry, secured_relative_path


def _csv_cell(value: str) -> str:
    return "'" + value if value.lstrip().startswith(("=", "+", "-", "@")) else value


class ToolsFolderArchiveGateway:
    def write(self, output: Path, entries: Sequence[FolderEncryptionEntry]) -> None:
        report = StringIO(newline="")
        writer = csv.writer(report)
        writer.writerow(("File", "Status", "Reason"))
        with ZipFile(output, "x", compression=ZIP_DEFLATED) as bundle:
            for entry in entries:
                writer.writerow(tuple(_csv_cell(value) for value in (entry.relative_path, entry.status, entry.reason)))
                if entry.status == "Encrypted" and entry.output_path is not None:
                    original = PurePosixPath(entry.relative_path)
                    name = secured_relative_path(original)
                    bundle.write(entry.output_path, str(name))
            bundle.writestr("EncryptionSummary.csv", "\ufeff" + report.getvalue())
