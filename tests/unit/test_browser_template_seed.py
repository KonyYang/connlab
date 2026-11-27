import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from zipfile import ZipFile

from docx import Document
from openpyxl import Workbook

from backend.infrastructure.files.browser_template_seed import seed_browser_templates
from scripts.stage_browser_templates import stage_bundle


def make_bundle(tmp_path):
    manifest = json.loads((Path(__file__).parents[2] / "packaging/browser_templates.json").read_text("utf-8"))
    src = tmp_path / "source"
    src.mkdir()
    for template in manifest["files"].values():
        name = template["name"]
        file = src / name
        if name.endswith(".docx"):
            doc = Document()
            doc.sections[0].header.paragraphs[0].text = "Customized header"
            doc.save(file)
        elif "E-033" in name:
            fixture = Path(__file__).parents[1] / "fixtures/ir_dwv/IR_DWV_Template.xlsx"
            file.write_bytes(fixture.read_bytes())
        else:
            book = Workbook()
            book.save(file)
            book.close()
        template["sha256"] = hashlib.sha256(file.read_bytes()).hexdigest()
    bundle = tmp_path / "seed.zip"
    stage_bundle(manifest, src, bundle)
    return manifest, bundle


def test_concurrent_new_install_preserves_templates_and_empty_structure(tmp_path):
    manifest, bundle = make_bundle(tmp_path)
    target = tmp_path / "Template"
    target.mkdir()
    with ThreadPoolExecutor(max_workers=3) as pool:
        assert list(pool.map(lambda _: seed_browser_templates(target, bundle), range(3))) == [[], [], []]
    for directory in manifest["directories"]:
        assert (target / directory).is_dir()
    assert {p.name for p in target.iterdir() if p.is_file()} == {s["name"] for s in manifest["files"].values()}
    for spec in manifest["files"].values():
        assert hashlib.sha256((target / spec["name"]).read_bytes()).hexdigest() == spec["sha256"]


def test_existing_unique_and_ambiguous_purposes_are_never_replaced(tmp_path):
    manifest, bundle = make_bundle(tmp_path)
    target = tmp_path / "Registered"
    target.mkdir()
    fee = target / "Site FDQF-E-176 r7.xlsx"
    book = Workbook()
    book.active["A1"] = "Manual adjustment"
    book.save(fee)
    book.close()
    before = fee.read_bytes()
    for name in ["Site E-3707_H.docx", "Old E-3707_H.docx"]:
        Document().save(target / name)
    warnings = seed_browser_templates(target, bundle)
    assert len(warnings) == 1 and all(name in warnings[0] for name in ["Site E-3707_H", "Old E-3707_H", str(target)])
    assert fee.read_bytes() == before
    assert not (target / manifest["files"]["fee_evaluation"]["name"]).exists()
    assert not (target / manifest["files"]["internal_report"]["name"]).exists()
    assert (target / manifest["files"]["customer_report"]["name"]).is_file()
    assert seed_browser_templates(target, bundle) == warnings


def test_invalid_field_copy_and_missing_or_unreadable_source_preserved(tmp_path):
    manifest, bundle = make_bundle(tmp_path)
    target = tmp_path / "Registered"
    assert seed_browser_templates(target, bundle)
    assert not target.exists()
    target.mkdir()
    candidate = target / "E-4515 field.docx"
    candidate.write_bytes(b"manual data")
    assert any(candidate.name in w for w in seed_browser_templates(target, bundle))
    assert candidate.read_bytes() == b"manual data"
    assert not (target / manifest["files"]["customer_report"]["name"]).exists()
    broken = tmp_path / "broken.zip"
    with ZipFile(bundle) as src, ZipFile(broken, "w") as dst:
        for name in src.namelist():
            data = src.read(name)
            dst.writestr(name, data + b"bad" if name == manifest["files"]["ir_dwv"]["name"] else data)
    clean = tmp_path / "NewTemplate"
    clean.mkdir()
    assert seed_browser_templates(clean, broken)
    assert not list(clean.iterdir())

def test_existing_alternate_layout_and_ambiguous_layouts(tmp_path):
    manifest, bundle = make_bundle(tmp_path)
    target = tmp_path / "Template"
    target.mkdir()
    custom = target / "Site" / "Custom title"
    for subfolder in ["E-mail", "Photos", "Test results/Final Examination", "Submitted Material"]:
        (custom / subfolder).mkdir(parents=True)
    assert seed_browser_templates(target, bundle) == []
    assert not (target / manifest["directories"][0]).exists()
    other = target / "Alternate"
    for subfolder in ["E-mail", "Photos", "Test results/Final Examination", "Submitted Material"]:
        (other / subfolder).mkdir(parents=True)
    warnings = seed_browser_templates(target, bundle)
    assert len(warnings) == 1 and str(custom) in warnings[0] and str(other) in warnings[0]
    assert not (target / manifest["directories"][0]).exists()


def test_redirected_template_layout_never_writes_outside_registered_location(tmp_path):
    import os

    manifest, bundle = make_bundle(tmp_path)
    target = tmp_path / "Template"
    target.mkdir()
    outside = tmp_path / "Outside"
    outside.mkdir()
    sentinel = outside / "sentinel"
    sentinel.write_bytes(b"protected")
    child = target / Path(manifest["directories"][0]).parts[0]
    if os.name == "nt":
        import _winapi
        _winapi.CreateJunction(str(outside), str(child))
    else:
        child.symlink_to(outside, target_is_directory=True)
    warnings = seed_browser_templates(target, bundle)
    assert any("layout" in w.lower() for w in warnings)
    assert list(outside.iterdir()) == [sentinel] and sentinel.read_bytes() == b"protected"


def test_interrupted_file_copy_can_resume_in_a_new_process(tmp_path):
    import subprocess
    import sys

    manifest, bundle = make_bundle(tmp_path)
    target = tmp_path / "Template"
    target.mkdir()
    entry = (
        "from pathlib import Path; import os,sys; "
        "from backend.infrastructure.files.browser_template_seed import seed_browser_templates; "
    )
    cmd = [sys.executable, "-B", "-c"]
    args = [str(target), str(bundle)]
    interrupt = entry + "os.fsync=lambda fd: os._exit(73); seed_browser_templates(*map(Path,sys.argv[1:]))"
    resume = entry + "sys.exit(bool(seed_browser_templates(*map(Path,sys.argv[1:]))))"
    assert subprocess.run(cmd + [interrupt] + args, check=False).returncode == 73
    assert not list(target.glob("*.docx")) and not list(target.glob("*.xlsx"))
    subprocess.run(cmd + [resume] + args, check=True)
    for spec in manifest["files"].values():
        assert hashlib.sha256((target / spec["name"]).read_bytes()).hexdigest() == spec["sha256"]


def test_explicit_word_and_ir_templates_take_precedence_over_seed_folder(tmp_path):
    manifest, bundle = make_bundle(tmp_path)
    folder = tmp_path / "Managed templates"
    folder.mkdir()
    record = tmp_path / "Site record.docx"
    Document().save(record)
    existing = record.read_bytes()
    missing = tmp_path / "Site IR.xlsx"
    warnings = seed_browser_templates(folder, bundle, overrides={"test_record": record, "ir_dwv": missing})
    assert len(warnings) == 1 and str(missing) in warnings[0]
    assert record.read_bytes() == existing
    assert not (folder / manifest["files"]["test_record"]["name"]).exists()
    assert not (folder / manifest["files"]["ir_dwv"]["name"]).exists()
    assert (folder / manifest["files"]["fee_evaluation"]["name"]).is_file()


def test_office_owner_files_are_not_candidates_for_missing_or_existing_templates(tmp_path):
    manifest, bundle = make_bundle(tmp_path)
    target = tmp_path / "Template"
    target.mkdir()
    for purpose in ("test_record", "customer_feedback"):
        (target / ("~$" + manifest["files"][purpose]["name"])).write_bytes(b"Office owner")
    assert not seed_browser_templates(target, bundle)
    assert not seed_browser_templates(target, bundle)
    for purpose in ("test_record", "customer_feedback"):
        assert (target / manifest["files"][purpose]["name"]).is_file()
        assert (target / ("~$" + manifest["files"][purpose]["name"])).read_bytes() == b"Office owner"
