"""Build the portable browser server's pinned, read-only template seed archive."""

import argparse
import hashlib
from io import BytesIO
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


def stage_bundle(manifest: dict, source: Path, destination: Path) -> None:
    # Check the very bytes we archive, including the customized Word headers.
    buffer = BytesIO()
    with ZipFile(buffer, "w", compression=ZIP_DEFLATED) as archive:
        for template in manifest["files"].values():
            name = template["name"]
            data = (source / name).read_bytes()
            if hashlib.sha256(data).hexdigest() != template["sha256"]:
                raise ValueError(f"Template differs from the approved release manifest: {name}")
            archive.writestr(name, data)
        for directory in manifest["directories"]:
            archive.writestr(directory + "/", b"")
        archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False))
    with destination.open("xb") as output:
        output.write(buffer.getbuffer())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    manifest_path = Path(__file__).resolve().parents[1] / "packaging/browser_templates.json"
    stage_bundle(json.loads(manifest_path.read_text(encoding="utf-8")), args.source, args.destination)
