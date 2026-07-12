"""Revision lifecycle commands for independent contact-measurement authority."""

from __future__ import annotations

from uuid import uuid4

from backend.application.contact_measurement_plan_impact_classifier import (
    classify_revision_targets,
)
from backend.application.contact_measurement_plan_bootstrap_service import (
    _bootstrap_payload,
)
from backend.application.contact_measurement_plan_revision_snapshot_helpers import (
    apply_target_replacement,
    copy_targets,
    persist_impacts,
)
from backend.application.contact_measurement_plan_revision_fingerprint import (
    editable_revision_fingerprint,
)
from backend.infrastructure.storage.models_contact_measurement_plan_authority import (
    MeasurementPlanRevisionModel,
)
from backend.infrastructure.storage.repositories.contact_measurement_plan_authority import ContactMeasurementPlanAuthorityRepository


class ContactMeasurementPlanLifecycleError(ValueError):
    """Raised when an authority revision command cannot be applied."""


class ContactMeasurementPlanLifecycleService:
    def __init__(
        self,
        repository: ContactMeasurementPlanAuthorityRepository,
        confirmed_store,
        bootstrap_service,
        clock,
        id_factory=lambda: uuid4().hex,
        enabled: bool = True,
    ) -> None:
        self._repository = repository
        self._confirmed = confirmed_store
        self._bootstrap = bootstrap_service
        self._clock = clock
        self._ids = id_factory
        self._enabled = enabled

    def open_draft(self, project_id: str, actor: str) -> str:
        self._require_enabled()
        active = self._confirmed.get_active_by_project(project_id)
        if active is None:
            raise ContactMeasurementPlanLifecycleError("Active confirmed Matrix is required.")
        self._bootstrap.bootstrap(active, actor)
        return self.create_draft(project_id, active.version.confirmed_matrix_id, active.version.confirmed_revision, _matrix_fingerprint(active), actor)

    def create_draft(self, project_id: str, matrix_id: str, matrix_revision: int, binding_fingerprint: str, actor: str) -> str:
        self._require_enabled()
        root = self._repository.get_root(project_id)
        if root is None:
            raise ContactMeasurementPlanLifecycleError("Contact measurement plan is not started.")
        if root.editable_revision_id:
            return root.editable_revision_id
        active = self._repository.get_active_revision(project_id)
        sequence = (active.revision_sequence if active else 0) + 1
        now, revision_id = self._clock(), f"cmprv-{self._ids()}"
        with self._repository.transaction():
            revision = MeasurementPlanRevisionModel(
                measurement_plan_revision_id=revision_id,
                measurement_plan_root_id=root.measurement_plan_root_id,
                revision_sequence=sequence,
                parent_revision_id=(
                    active.measurement_plan_revision_id if active else None
                ),
                state="draft",
                revision_fingerprint=binding_fingerprint,
                base_confirmed_matrix_id=matrix_id,
                base_matrix_revision=matrix_revision,
                matrix_binding_fingerprint=binding_fingerprint,
                bootstrap_provenance=None,
                created_by=actor,
                created_at=now,
                updated_at=now,
                confirmed_by=None,
                confirmed_at=None,
                superseded_at=None,
                superseded_reason=None,
            )
            self._repository.add(revision)
            if active is not None:
                copy_targets(
                    repository=self._repository,
                    source_revision_id=active.measurement_plan_revision_id,
                    target_revision_id=revision_id,
                    id_factory=self._ids,
                )
            root.editable_revision_id = revision_id
            root.updated_at = now
            self._repository.audit(
                root.measurement_plan_root_id,
                "save",
                actor,
                now,
                revision_id,
            )
            self._repository.flush()
            return revision_id

    def confirm(self, project_id: str, revision_id: str, expected_fingerprint: str, actor: str) -> None:
        self._require_enabled()
        root = self._repository.get_root(project_id)
        revision = self._repository.get_revision(revision_id)
        if root is None or revision is None or root.editable_revision_id != revision_id:
            raise ContactMeasurementPlanLifecycleError("Editable contact measurement revision was not found.")
        if revision.revision_fingerprint != expected_fingerprint:
            raise ContactMeasurementPlanLifecycleError("Contact measurement revision is stale.")
        active_matrix = self._confirmed.get_active_by_project(project_id)
        if active_matrix is None or revision.matrix_binding_fingerprint != _matrix_fingerprint(
            active_matrix
        ):
            raise ContactMeasurementPlanLifecycleError(
                "Contact measurement Matrix binding is stale."
            )
        if self._repository.unresolved_review_impacts(revision_id):
            raise ContactMeasurementPlanLifecycleError(
                "Contact measurement revision has unresolved review impacts."
            )
        now = self._clock()
        with self._repository.transaction():
            active = self._repository.get_active_revision(project_id)
            if active is not None:
                active.state = "superseded"
                active.superseded_at = now
                active.superseded_reason = "Superseded by confirmed editable revision."
                self._repository.flush()
            revision.state = "confirmed"
            revision.confirmed_by = actor
            revision.confirmed_at = now
            revision.updated_at = now
            root.active_confirmed_revision_id = revision_id
            root.editable_revision_id = None
            root.updated_at = now
            self._repository.audit(
                root.measurement_plan_root_id,
                "confirm",
                actor,
                now,
                revision_id,
            )
            self._repository.flush()

    def save_revision(
        self,
        project_id: str,
        revision_id: str,
        expected_fingerprint: str,
        actor: str,
    ) -> str:
        """Record one explicit draft save after optimistic-concurrency validation."""
        revision = self._editable_revision(
            project_id,
            revision_id,
            expected_fingerprint,
        )
        root = self._repository.get_root(project_id)
        assert root is not None
        now = self._clock()
        with self._repository.transaction():
            revision.updated_at = now
            self._repository.audit(
                root.measurement_plan_root_id,
                "save",
                actor,
                now,
                revision_id,
            )
            self._repository.flush()
        return revision.revision_fingerprint

    def refresh_impacts(
        self,
        project_id: str,
        revision_id: str,
        expected_matrix_binding_fingerprint: str,
        actor: str,
    ) -> str:
        """Classify current Matrix changes without mutating the Matrix authority."""
        self._require_enabled()
        revision = self._repository.get_revision(revision_id)
        root = self._repository.get_root(project_id)
        current = self._confirmed.get_active_by_project(project_id)
        if root is None or revision is None or root.editable_revision_id != revision_id:
            raise ContactMeasurementPlanLifecycleError(
                "Editable contact measurement revision was not found."
            )
        if current is None:
            raise ContactMeasurementPlanLifecycleError(
                "Active confirmed Matrix is required."
            )
        current_fingerprint = _matrix_fingerprint(current)
        if current_fingerprint != expected_matrix_binding_fingerprint:
            raise ContactMeasurementPlanLifecycleError(
                "Contact measurement Matrix binding is stale."
            )
        result = classify_revision_targets(
            tuple(self._repository.targets(revision_id)),
            current,
        )
        now = self._clock()
        with self._repository.transaction():
            persist_impacts(
                repository=self._repository,
                root_id=root.measurement_plan_root_id,
                revision_id=revision_id,
                targets=self._repository.targets(revision_id),
                result=result,
                after_fingerprint=current_fingerprint,
                created_at=now,
                id_factory=self._ids,
            )
            revision.state = "needs_review" if result.status == "needs_review" else "draft"
            revision.matrix_binding_fingerprint = current_fingerprint
            revision.updated_at = now
            self._repository.audit(
                root.measurement_plan_root_id,
                "refresh_impacts",
                actor,
                now,
                revision_id,
                reason=result.status,
            )
            self._repository.flush()
        return result.status

    def accept_compatible_suggestions(
        self,
        project_id: str,
        revision_id: str,
        expected_fingerprint: str,
        actor: str,
    ) -> None:
        """Audit acceptance without rebinding or overwriting explicit overrides."""
        revision = self._editable_revision(
            project_id,
            revision_id,
            expected_fingerprint,
        )
        root = self._repository.get_root(project_id)
        assert root is not None
        now = self._clock()
        with self._repository.transaction():
            self._repository.accept_compatible_impacts(revision_id)
            revision.updated_at = now
            self._repository.audit(
                root.measurement_plan_root_id,
                "accept_compatible_suggestions",
                actor,
                now,
                revision_id,
            )
            self._repository.flush()

    def set_target_inclusion(
        self,
        project_id: str,
        revision_id: str,
        stable_target_key: str,
        included: bool,
        exclusion_reason: str | None,
        families: tuple[dict[str, object], ...] | None,
        expected_fingerprint: str,
        actor: str,
    ) -> None:
        """Change one draft target only through explicit include/exclude intent."""
        revision = self._editable_revision(
            project_id,
            revision_id,
            expected_fingerprint,
        )
        target = self._repository.target_by_key(revision_id, stable_target_key)
        if target is None:
            raise ContactMeasurementPlanLifecycleError("Contact measurement target was not found.")
        if not included and not (exclusion_reason or "").strip():
            raise ContactMeasurementPlanLifecycleError(
                "An exclusion reason is required when a target is excluded."
            )
        if families is not None:
            _validate_families(families)
        root = self._repository.get_root(project_id)
        assert root is not None
        now = self._clock()
        with self._repository.transaction():
            target.included = included
            target.coverage_state = "included" if included else "excluded"
            target.exclusion_reason = None if included else exclusion_reason.strip()
            if families is not None:
                self._repository.replace_families(
                    target.measurement_plan_target_snapshot_id,
                    families,
                    self._ids,
                )
                target.readings_per_sample = sum(
                    int(family["count_per_sample"])
                    for family in families
                    if bool(family["included"])
                )
            self._repository.flush()
            revision.revision_fingerprint = editable_revision_fingerprint(
                self._repository,
                revision_id,
            )
            revision.updated_at = now
            self._repository.audit(
                root.measurement_plan_root_id,
                "set_target_inclusion",
                actor,
                now,
                revision_id,
                reason=target.exclusion_reason,
            )
            self._repository.flush()

    def rebind_target(
        self,
        project_id: str,
        revision_id: str,
        stable_target_key: str,
        candidate_subject_key: str,
        expected_fingerprint: str,
        actor: str,
    ) -> None:
        """Rebind only by a current canonical target key, never by labels or order."""
        revision = self._editable_revision(
            project_id,
            revision_id,
            expected_fingerprint,
        )
        target = self._repository.target_by_key(revision_id, stable_target_key)
        current = self._confirmed.get_active_by_project(project_id)
        if current is None:
            raise ContactMeasurementPlanLifecycleError(
                "Contact measurement target rebind is unavailable."
            )
        replacement = next(
            (
                item
                for item in _bootstrap_payload(current)
                if item["candidate_subject_key"] == candidate_subject_key
            ),
            None,
        )
        if replacement is None:
            raise ContactMeasurementPlanLifecycleError(
                "Replacement target is not present in the active confirmed Matrix."
            )
        replacement_target_key = str(replacement["stable_target_key"])
        if target is None:
            existing_rebound = self._repository.target_by_key(
                revision_id,
                replacement_target_key,
            )
            if existing_rebound is not None and existing_rebound.is_override:
                self._repository.resolve_candidate_rebind(
                    revision_id,
                    candidate_subject_key,
                )
                return
            raise ContactMeasurementPlanLifecycleError(
                "Contact measurement target rebind is unavailable."
            )
        collision = self._repository.target_by_key(revision_id, replacement_target_key)
        if collision is not None and collision.measurement_plan_target_snapshot_id != (
            target.measurement_plan_target_snapshot_id
        ):
            raise ContactMeasurementPlanLifecycleError(
                "Replacement target is already bound in this editable revision."
            )
        root = self._repository.get_root(project_id)
        assert root is not None
        now = self._clock()
        with self._repository.transaction():
            apply_target_replacement(target, replacement, revision.revision_fingerprint)
            target.is_override = True
            try:
                self._repository.resolve_candidate_rebind(
                    revision_id,
                    candidate_subject_key,
                )
            except ValueError as exc:
                raise ContactMeasurementPlanLifecycleError(str(exc)) from exc
            self._repository.flush()
            revision.revision_fingerprint = editable_revision_fingerprint(
                self._repository,
                revision_id,
            )
            revision.updated_at = now
            self._repository.audit(
                root.measurement_plan_root_id,
                "rebind_target",
                actor,
                now,
                revision_id,
                reason=candidate_subject_key,
            )
            self._repository.flush()

    def _editable_revision(
        self,
        project_id: str,
        revision_id: str,
        expected_fingerprint: str,
    ) -> MeasurementPlanRevisionModel:
        self._require_enabled()
        root = self._repository.get_root(project_id)
        revision = self._repository.get_revision(revision_id)
        if root is None or revision is None or root.editable_revision_id != revision_id:
            raise ContactMeasurementPlanLifecycleError(
                "Editable contact measurement revision was not found."
            )
        if revision.revision_fingerprint != expected_fingerprint:
            raise ContactMeasurementPlanLifecycleError("Contact measurement revision is stale.")
        return revision

    def _require_enabled(self) -> None:
        if not self._enabled:
            raise ContactMeasurementPlanLifecycleError(
                "authority_disabled: independent contact measurement authority is disabled."
            )


def _matrix_fingerprint(snapshot) -> str:
    return f"{snapshot.version.confirmed_matrix_id}:{snapshot.version.confirmed_revision}"


def _validate_families(families: tuple[dict[str, object], ...]) -> None:
    ids: set[str] = set()
    for family in families:
        family_id = str(family["family_id"]).strip()
        if not family_id or family_id in ids:
            raise ContactMeasurementPlanLifecycleError(
                "Contact family ids must be nonblank and unique."
            )
        ids.add(family_id)
        if not str(family["label"]).strip() or not str(family["record_prefix"]).strip():
            raise ContactMeasurementPlanLifecycleError(
                "Contact family label and record prefix are required."
            )
        if int(family["count_per_sample"]) < 0:
            raise ContactMeasurementPlanLifecycleError(
                "Contact family count per sample must be non-negative."
            )
