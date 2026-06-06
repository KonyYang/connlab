from __future__ import annotations

from pathlib import Path

import pytest

from backend.application.confirmed_matrix_fee_evaluation_export_service import (
    ConfirmedMatrixFeeEvaluationExportError,
    ExportConfirmedMatrixFeeEvaluationCommand,
    ExportConfirmedMatrixFeeEvaluationResult,
)
from backend.infrastructure.office.fee_evaluation_export_child import (
    _run_export_with_session,
)


def test_child_transaction_commits_after_success() -> None:
    session = _FakeSession()
    result = _run_export_with_session(
        command=_command(),
        session_factory=_SessionFactory(session),
        service_builder=lambda opened_session: _SuccessService(),
    )

    assert result["status"] == "success"
    assert session.committed is True
    assert session.rolled_back is False
    assert session.closed is True


def test_child_transaction_rolls_back_known_business_error() -> None:
    session = _FakeSession()

    result = _run_export_with_session(
        command=_command(),
        session_factory=_SessionFactory(session),
        service_builder=lambda opened_session: _FailingService(
            ConfirmedMatrixFeeEvaluationExportError("not ready")
        ),
    )

    assert result["status"] == "business_error"
    assert session.committed is False
    assert session.rolled_back is True
    assert session.closed is True


def test_child_transaction_rolls_back_unknown_error() -> None:
    session = _FakeSession()

    result = _run_export_with_session(
        command=_command(),
        session_factory=_SessionFactory(session),
        service_builder=lambda opened_session: _FailingService(RuntimeError("boom")),
    )

    assert result["status"] == "execution_failure"
    assert session.committed is False
    assert session.rolled_back is True
    assert session.closed is True


class _FakeSession:
    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def __enter__(self) -> "_FakeSession":
        return self

    def __exit__(self, *args: object) -> None:
        self.closed = True

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


class _SessionFactory:
    def __init__(self, session: _FakeSession) -> None:
        self.session = session

    def __call__(self) -> _FakeSession:
        return self.session


class _SuccessService:
    def export(
        self, command: ExportConfirmedMatrixFeeEvaluationCommand
    ) -> ExportConfirmedMatrixFeeEvaluationResult:
        return ExportConfirmedMatrixFeeEvaluationResult(
            project_id=command.project_id,
            output_path=Path("C:/tmp/fee.xls"),
            output_format="xls",
            status="generated",
            confirmed_matrix_id="cmv-1",
            confirmed_revision=1,
            pricing_rule_version_id="rules-v1",
            pricing_effective_from=None,
            prepared_by=None,
            approved_by=None,
            output_record_id="por-1",
            line_traceability=(),
            warnings=(),
        )


class _FailingService:
    def __init__(self, exc: Exception) -> None:
        self.exc = exc

    def export(self, command: ExportConfirmedMatrixFeeEvaluationCommand) -> object:
        raise self.exc


def _command() -> ExportConfirmedMatrixFeeEvaluationCommand:
    return ExportConfirmedMatrixFeeEvaluationCommand(
        project_id="P1",
        template_path=Path("C:/tmp/template.xls"),
        output_dir=Path("C:/tmp"),
    )
