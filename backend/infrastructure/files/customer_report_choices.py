"""Store explicit customer-content choices under the owning data instance."""
from hashlib import sha256
import json
import os
from pathlib import Path
from uuid import uuid4


class CustomerReportChoices:
    def __init__(self, root: Path):
        self.root = Path(root)

    def _path(self, scope, digest):
        key = sha256(f"{scope}\0{digest}".encode()).hexdigest()
        return self.root / key[:2] / (key + ".json")

    def read(self, scope, digest):
        try:
            return json.loads(self._path(scope, digest).read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {}

    def remember(self, scope, digest, decisions):
        if not decisions:
            return
        target = self._path(scope, digest)
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(f".{uuid4().hex}.tmp")
        try:
            temporary.write_text(json.dumps(decisions, ensure_ascii=False), encoding="utf-8")
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)
