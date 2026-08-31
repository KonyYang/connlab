from hashlib import sha256
from pathlib import Path
import shutil

import pytest

from backend.application.current_report_update_service import CurrentReportArtifact
from backend.application.customer_report_projection_service import (
    CustomerReportGenerationCommand,
    CustomerReportProjectionError,
    CustomerReportProjectionService,
)
from backend.infrastructure.files.report_publication_gateway import (
    ReportPublicationGateway,
)


def test_official_customer_state_is_stale_when_internal_report_changed(tmp_path: Path) -> None:
    internal = _write(tmp_path / "DL-2026-04-015 Qualification Test Report_Rev_A.docx", b"internal-v2")
    customer = _write(
        tmp_path / "DL-2026-04-015-CR Qualification Test Report_Rev_A.docx",
        b"customer-v1",
    )
    writer = _Writer(source_fingerprint=sha256(b"internal-v1").hexdigest())
    service = _service(tmp_path, internal, writer=writer, customer=customer)

    state = service.get_state("project-1")

    assert state.status == "stale"
    assert state.mode == "official"
    assert state.file_name == customer.name
    assert state.internal_report_sha256 == sha256(b"internal-v2").hexdigest()
    assert state.generated_from_internal_sha256 == sha256(b"internal-v1").hexdigest()
    assert state.can_generate is True
    assert state.download_url_available is True


def test_official_generation_uses_current_internal_report_and_canonical_name(
    tmp_path: Path,
) -> None:
    internal = _write(tmp_path / "DL-2026-04-015 Qualification Test Report_Rev_A.docx", b"internal")
    template = _write(tmp_path / "E-4515_F Customer Test Report.docx", b"template")
    writer = _Writer()
    files = _Files()
    service = _service(tmp_path, internal, writer=writer, files=files)

    result = service.generate(
        CustomerReportGenerationCommand(
            project_id="project-1",
            template_path=template,
            expected_internal_report_sha256=_hash(internal),
            expected_customer_report_sha256=None,
        )
    )

    assert writer.sources == [internal]
    assert result.mode == "official"
    assert result.file_name == "DL-2026-04-015-CR Qualification Test Report_Rev_A.docx"
    assert result.archive_path is None
    assert result.source_report_sha256 == _hash(internal)
    assert result.file_path.is_file()


def test_existing_official_customer_requires_both_preview_fingerprints(
    tmp_path: Path,
) -> None:
    internal = _write(tmp_path / "DL-2026-04-015 Qualification Test Report_Rev_A.docx", b"internal")
    customer = _write(
        tmp_path / "DL-2026-04-015-CR Qualification Test Report_Rev_A.docx",
        b"customer-old",
    )
    template = _write(tmp_path / "E-4515_F Customer Test Report.docx", b"template")
    service = _service(tmp_path, internal, customer=customer)

    with pytest.raises(CustomerReportProjectionError, match="Preview the customer report again"):
        service.generate(
            CustomerReportGenerationCommand(
                project_id="project-1",
                template_path=template,
                expected_internal_report_sha256=_hash(internal),
                expected_customer_report_sha256=None,
            )
        )

    with pytest.raises(CustomerReportProjectionError, match="changed after preview"):
        service.generate(
            CustomerReportGenerationCommand(
                project_id="project-1",
                template_path=template,
                expected_internal_report_sha256=_hash(internal),
                expected_customer_report_sha256="0" * 64,
            )
        )
    assert customer.read_bytes() == b"customer-old"


def test_deleted_customer_after_preview_requires_explicit_regeneration_confirmation(
    tmp_path: Path,
) -> None:
    internal = _write(
        tmp_path / "DL-2026-04-015 Qualification Test Report_Rev_A.docx",
        b"internal",
    )
    customer = _write(
        tmp_path / "DL-2026-04-015-CR Qualification Test Report_Rev_A.docx",
        b"customer-old",
    )
    template = _write(
        tmp_path / "E-4515_F Customer Test Report.docx",
        b"template",
    )
    service = _service(
        tmp_path,
        internal,
        writer=_Writer(),
        files=ReportPublicationGateway(),
    )
    preview = service.get_state("project-1")
    customer.unlink()

    with pytest.raises(CustomerReportProjectionError) as error:
        service.generate(
            CustomerReportGenerationCommand(
                project_id="project-1",
                template_path=template,
                expected_internal_report_sha256=preview.internal_report_sha256,
                expected_customer_report_sha256=preview.file_sha256,
            )
        )

    assert getattr(error.value, "code", None) == "customer_report_missing_after_preview"
    assert not customer.exists()


def test_existing_official_customer_is_archived_and_replaced_atomically(
    tmp_path: Path,
) -> None:
    internal = _write(tmp_path / "DL-2026-04-015 Qualification Test Report_Rev_A.docx", b"internal")
    customer = _write(
        tmp_path / "DL-2026-04-015-CR Qualification Test Report_Rev_A.docx",
        b"customer-old",
    )
    template = _write(tmp_path / "E-4515_F Customer Test Report.docx", b"template")
    files = _Files()
    service = _service(tmp_path, internal, customer=customer, files=files)

    result = service.generate(
        CustomerReportGenerationCommand(
            project_id="project-1",
            template_path=template,
            expected_internal_report_sha256=_hash(internal),
            expected_customer_report_sha256=_hash(customer),
        )
    )

    assert result.changed is True
    assert result.archive_path is not None
    assert result.archive_path.read_bytes() == b"customer-old"
    assert customer.read_bytes() == b"internal|customer"


def test_managed_internal_report_generates_a_download_copy_without_publication(
    tmp_path: Path,
) -> None:
    managed = tmp_path / "managed"
    managed.mkdir()
    internal = _write(managed / "DL-2026-04-015 Qualification Test Report_Rev_A_Draft.docx", b"internal")
    template = _write(tmp_path / "E-4515_F Customer Test Report.docx", b"template")
    generated = tmp_path / "generated"
    service = CustomerReportProjectionService(
        current_reports=_CurrentReports(_current(internal, mode="managed_draft")),
        files=_Files(),
        writer=_Writer(),
        generated_root=generated,
    )

    result = service.generate(
        CustomerReportGenerationCommand(
            project_id="project-1",
            template_path=template,
            expected_internal_report_sha256=_hash(internal),
            expected_customer_report_sha256=None,
        )
    )

    assert result.mode == "managed_download"
    assert result.file_path.parent == generated / "project-1"
    assert result.file_name == "DL-2026-04-015-CR Qualification Test Report_Rev_A_Draft.docx"


def test_multiple_official_customer_reports_block_generation(tmp_path: Path) -> None:
    internal = _write(tmp_path / "DL-2026-04-015 Qualification Test Report_Rev_A.docx", b"internal")
    first = _write(tmp_path / "DL-2026-04-015-CR Report_Rev_A.docx", b"customer-1")
    second = _write(tmp_path / "DL-2026-04-015-CR Report_Rev_B.docx", b"customer-2")
    files = _Files()
    files.customer_reports = (first, second)
    service = _service(tmp_path, internal, files=files)

    state = service.get_state("project-1")

    assert state.status == "ambiguous"
    assert state.can_generate is False
    assert state.blockers


def test_existing_customer_is_not_replaced_if_internal_source_changes_during_generation(
    tmp_path: Path,
) -> None:
    internal = _write(tmp_path / "DL-2026-04-015 Qualification Test Report_Rev_A.docx", b"internal")
    customer = _write(
        tmp_path / "DL-2026-04-015-CR Qualification Test Report_Rev_A.docx",
        b"customer-old",
    )
    template = _write(tmp_path / "E-4515_F Customer Test Report.docx", b"template")
    service = CustomerReportProjectionService(
        current_reports=_CurrentReports(_current(internal)),
        files=ReportPublicationGateway(),
        writer=_MutatingWriter(_hash(internal)),
        generated_root=tmp_path / "generated",
    )

    with pytest.raises(CustomerReportProjectionError, match="changed during"):
        service.generate(
            CustomerReportGenerationCommand(
                project_id="project-1",
                template_path=template,
                expected_internal_report_sha256=_hash(internal),
                expected_customer_report_sha256=_hash(customer),
            )
        )

    assert customer.read_bytes() == b"customer-old"
    assert not list(tmp_path.glob(".*.stage.docx"))


def _service(
    tmp_path: Path,
    internal: Path,
    *,
    customer: Path | None = None,
    writer=None,
    files=None,
) -> CustomerReportProjectionService:
    file_gateway = files or _Files()
    if customer is not None:
        file_gateway.customer_reports = (customer,)
    return CustomerReportProjectionService(
        current_reports=_CurrentReports(_current(internal)),
        files=file_gateway,
        writer=writer or _Writer(),
        generated_root=tmp_path / "generated",
    )


def _current(path: Path, *, mode: str = "official") -> CurrentReportArtifact:
    return CurrentReportArtifact(
        status="ready",
        mode=mode,
        file_name=path.name,
        file_path=path,
        file_sha256=_hash(path),
        history_root=path.parent / "History" / "Report",
        folder_path=path.parent,
        official_folder_path=path.parent if mode == "official" else None,
    )


class _CurrentReports:
    def __init__(self, report: CurrentReportArtifact) -> None:
        self.report = report

    def get_current_report(self, project_id: str) -> CurrentReportArtifact:
        assert project_id == "project-1"
        return self.report


class _Writer:
    def __init__(self, source_fingerprint: str | None = None) -> None:
        self.source_fingerprint = source_fingerprint
        self.sources: list[Path] = []

    def generate_customer_report(self, *, source_path, template_path, output_path):
        self.sources.append(Path(source_path))
        Path(output_path).write_bytes(Path(source_path).read_bytes() + b"|customer")
        self.source_fingerprint = _hash(Path(source_path))
        return Path(output_path)

    def read_source_report_sha256(self, path: Path) -> str | None:
        return self.source_fingerprint


class _MutatingWriter(_Writer):
    def generate_customer_report(self, *, source_path, template_path, output_path):
        Path(output_path).write_bytes(b"generated-from-old-source")
        Path(source_path).write_bytes(b"internal-changed")
        return Path(output_path)


class _Files:
    def __init__(self) -> None:
        self.customer_reports: tuple[Path, ...] = tuple()

    def discover_customer_reports(self, *, folder: Path, dl_number: str):
        return self.customer_reports

    def fingerprint(self, path: Path) -> str:
        return _hash(path)

    def publish_generated_current(
        self,
        *,
        source_path,
        expected_source_sha256,
        target_path,
        generate_document,
    ):
        generated = generate_document(Path(source_path), Path(target_path))
        return _Publication(Path(generated), _hash(Path(generated)), True, None)

    def publish_update(
        self,
        *,
        current_path,
        expected_current_sha256,
        history_root,
        update_document,
    ):
        current = Path(current_path)
        if _hash(current) != expected_current_sha256:
            raise RuntimeError("changed after preview")
        archive = Path(history_root) / "20260831-120000" / current.name
        archive.parent.mkdir(parents=True)
        shutil.copy2(current, archive)
        stage = current.with_name(f".{current.name}.stage.docx")
        update_document(current, stage)
        stage.replace(current)
        return _Publication(current, _hash(current), True, archive)


class _Publication:
    def __init__(self, current_path, current_sha256, changed, archive_path) -> None:
        self.current_path = current_path
        self.current_sha256 = current_sha256
        self.changed = changed
        self.archive_path = archive_path


def _write(path: Path, content: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def _hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()
