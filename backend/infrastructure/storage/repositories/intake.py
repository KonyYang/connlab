"""Application form and sample repositories."""

from __future__ import annotations

from dataclasses import replace

from sqlalchemy import literal_column, select
from sqlalchemy.orm import Session

from backend.domain import ApplicationForm, SampleInfo
from backend.infrastructure.storage.models import ApplicationFormModel, SampleInfoModel


class ApplicationFormRepository:
    """Persist and load application form domain records."""

    def __init__(self, session: Session) -> None:
        """Create a repository bound to a SQLAlchemy session."""
        self._session = session

    def create(self, form: ApplicationForm) -> ApplicationForm:
        """Persist a new application form."""
        self._session.add(_form_to_model(form))
        self._session.flush()
        return form

    def create_with_samples(
        self,
        form: ApplicationForm,
        samples: tuple[SampleInfo, ...],
    ) -> ApplicationForm:
        """Persist an application form and its project sample rows together."""
        self._session.add(_form_to_model(form))
        self._session.add_all(
            _sample_to_model(
                sample
                if sample.source_form_id is not None
                else replace(sample, source_form_id=form.form_id)
            )
            for sample in samples
        )
        self._session.flush()
        return form

    def get(self, form_id: str) -> ApplicationForm | None:
        """Return an application form by ID, or None when missing."""
        row = self._session.get(ApplicationFormModel, form_id)
        return _form_to_domain(row) if row else None

    def list_by_project(self, project_id: str) -> list[ApplicationForm]:
        """Return application forms for a project."""
        rows = self._session.scalars(
            select(ApplicationFormModel)
            .where(ApplicationFormModel.project_id == project_id)
            .order_by(ApplicationFormModel.form_id)
        ).all()
        return [_form_to_domain(row) for row in rows]

    def update(self, form: ApplicationForm) -> ApplicationForm:
        """Update an existing application form."""
        row = self._session.get(ApplicationFormModel, form.form_id)
        if row is None:
            raise ValueError(f"Application form not found: {form.form_id}")
        row.project_id = form.project_id
        row.form_no = form.form_no
        row.revision = form.revision
        row.requester = form.requester
        row.request_date = form.request_date
        row.phone = form.phone
        row.email = form.email
        row.business_unit = form.business_unit
        row.manufacturing_site = form.manufacturing_site
        row.requested_testing = form.requested_testing
        row.subcontract_allowed = form.subcontract_allowed
        row.reference_doc = form.reference_doc
        row.lab_test_request_number = form.lab_test_request_number
        row.project_number = form.project_number
        row.requested_completion_date = form.requested_completion_date
        row.results_format = form.results_format
        row.test_type = form.test_type
        row.sample_status = form.sample_status
        row.project_type = form.project_type
        row.post_testing_disposition = form.post_testing_disposition
        row.confidential = form.confidential
        row.subcontract = form.subcontract
        row.additional_information = form.additional_information
        row.send_copies_recipients = form.send_copies_recipients
        row.lab = form.lab
        row.assigned_personnel = form.assigned_personnel
        row.received_date = form.received_date
        row.estimated_completion_date = form.estimated_completion_date
        row.sample_condition = form.sample_condition
        self._session.flush()
        return form


class SampleInfoRepository:
    """Persist and load sample information records."""

    def __init__(self, session: Session) -> None:
        """Create a repository bound to a SQLAlchemy session."""
        self._session = session

    def create(self, sample: SampleInfo) -> SampleInfo:
        """Persist a new sample info record."""
        self._session.add(_sample_to_model(sample))
        self._session.flush()
        return sample

    def get(self, sample_id: str) -> SampleInfo | None:
        """Return a sample by ID, or None when missing."""
        row = self._session.get(SampleInfoModel, sample_id)
        return _sample_to_domain(row) if row else None

    def list_by_project(self, project_id: str) -> list[SampleInfo]:
        """Return sample rows for a project."""
        rows = self._session.scalars(
            select(SampleInfoModel)
            .where(SampleInfoModel.project_id == project_id)
            .order_by(SampleInfoModel.row_index, literal_column("rowid"))
        ).all()
        return [_sample_to_domain(row) for row in rows]

    def update(self, sample: SampleInfo) -> SampleInfo:
        """Update an existing sample info record."""
        row = self._session.get(SampleInfoModel, sample.sample_id)
        if row is None:
            raise ValueError(f"Sample info not found: {sample.sample_id}")
        row.project_id = sample.project_id
        row.product_name = sample.product_name
        row.part_number = sample.part_number
        row.revision = sample.revision
        row.lot_or_traceability = sample.lot_or_traceability
        row.material = sample.material
        row.plating = sample.plating
        row.lubricant = sample.lubricant
        row.housing_material = sample.housing_material
        row.quantity = sample.quantity
        row.row_index = sample.row_index
        row.source_form_id = sample.source_form_id
        self._session.flush()
        return sample


def _form_to_model(form: ApplicationForm) -> ApplicationFormModel:
    """Convert an application form domain record to an ORM row."""
    return ApplicationFormModel(
        form_id=form.form_id,
        project_id=form.project_id,
        form_no=form.form_no,
        revision=form.revision,
        requester=form.requester,
        request_date=form.request_date,
        phone=form.phone,
        email=form.email,
        business_unit=form.business_unit,
        manufacturing_site=form.manufacturing_site,
        requested_testing=form.requested_testing,
        subcontract_allowed=form.subcontract_allowed,
        reference_doc=form.reference_doc,
        lab_test_request_number=form.lab_test_request_number,
        project_number=form.project_number,
        requested_completion_date=form.requested_completion_date,
        results_format=form.results_format,
        test_type=form.test_type,
        sample_status=form.sample_status,
        project_type=form.project_type,
        post_testing_disposition=form.post_testing_disposition,
        confidential=form.confidential,
        subcontract=form.subcontract,
        additional_information=form.additional_information,
        send_copies_recipients=form.send_copies_recipients,
        lab=form.lab,
        assigned_personnel=form.assigned_personnel,
        received_date=form.received_date,
        estimated_completion_date=form.estimated_completion_date,
        sample_condition=form.sample_condition,
    )


def _form_to_domain(row: ApplicationFormModel) -> ApplicationForm:
    """Convert an application form ORM row to a domain record."""
    return ApplicationForm(
        form_id=row.form_id,
        project_id=row.project_id,
        form_no=row.form_no,
        revision=row.revision,
        requester=row.requester,
        request_date=row.request_date,
        phone=row.phone,
        email=row.email,
        business_unit=row.business_unit,
        manufacturing_site=row.manufacturing_site,
        requested_testing=row.requested_testing,
        subcontract_allowed=row.subcontract_allowed,
        reference_doc=row.reference_doc,
        lab_test_request_number=row.lab_test_request_number,
        project_number=row.project_number,
        requested_completion_date=row.requested_completion_date,
        results_format=row.results_format,
        test_type=row.test_type,
        sample_status=row.sample_status,
        project_type=row.project_type,
        post_testing_disposition=row.post_testing_disposition,
        confidential=row.confidential,
        subcontract=row.subcontract,
        additional_information=row.additional_information,
        send_copies_recipients=row.send_copies_recipients,
        lab=row.lab,
        assigned_personnel=row.assigned_personnel,
        received_date=row.received_date,
        estimated_completion_date=row.estimated_completion_date,
        sample_condition=row.sample_condition,
    )


def _sample_to_model(sample: SampleInfo) -> SampleInfoModel:
    """Convert a sample domain record to an ORM row."""
    return SampleInfoModel(
        sample_id=sample.sample_id,
        project_id=sample.project_id,
        product_name=sample.product_name,
        part_number=sample.part_number,
        revision=sample.revision,
        lot_or_traceability=sample.lot_or_traceability,
        material=sample.material,
        plating=sample.plating,
        lubricant=sample.lubricant,
        housing_material=sample.housing_material,
        quantity=sample.quantity,
        row_index=sample.row_index,
        source_form_id=sample.source_form_id,
    )


def _sample_to_domain(row: SampleInfoModel) -> SampleInfo:
    """Convert a sample ORM row to a domain record."""
    return SampleInfo(
        sample_id=row.sample_id,
        project_id=row.project_id,
        product_name=row.product_name,
        part_number=row.part_number,
        revision=row.revision,
        lot_or_traceability=row.lot_or_traceability,
        material=row.material,
        plating=row.plating,
        lubricant=row.lubricant,
        housing_material=row.housing_material,
        quantity=row.quantity,
        row_index=row.row_index,
        source_form_id=row.source_form_id,
    )
