"""Shared reviewed form/sample projection, separate from Intake confirmation writes."""

from __future__ import annotations

import re
from typing import Any
from uuid import uuid4

from backend.domain import ApplicationForm, SampleInfo


class IntakeDataProjector:
    """Project already reviewed values; callers own completeness and persistence."""

    def application_form(self, project_id: str, data: dict[str, Any]) -> ApplicationForm:
        return ApplicationForm(
            form_id=uuid4().hex,
            project_id=project_id,
            form_no=self._optional_text(data, "form_no") or "UNCONFIRMED",
            revision=self._optional_text(data, "revision") or "UNCONFIRMED",
            requester=self._text(data, "requester"),
            phone=self._optional_text(data, "phone"),
            email=self._optional_text(data, "email"),
            business_unit=self._optional_text(data, "business_unit"),
            manufacturing_site=self._optional_text(data, "manufacturing_site"),
            requested_testing=self._optional_text(data, "requested_testing"),
            subcontract_allowed=self._optional_bool(data, "subcontract"),
            reference_doc=self._optional_text(data, "reference_doc"),
            lab_test_request_number=self._optional_text(data, "lab_test_request_number"),
            project_number=self._optional_text(data, "project_no"),
            requested_completion_date=self._optional_text(data, "requested_completion_date"),
            results_format=self._optional_text(data, "results_format"),
            test_type=self._optional_text(data, "test_type"),
            sample_status=self._optional_text(data, "sample_status"),
            project_type=self._optional_text(data, "project_type"),
            post_testing_disposition=self._optional_text(data, "post_testing_disposition"),
            confidential=self._optional_text(data, "confidential"),
            subcontract=self._optional_text(data, "subcontract"),
            additional_information=self._optional_text(data, "additional_information"),
            send_copies_recipients=self._optional_text(data, "send_copies_recipients"),
            lab=self._optional_text(data, "lab"),
            assigned_personnel=self._optional_text(data, "assigned_personnel"),
            received_date=self._optional_text(data, "received_date"),
            estimated_completion_date=self._optional_text(data, "estimated_completion_date"),
            sample_condition=self._optional_text(data, "sample_condition"),
        )

    def sample_infos(
        self,
        project_id: str,
        source_form_id: str,
        data: dict[str, Any],
    ) -> tuple[SampleInfo, ...]:
        rows = data.get("samples")
        if not isinstance(rows, list):
            rows = [{}]
        samples: list[SampleInfo] = []
        for row_index, row in enumerate(rows):
            if not isinstance(row, dict):
                continue
            samples.append(
                SampleInfo(
                    sample_id=uuid4().hex,
                    project_id=project_id,
                    product_name=self._optional_text(row, "product_name")
                    or self._text(data, "product_name"),
                    part_number=self._optional_text(row, "part_number") or "UNCONFIRMED",
                    revision=self._optional_text(row, "revision"),
                    lot_or_traceability=self._optional_text(row, "lot_or_traceability"),
                    material=self._optional_text(row, "material"),
                    plating=self._optional_text(row, "plating"),
                    lubricant=self._optional_text(row, "lubricant"),
                    housing_material=self._optional_text(row, "housing_material"),
                    quantity=self._optional_int(row, "quantity"),
                    row_index=row_index,
                    source_form_id=source_form_id,
                )
            )
        return tuple(samples)

    def _text(self, data: dict[str, Any], key: str) -> str:
        value = self._optional_text(data, key)
        if value is None:
            raise ValueError(f"Missing required field: {key}")
        return value

    def _optional_text(self, data: dict[str, Any], key: str) -> str | None:
        value = data.get(key)
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _optional_int(self, data: dict[str, Any], key: str) -> int | None:
        value = data.get(key)
        if value in (None, ""):
            return None
        if isinstance(value, str):
            match = re.search(r"\d+", value)
            if match:
                return int(match.group(0))
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{key} must be an integer.") from exc

    def _optional_bool(self, data: dict[str, Any], key: str) -> bool | None:
        value = self._optional_text(data, key)
        if value is None:
            return None
        lowered = value.lower()
        if lowered in {"yes", "y", "true", "1", "allowed"}:
            return True
        if lowered in {"no", "n", "false", "0", "not allowed"}:
            return False
        return None
