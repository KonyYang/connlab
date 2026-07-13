"""Freeform contact-family validation shared by the editable authority boundary."""

from __future__ import annotations

import re
import unicodedata


_FREEFORM_ID = re.compile(r"ff-(?:llcr|cr)-[1-9][0-9]*$")


class ContactMeasurementPlanFamilyValidationError(ValueError):
    """A single target payload cannot become an authority snapshot."""


def validate_contact_measurement_families(
    families: tuple[dict[str, object], ...],
) -> None:
    """Fail closed before the repository replaces one target's family rows."""
    family_ids: set[str] = set()
    normalized_labels: dict[str, str] = {}
    normalized_prefixes: set[str] = set()
    for family in families:
        family_id = str(family["family_id"]).strip()
        if not family_id or family_id in family_ids:
            raise ContactMeasurementPlanFamilyValidationError(
                "Contact family ids must be nonblank and unique."
            )
        family_ids.add(family_id)
        label = str(family["label"]).strip()
        record_prefix = str(family["record_prefix"]).strip()
        if not label or not record_prefix:
            raise ContactMeasurementPlanFamilyValidationError(
                "Contact family label and record prefix are required."
            )
        count = int(family["count_per_sample"])
        included = bool(family["included"])
        if count < 0 or (included and count == 0):
            raise ContactMeasurementPlanFamilyValidationError(
                "Included contact family count per sample must be a positive integer."
            )
        if _FREEFORM_ID.fullmatch(family_id):
            normalized = normalize_freeform_prefix(record_prefix)
            normalized_label = normalize_freeform_label(label)
            if normalized in normalized_prefixes:
                raise ContactMeasurementPlanFamilyValidationError(
                    "Contact family prefixes must be unique."
                )
            if normalized != record_prefix:
                raise ContactMeasurementPlanFamilyValidationError(
                    "Freeform contact prefixes must use 1 to 64 uppercase ASCII letters or digits."
                )
            normalized_prefixes.add(normalized)
            existing_id = normalized_labels.get(normalized_label)
            if existing_id is not None and existing_id != family_id:
                raise ContactMeasurementPlanFamilyValidationError(
                    "family_identity_collision: contact family labels must be unique."
                )
            normalized_labels[normalized_label] = family_id


def validate_sibling_freeform_family_authorities(
    pending_families: tuple[dict[str, object], ...],
    sibling_authorities: list[tuple[str, str, str]],
) -> None:
    """Reject semantic redefinition of an issued id in one revision and kind."""
    issued: dict[str, tuple[str, str]] = {}
    labels: dict[str, str] = {}
    for family_id, label, prefix in sibling_authorities:
        if not _FREEFORM_ID.fullmatch(family_id):
            continue
        normalized_label = normalize_freeform_label(label)
        normalized_prefix = normalize_freeform_prefix(prefix)
        existing = issued.get(family_id)
        if existing is not None and existing != (normalized_label, normalized_prefix):
            raise ContactMeasurementPlanFamilyValidationError(
                "family_identity_collision: persisted family id has divergent semantics."
            )
        issued[family_id] = (normalized_label, normalized_prefix)
        label_owner = labels.get(normalized_label)
        if label_owner is not None and label_owner != family_id:
            raise ContactMeasurementPlanFamilyValidationError(
                "family_identity_collision: persisted contact family labels are duplicated."
            )
        labels[normalized_label] = family_id
    for family in pending_families:
        family_id = str(family["family_id"]).strip()
        if not _FREEFORM_ID.fullmatch(family_id):
            continue
        normalized_label = normalize_freeform_label(str(family["label"]).strip())
        normalized_prefix = normalize_freeform_prefix(str(family["record_prefix"]).strip())
        existing = issued.get(family_id)
        if existing is not None and existing != (normalized_label, normalized_prefix):
            raise ContactMeasurementPlanFamilyValidationError(
                "family_identity_collision: issued family id cannot change label or prefix."
            )
        label_owner = labels.get(normalized_label)
        if label_owner is not None and label_owner != family_id:
            raise ContactMeasurementPlanFamilyValidationError(
                "family_identity_collision: contact family labels must be unique."
            )


def normalize_freeform_label(value: str) -> str:
    return unicodedata.normalize("NFKC", value).strip().casefold()


def normalize_freeform_prefix(value: str) -> str:
    """Return the stored prefix form without rewriting legacy family values."""
    normalized = unicodedata.normalize("NFKC", value).upper()
    if not re.fullmatch(r"[A-Z0-9]{1,64}", normalized):
        return ""
    return normalized
