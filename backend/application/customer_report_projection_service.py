"""Derive one customer report from the current Internal Report artifact."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Callable, Protocol

from backend.application.current_report_update_service import CurrentReportArtifact


class CustomerReportProjectionError(ValueError):
    """Raised when a customer report cannot be projected or published safely."""


class CurrentReportReader(Protocol):
    def get_current_report(self, project_id: str) -> CurrentReportArtifact: ...


class CustomerReportWriter(Protocol):
    def generate_customer_report(
        self,
        *,
        source_path: Path,
        template_path: Path,
        output_path: Path,
    ) -> Path: ...

    def read_source_report_sha256(self, path: Path) -> str | None: ...


class CustomerReportFiles(Protocol):
    def discover_customer_reports(
        self,
        *,
        folder: Path,
        dl_number: str,
    ) -> tuple[Path, ...]: ...

    def fingerprint(self, path: Path) -> str: ...

    def publish_generated_current(
        self,
        *,
        source_path: Path,
        expected_source_sha256: str,
        target_path: Path,
        generate_document: Callable[[Path, Path], Path],
    ): ...

    def publish_update(
        self,
        *,
        current_path: Path,
        expected_current_sha256: str,
        history_root: Path,
        update_document: Callable[[Path, Path], Path],
    ): ...


@dataclass(frozen=True, slots=True)
class CustomerReportGenerationCommand:
    project_id: str
    template_path: Path
    expected_internal_report_sha256: str
    expected_customer_report_sha256: str | None


@dataclass(frozen=True, slots=True)
class CustomerReportProjectionState:
    project_id: str
    status: str
    mode: str | None
    file_name: str | None
    file_path: Path | None
    file_sha256: str | None
    internal_report_sha256: str | None
    generated_from_internal_sha256: str | None
    can_generate: bool
    download_url_available: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CustomerReportGenerationResult:
    project_id: str
    mode: str
    file_name: str
    file_path: Path
    file_sha256: str
    source_report_sha256: str
    changed: bool
    archive_path: Path | None


class CustomerReportProjectionService:
    """Own current-source selection, lineage state, and safe publication."""

    def __init__(
        self,
        *,
        current_reports: CurrentReportReader,
        files: CustomerReportFiles,
        writer: CustomerReportWriter,
        generated_root: Path,
    ) -> None:
        self._current_reports = current_reports
        self._files = files
        self._writer = writer
        self._generated_root = Path(generated_root)

    def get_state(self, project_id: str) -> CustomerReportProjectionState:
        current = self._current_reports.get_current_report(project_id)
        if (
            current.status != "ready"
            or current.file_path is None
            or current.file_name is None
            or current.file_sha256 is None
        ):
            return CustomerReportProjectionState(
                project_id=project_id,
                status="blocked",
                mode=None,
                file_name=None,
                file_path=None,
                file_sha256=None,
                internal_report_sha256=current.file_sha256,
                generated_from_internal_sha256=None,
                can_generate=False,
                download_url_available=False,
                blockers=("A single current Internal Report is required.",),
                warnings=tuple(),
            )
        if current.mode != "official":
            return CustomerReportProjectionState(
                project_id=project_id,
                status="missing",
                mode="managed_download",
                file_name=None,
                file_path=None,
                file_sha256=None,
                internal_report_sha256=current.file_sha256,
                generated_from_internal_sha256=None,
                can_generate=True,
                download_url_available=False,
                blockers=tuple(),
                warnings=(
                    "No official project folder is available; generation will download a copy.",
                ),
            )
        folder = current.folder_path or current.file_path.parent
        candidates = self._files.discover_customer_reports(
            folder=folder,
            dl_number=_dl_number(current.file_name),
        )
        if len(candidates) > 1:
            return CustomerReportProjectionState(
                project_id=project_id,
                status="ambiguous",
                mode="official",
                file_name=None,
                file_path=None,
                file_sha256=None,
                internal_report_sha256=current.file_sha256,
                generated_from_internal_sha256=None,
                can_generate=False,
                download_url_available=False,
                blockers=(
                    "Multiple customer reports were found beside the current Internal Report.",
                ),
                warnings=tuple(),
            )
        if not candidates:
            return CustomerReportProjectionState(
                project_id=project_id,
                status="missing",
                mode="official",
                file_name=None,
                file_path=None,
                file_sha256=None,
                internal_report_sha256=current.file_sha256,
                generated_from_internal_sha256=None,
                can_generate=True,
                download_url_available=False,
                blockers=tuple(),
                warnings=tuple(),
            )
        customer = candidates[0]
        customer_sha256 = self._files.fingerprint(customer)
        generated_from = self._writer.read_source_report_sha256(customer)
        if generated_from is None:
            status = "untracked"
            warnings = (
                "The existing customer report has no ConnLab source fingerprint. Regenerate it to establish lineage.",
            )
        elif generated_from.casefold() != current.file_sha256.casefold():
            status = "stale"
            warnings = (
                "The current Internal Report changed after this customer report was generated.",
            )
        else:
            status = "ready"
            warnings = tuple()
        return CustomerReportProjectionState(
            project_id=project_id,
            status=status,
            mode="official",
            file_name=customer.name,
            file_path=customer,
            file_sha256=customer_sha256,
            internal_report_sha256=current.file_sha256,
            generated_from_internal_sha256=generated_from,
            can_generate=True,
            download_url_available=True,
            blockers=tuple(),
            warnings=warnings,
        )

    def generate(
        self,
        command: CustomerReportGenerationCommand,
    ) -> CustomerReportGenerationResult:
        template = Path(command.template_path)
        if template.suffix.casefold() != ".docx" or not template.is_file():
            raise CustomerReportProjectionError(
                "The approved E-4515_F customer report template is unavailable."
            )
        current = self._current_reports.get_current_report(command.project_id)
        if (
            current.status != "ready"
            or current.file_path is None
            or current.file_name is None
            or current.file_sha256 is None
        ):
            raise CustomerReportProjectionError(
                "A single current Internal Report is required."
            )
        expected_internal = command.expected_internal_report_sha256.strip().casefold()
        if expected_internal != current.file_sha256.casefold():
            raise CustomerReportProjectionError(
                "The current Internal Report changed after preview. Preview the customer report again."
            )

        if current.mode != "official":
            return self._generate_download(command, current, template)

        state = self.get_state(command.project_id)
        if state.blockers:
            raise CustomerReportProjectionError(" ".join(state.blockers))
        if state.file_path is None:
            if command.expected_customer_report_sha256:
                raise CustomerReportProjectionError(
                    "The customer report state changed after preview. Preview the customer report again."
                )
            folder = current.folder_path or current.file_path.parent
            target = folder / customer_report_file_name(current.file_name)
            published = self._files.publish_generated_current(
                source_path=current.file_path,
                expected_source_sha256=expected_internal,
                target_path=target,
                generate_document=lambda source, output: self._writer.generate_customer_report(
                    source_path=source,
                    template_path=template,
                    output_path=output,
                ),
            )
        else:
            expected_customer = (
                command.expected_customer_report_sha256 or ""
            ).strip().casefold()
            if not expected_customer:
                raise CustomerReportProjectionError(
                    "Preview the customer report again before replacing the existing file."
                )
            if state.file_sha256 is None or expected_customer != state.file_sha256.casefold():
                raise CustomerReportProjectionError(
                    "The customer report changed after preview. Preview the customer report again."
                )
            if current.history_root is None:
                raise CustomerReportProjectionError(
                    "The customer report History folder is unavailable."
                )
            published = self._files.publish_update(
                current_path=state.file_path,
                expected_current_sha256=expected_customer,
                history_root=current.history_root,
                update_document=lambda _customer, output: self._generate_from_expected_source(
                    source_path=current.file_path,
                    expected_source_sha256=expected_internal,
                    template_path=template,
                    output_path=output,
                ),
            )
        return CustomerReportGenerationResult(
            project_id=command.project_id,
            mode="official",
            file_name=published.current_path.name,
            file_path=published.current_path,
            file_sha256=published.current_sha256,
            source_report_sha256=current.file_sha256,
            changed=published.changed,
            archive_path=published.archive_path,
        )

    def _generate_download(
        self,
        command: CustomerReportGenerationCommand,
        current: CurrentReportArtifact,
        template: Path,
    ) -> CustomerReportGenerationResult:
        assert current.file_path is not None
        assert current.file_name is not None
        assert current.file_sha256 is not None
        folder = self._generated_root / _safe_component(command.project_id)
        folder.mkdir(parents=True, exist_ok=True)
        output = _reserve_path(folder / customer_report_file_name(current.file_name))
        try:
            written = self._generate_from_expected_source(
                source_path=current.file_path,
                expected_source_sha256=current.file_sha256,
                template_path=template,
                output_path=output,
            )
            if Path(written) != output or not output.is_file():
                raise CustomerReportProjectionError(
                    "Customer report generation did not produce the reserved download."
                )
            if self._files.fingerprint(current.file_path) != current.file_sha256:
                raise CustomerReportProjectionError(
                    "The current Internal Report changed during generation. Generate again."
                )
            return CustomerReportGenerationResult(
                project_id=command.project_id,
                mode="managed_download",
                file_name=output.name,
                file_path=output,
                file_sha256=self._files.fingerprint(output),
                source_report_sha256=current.file_sha256,
                changed=True,
                archive_path=None,
            )
        except Exception:
            output.unlink(missing_ok=True)
            raise

    def _generate_from_expected_source(
        self,
        *,
        source_path: Path,
        expected_source_sha256: str,
        template_path: Path,
        output_path: Path,
    ) -> Path:
        expected = expected_source_sha256.strip().casefold()
        if self._files.fingerprint(source_path) != expected:
            raise CustomerReportProjectionError(
                "The current Internal Report changed after preview. Generate again."
            )
        written = self._writer.generate_customer_report(
            source_path=source_path,
            template_path=template_path,
            output_path=output_path,
        )
        if self._files.fingerprint(source_path) != expected:
            raise CustomerReportProjectionError(
                "The current Internal Report changed during customer report generation. Generate again."
            )
        return Path(written)


def customer_report_file_name(internal_report_name: str) -> str:
    source = Path(internal_report_name)
    first, separator, remainder = source.stem.partition(" ")
    if not first.casefold().endswith("-cr"):
        first = f"{first}-CR"
    return f"{first}{separator}{remainder}{source.suffix}"


def _dl_number(report_name: str) -> str:
    first = Path(report_name).stem.split(maxsplit=1)[0]
    return re.sub(r"-CR$", "", first, flags=re.IGNORECASE)


def _safe_component(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip()).strip("._")
    return safe or "project"


def _reserve_path(path: Path) -> Path:
    if not path.exists():
        return path
    for suffix in range(2, 10_000):
        candidate = path.with_name(f"{path.stem} ({suffix}){path.suffix}")
        if not candidate.exists():
            return candidate
    raise CustomerReportProjectionError(
        "Unable to reserve a non-overwriting customer report download name."
    )
