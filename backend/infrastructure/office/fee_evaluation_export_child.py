"""Child entry point for production Fee Evaluation export subprocesses."""

from __future__ import annotations

import argparse
from collections.abc import Callable
import json
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


class _ExportService(Protocol):
    def export(
        self, command: ExportConfirmedMatrixFeeEvaluationCommand
    ) -> object:
        """Run one export command."""


def main(argv: list[str] | None = None) -> int:
    """Run a production Fee Evaluation export and emit one JSON object."""
    args = _parse_args(argv)
    try:
        payload = json.loads(args.command_json.read_text(encoding="utf-8"))
        command = command_from_payload(payload)
        settings = Settings.load()
        engine = create_database_engine(settings)
        init_db(engine)
        session_factory = create_session_factory(engine)
        result = _run_export_with_session(
            command=command,
            session_factory=session_factory,
            service_builder=_build_direct_export_service,
        )
        _emit(result)
        return 0 if result.get("status") == "success" else 1
    except ValueError as exc:
        _emit(
            {
                "status": "value_error",
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            }
        )
        return 1
    except Exception as exc:
        _emit(
            {
                "status": "execution_failure",
                "error_type": type(exc).__name__,
                "error_message": f"{type(exc).__name__}: {exc}",
            }
        )
        return 1


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
            result = service.export(command)
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
    )


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a production Fee Evaluation export in a child process."
    )
    parser.add_argument("--command-json", required=True, type=Path)
    return parser.parse_args(argv)


def _error_payload(status: str, exc: Exception) -> dict[str, str]:
    return {
        "status": status,
        "error_type": type(exc).__name__,
        "error_message": str(exc),
    }


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False), end="")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
