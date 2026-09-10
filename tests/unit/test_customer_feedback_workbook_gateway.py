from __future__ import annotations

from pathlib import Path
import os
import shutil

import pytest
from openpyxl import Workbook, load_workbook

from backend.infrastructure.office.customer_feedback_workbook_gateway import (
    CustomerFeedbackWorkbookGateway,
    CustomerFeedbackWorkbookGatewayError,
)


def test_customer_feedback_workbook_gateway_keeps_python_xlsx_engine() -> None:
    source = Path(
        "backend/infrastructure/office/customer_feedback_workbook_gateway.py"
    ).read_text(encoding="utf-8")

    assert "openpyxl" in source
    assert "win32com" not in source
    assert "DispatchEx" not in source


def test_customer_feedback_workbook_gateway_copies_template_without_overwriting_source(
    tmp_path: Path,
) -> None:
    template = tmp_path / "E-4243_D Customer Feedback Form.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet["A1"] = "LTR Number"
    sheet["A2"] = "Product Description"
    sheet["A3"] = "Requestor"
    workbook.save(template)
    output = tmp_path / "generated" / "feedback.xlsx"

    result_path, warnings = CustomerFeedbackWorkbookGateway().generate(
        template_path=template,
        output_path=output,
        identity={
            "ltr_number": "DL-2026-05-003",
            "product_name": "Connector",
            "requestor": "MP Cao",
        },
    )

    assert result_path == output
    generated = load_workbook(output)
    sheet = generated.active
    assert sheet["B1"].value == "DL-2026-05-003"
    assert sheet["B2"].value == "Connector"
    assert sheet["B3"].value == "MP Cao"
    assert warnings == ()
    source = load_workbook(template)
    assert source.active["B1"].value is None


def test_customer_feedback_workbook_gateway_fills_sample_compatible_header_offsets(
    tmp_path: Path,
) -> None:
    template = tmp_path / "E-4243_D Customer Feedback Form.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Customer Feedback Form"
    sheet["A7"] = "Customer Name"
    sheet["D7"] = "Telephone No."
    sheet["F7"] = "Site"
    sheet["A9"] = "Project Details\n( if applicable)"
    sheet["F9"] = "Work Request No."
    sheet["A11"] = "From Date\n(mm/dd/yy)"
    sheet["D11"] = "To Date\n(mm/dd/yy)"
    sheet["A13"] = "GES Team"
    workbook.save(template)
    output = tmp_path / "generated" / "feedback.xlsx"

    result_path, warnings = CustomerFeedbackWorkbookGateway().generate(
        template_path=template,
        output_path=output,
        identity={
            "ltr_number": "DL-BI",
            "product_name": "Connector BI Qualification",
            "requestor": "Requester BI",
            "phone": "12345",
            "location": "Dongguan",
            "received_date": "20 Jun 2026",
            "estimated_completion_date": "02 Jul 2026",
            "lab": "Dongguan Lab",
        },
    )

    assert result_path == output
    generated = load_workbook(output)
    sheet = generated["Customer Feedback Form"]
    assert sheet["C7"].value == "Requester BI"
    assert sheet["E7"].value == "12345"
    assert sheet["I7"].value == "Dongguan"
    assert sheet["C9"].value == "Connector BI Qualification"
    assert sheet["I9"].value == "DL-BI"
    assert sheet["C11"].value == "20 Jun 2026"
    assert sheet["E11"].value == "02 Jul 2026"
    assert sheet["C13"].value == "Dongguan Lab"
    assert warnings == ()


def test_customer_feedback_workbook_gateway_blocks_missing_required_identity_anchor(
    tmp_path: Path,
) -> None:
    template = tmp_path / "E-4243_D Customer Feedback Form.xlsx"
    workbook = Workbook()
    workbook.active["A1"] = "Customer Name"
    workbook.save(template)

    with pytest.raises(CustomerFeedbackWorkbookGatewayError, match="Work Request No"):
        CustomerFeedbackWorkbookGateway().generate(
            template_path=template,
            output_path=tmp_path / "generated" / "feedback.xlsx",
            identity={
                "ltr_number": "DL-BI",
                "product_name": "Connector BI Qualification",
            },
        )


def test_customer_feedback_workbook_gateway_rejects_non_xlsx_template(tmp_path: Path) -> None:
    template = tmp_path / "E-4243.xls"
    template.write_bytes(b"template")

    with pytest.raises(CustomerFeedbackWorkbookGatewayError, match=".xlsx"):
        CustomerFeedbackWorkbookGateway().generate(
            template_path=template,
            output_path=tmp_path / "out.xlsx",
            identity={},
        )


def test_customer_feedback_workbook_gateway_rejects_output_equal_to_template(
    tmp_path: Path,
) -> None:
    template = tmp_path / "E-4243.xlsx"
    template.write_bytes(b"template")

    with pytest.raises(CustomerFeedbackWorkbookGatewayError, match="must not overwrite"):
        CustomerFeedbackWorkbookGateway().generate(
            template_path=template,
            output_path=template,
            identity={},
        )


@pytest.mark.skipif(not hasattr(getattr(shutil, "_winapi", None), "CopyFile2"), reason="Windows CopyFile2 boundary")
def test_customer_feedback_supports_long_template_and_output_without_windows_policy_change(
    tmp_path: Path, monkeypatch,
) -> None:
    directory = tmp_path / ("templates" * 12) / ("nested" * 12)
    template = directory / "Customer Feedback Form.xlsx"
    output = directory / "generated" / "DL-2026-08-079 Customer Feedback Form_Even Yang.xlsx"
    assert len(str(template)) >= 260
    template_io = Path("\\\\?\\" + str(template))
    output_io = Path("\\\\?\\" + str(output))
    template_io.parent.mkdir(parents=True)
    book = Workbook()
    book.active["A1"] = "LTR Number"
    book.active["A2"] = "Product Description"
    book.active["C3"] = "=1+2"
    book.save(template_io)
    book.close()
    source_bytes = template_io.read_bytes()
    native_copy = shutil._winapi.CopyFile2

    def copy_on_windows_without_long_path_policy(source, destination, flags):
        for path in (source, destination):
            if len(str(path)) >= 260 and not str(path).startswith("\\\\?\\"):
                error = FileNotFoundError("Reported CopyFile2 MAX_PATH failure")
                error.winerror = 3
                raise error
        return native_copy(source, destination, flags)

    monkeypatch.setattr(shutil._winapi, "CopyFile2", copy_on_windows_without_long_path_policy)
    result, warnings = CustomerFeedbackWorkbookGateway().generate(
        template_path=template, output_path=output,
        identity={"ltr_number": "DL-2026-08-079", "product_name": "Connector"},
    )
    assert result == output
    assert warnings == ()
    generated = load_workbook(output_io)
    try:
        assert generated.active["B1"].value == "DL-2026-08-079"
        assert generated.active["B2"].value == "Connector"
        assert generated.active["C3"].value == "=1+2"
    finally:
        generated.close()
    assert template_io.read_bytes() == source_bytes


@pytest.mark.skipif(not hasattr(getattr(shutil, "_winapi", None), "CopyFile2"), reason="Windows filesystem boundary")
@pytest.mark.parametrize("already_extended", [False, True])
def test_customer_feedback_uses_extended_unc_for_all_workbook_io(tmp_path, monkeypatch, already_extended):
    import io
    import ntpath

    template = tmp_path / "template.xlsx"
    workbook = Workbook()
    workbook.active["A1"] = "LTR Number"
    workbook.save(template)
    workbook.close()
    original = template.read_bytes()
    share = "\\\\connlab-test\\share\\"
    extended_share = "\\\\?\\UNC\\connlab-test\\share\\"

    def isolated_share_path(path):
        if not isinstance(path, (str, os.PathLike)):
            return path
        value = os.fspath(path)
        if value.startswith((share, extended_share)):
            assert value.startswith(extended_share), "UNC I/O must not depend on LongPathsEnabled"
            relative = value[len(extended_share):]
            return str(Path("\\\\?\\" + str(tmp_path)) / relative)
        return path

    # Emulate a share at the OS/filesystem boundary; no network or admin share is used.
    native_stat, native_mkdir = os.stat, os.mkdir
    native_open, native_final = io.open, ntpath._getfinalpathname
    native_copy = shutil._winapi.CopyFile2
    monkeypatch.setattr(os, "stat", lambda path, *a, **kw: native_stat(isolated_share_path(path), *a, **kw))
    monkeypatch.setattr(os, "mkdir", lambda path, *a, **kw: native_mkdir(isolated_share_path(path), *a, **kw))
    monkeypatch.setattr(io, "open", lambda path, *a, **kw: native_open(isolated_share_path(path), *a, **kw))
    monkeypatch.setattr(ntpath, "_getfinalpathname", lambda path: native_final(isolated_share_path(path)))
    monkeypatch.setattr(shutil._winapi, "CopyFile2", lambda src, dst, flags:
                        native_copy(isolated_share_path(src), isolated_share_path(dst), flags))
    prefix = extended_share if already_extended else share
    output = Path(prefix + "generated\\feedback.xlsx")
    result, warnings = CustomerFeedbackWorkbookGateway().generate(
        template_path=Path(prefix + "template.xlsx"), output_path=output,
        identity={"ltr_number": "DL-UNC"},
    )
    assert result == output
    assert warnings == ()
    generated = load_workbook(tmp_path / "generated" / "feedback.xlsx")
    try:
        assert generated.active["B1"].value == "DL-UNC"
    finally:
        generated.close()
    assert template.read_bytes() == original
