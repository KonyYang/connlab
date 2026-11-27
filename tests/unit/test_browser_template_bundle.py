import hashlib
import json
from zipfile import ZipFile

import pytest

from scripts.stage_browser_templates import stage_bundle


def test_bundle_keeps_exact_template_bytes_and_empty_structure(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    template = source / "FDQF-E-036 Test Record Template-Even.docx"
    template.write_bytes(b"custom header and original layout")
    (source / "E-3718 filled request.docx").write_bytes(b"private example")
    manifest = {"files": {"test_record": {"name": template.name,
                "sha256": hashlib.sha256(template.read_bytes()).hexdigest()}},
                "directories": ["project/Title/E-mail", "project/Source Book"]}
    bundle = tmp_path / "templates.zip"
    stage_bundle(manifest, source, bundle)
    with ZipFile(bundle) as archive:
        assert set(archive.namelist()) == {
            template.name, "manifest.json", "project/Title/E-mail/", "project/Source Book/"
        }
        assert archive.read(template.name) == template.read_bytes()
        assert json.loads(archive.read("manifest.json")) == manifest
    template.write_bytes(b"changed")
    retry = tmp_path / "next.zip"
    with pytest.raises(ValueError, match="FDQF-E-036"):
        stage_bundle(manifest, source, retry)
    assert not retry.exists()
