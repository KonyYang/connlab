"""Child entry point for production Fee Evaluation export subprocesses."""

from __future__ import annotations

import argparse
from collections.abc import Callable
import json
import sys
from pathlib import Path
from typing import Any, Protocol

from sqlalchemy.orm import Session

from backend.application.confirmed_matrix_fee_draft_service import (
    ConfirmedMatrixFeeDraftNotFoundError,
    ConfirmedMatrixFeeDraftService,
)
from backend.application.confirmed_matrix_fee_evaluation_export_service import (
    ConfirmedMatrixFeeEvaluationExportError,
    ConfirmedMatrixFeeEvaluationExportNotFoundError,
    ConfirmedMatrixFeeEvaluationExportService,
    ConfirmedMatrixFeeEvaluationExportUnavailableError,
    ExportConfirmedMatrixFeeEvaluationCommand,
)
from backend.application.confirmed_matrix_fee_evaluation_export_timeout_service import (
    command_from_payload,
    result_to_payload,
)
from backend.application.fee_evaluation_current_pricing_draft_guard import (
    CurrentFeePricingDraftRequiredError,
)
from backend.application.project_output_record_service import (
    ProjectOutputRecordError,
    ProjectOutputRecordNotFoundError,
    ProjectOutputRecordService,
)
from backend.infrastructure.office import FeeEvaluationWorkbookGateway
from backend.infrastructure.office.office_lifecycle import OfficeAutomationUnavailable
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories import (
    ConfirmedMatrixAuthorityRepository,
    ProjectOutputRecordRepository,
    ProjectRepository,
    ProjectTestPlanDraftRepository,
)
from backend.shared.config import Settings
from backend.shared.operation_diagnostics import operation, stage, failure_details, record_failure


class _ExportService(Protocol):
    def export(
        self, command: ExportConfirmedMatrixFeeEvaluationCommand
    ) -> object:
        """Run one export command."""


def main(argv: list[str] | None = None) -> int:
    """Run a production Fee Evaluation export and emit one JSON object."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = _parse_args(argv)
    # The request file remains transient and is never copied into support logs.
    diagnostic_id = None
    try:
        diagnostic_id = json.loads(args.command_json.read_text(encoding="utf-8")).get("diagnostic_context", {}).get("operation_id")
    except (OSError, ValueError, AttributeError):
        pass
    with operation("fee_export_child", operation_id=diagnostic_id) as evidence:
        result = _execute_request(args)
    result["diagnostic_events"] = evidence["events"]
    _emit(result)
    return 0 if result.get("status") == "success" else 1


def _execute_request(args):
    try:
        with stage("office_child_initialize"):
            payload = json.loads(args.command_json.read_text(encoding="utf-8"))
            command = command_from_payload(payload)
            settings = Settings.load()
            engine = create_database_engine(settings)
        try:
            with stage("office_child_database"):
                init_db(engine)
                session_factory = create_session_factory(engine)
            return _run_export_with_session(command=command, session_factory=session_factory,
                                            service_builder=_build_direct_export_service)
        finally:
            engine.dispose()
    except ValueError as exc:
        return _error_payload("value_error", exc)
    except Exception as exc:
        return _error_payload("execution_failure", exc)


def _run_export_with_session(
    *,
    command: ExportConfirmedMatrixFeeEvaluationCommand,
    session_factory: Callable[[], Any],
    service_builder: Callable[[Any], _ExportService],
) -> dict[str, Any]:
    """Run export in one explicit child-owned database transaction."""
    with session_factory() as session:
        service = service_builder(session)
        try:
            with stage("office_export"):
                result = service.export(command)
            with stage("office_child_commit"):
                session.commit()
            return {
                "status": "success",
                "result": result_to_payload(result),  # type: ignore[arg-type]
            }
        except (
            ConfirmedMatrixFeeEvaluationExportError,
            ProjectOutputRecordError,
        ) as exc:
            session.rollback()
            return _error_payload("business_error", exc)
        except CurrentFeePricingDraftRequiredError as exc:
            session.rollback()
            return _error_payload("pricing_draft_conflict", exc)
        except (
            ConfirmedMatrixFeeEvaluationExportNotFoundError,
            ConfirmedMatrixFeeDraftNotFoundError,
            ProjectOutputRecordNotFoundError,
        ) as exc:
            session.rollback()
            return _error_payload("not_found", exc)
        except (
            ConfirmedMatrixFeeEvaluationExportUnavailableError,
            OfficeAutomationUnavailable,
        ) as exc:
            session.rollback()
            return _error_payload("unavailable", exc)
        except ValueError as exc:
            session.rollback()
            return _error_payload("value_error", exc)
        except Exception as exc:
            session.rollback()
            return _error_payload("execution_failure", exc)


def _build_direct_export_service(session: Session) -> ConfirmedMatrixFeeEvaluationExportService:
    """Build the direct in-process export service inside the child process."""
    from backend.application.contact_measurement_plan_confirmed_consumer_adapter import (
        ContactMeasurementPlanConfirmedConsumerAdapter,
    )
    from backend.application.contact_measurement_plan_projection_service import (
        ContactMeasurementPlanProjectionService,
    )
    from backend.application.contact_point_profile_confirmed_consumer_adapter import (
        ContactPointProfileConfirmedConsumerAdapter,
    )
    from backend.application.fee_evaluation_current_pricing_draft_guard import (
        CurrentFeePricingDraftGuard,
    )
    from backend.api.dependencies import _build_fee_evaluation_pricing_draft_service
    from backend.infrastructure.storage.repositories.contact_measurement_plan_authority import (
        ContactMeasurementPlanAuthorityRepository,
    )
    from backend.infrastructure.storage.repositories.contact_point_profile_authority import (
        ContactPointProfileAuthorityRepository,
    )

    confirmed_store = ConfirmedMatrixAuthorityRepository(session)
    settings = Settings.load()
    return ConfirmedMatrixFeeEvaluationExportService(
        fee_draft_service=ConfirmedMatrixFeeDraftService(
            confirmed_store=confirmed_store,
            contact_measurement_adapter=ContactMeasurementPlanConfirmedConsumerAdapter(
                projection_service=ContactMeasurementPlanProjectionService(
                    ContactMeasurementPlanAuthorityRepository(session),
                    settings.contact_measurement_plan_authority_enabled,
                    confirmed_store,
                ),
                confirmed_store=confirmed_store,
            ),
            contact_point_profile_adapter=ContactPointProfileConfirmedConsumerAdapter(
                repository=ContactPointProfileAuthorityRepository(session),
            ),
        ),
        confirmed_store=confirmed_store,
        project_output_service=ProjectOutputRecordService(
            project_store=ProjectRepository(session),
            draft_store=ProjectTestPlanDraftRepository(session),
            output_store=ProjectOutputRecordRepository(session),
        ),
        workbook_writer=FeeEvaluationWorkbookGateway(),
        current_pricing_draft_guard=CurrentFeePricingDraftGuard(
            pricing_draft_loader=_build_fee_evaluation_pricing_draft_service(session)
        ),
    )


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a production Fee Evaluation export in a child process."
    )
    parser.add_argument("--command-json", required=True, type=Path)
    return parser.parse_args(argv)


def _error_payload(status: str, exc: Exception) -> dict[str, Any]:
    record_failure(exc)
    return {
        "status": status,
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "diagnostic": failure_details(exc),
    }


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False), end="")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
