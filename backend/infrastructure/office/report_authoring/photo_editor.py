"""Protected-report adapter around the deterministic OOXML photo slots."""
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from backend.infrastructure.office.office_protected_document_gateway import ProtectedWordPackageGateway
from backend.infrastructure.office.report_authoring.photo_slots import (
    inspect_photo_slots, read_photo_slot, replace_photo_slots, PhotoReplacement,
)


class ReportPhotoEditor:
    def __init__(self, protected=None):
        self.protected = protected or ProtectedWordPackageGateway()

    def inspect(self, source):
        with self.protected.readable_copy(source) as readable:
            return [asdict(slot) for slot in inspect_photo_slots(readable)]

    def read(self, source, slot_id):
        with self.protected.readable_copy(source) as readable:
            return read_photo_slot(readable, slot_id)

    def update(self, source, output, replacements):
        if output.exists():
            raise ValueError('Output already exists; report originals are never overwritten.')
        with TemporaryDirectory(prefix='connlab-photos-') as directory:
            changed = Path(directory)/'changed.docx'
            with self.protected.readable_copy(source) as readable:
                result = replace_photo_slots(readable, changed, [PhotoReplacement(**item) for item in replacements],
                    expected_source_sha256=sha256(readable.read_bytes()).hexdigest())
            protection = self.protected.stage_editable_copy(source, output)
            output.write_bytes(changed.read_bytes())
            self.protected.restore_password_protection(output, protection)
            return result.changed
