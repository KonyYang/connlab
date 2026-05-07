"""Repository for backend-managed lookup options."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.domain.lookup_options import LookupOption
from backend.infrastructure.storage.models import LookupOptionModel


class LookupOptionRepository:
    """Persist and load grouped lookup options."""

    def __init__(self, session: Session) -> None:
        """Create a repository bound to a SQLAlchemy session."""
        self._session = session

    def has_any(self) -> bool:
        """Return whether any lookup option exists."""
        return (
            self._session.scalar(select(LookupOptionModel.option_id).limit(1))
            is not None
        )

    def add_many(self, options: tuple[LookupOption, ...]) -> None:
        """Persist multiple lookup options."""
        self._session.add_all(_option_to_model(option) for option in options)
        self._session.flush()

    def add_missing(self, options: tuple[LookupOption, ...]) -> None:
        """Persist lookup options that are not already present by group and value."""
        if not options:
            return
        existing = {
            (row.group_key, row.value)
            for row in self._session.scalars(select(LookupOptionModel)).all()
        }
        self._session.add_all(
            _option_to_model(option)
            for option in options
            if (option.group_key, option.value) not in existing
        )
        self._session.flush()

    def list_active_by_groups(self, group_keys: tuple[str, ...]) -> dict[str, list[LookupOption]]:
        """Return active lookup options for the requested groups."""
        if not group_keys:
            return {}
        rows = self._session.scalars(
            select(LookupOptionModel)
            .where(LookupOptionModel.group_key.in_(group_keys))
            .where(LookupOptionModel.active.is_(True))
            .order_by(
                LookupOptionModel.group_key,
                LookupOptionModel.sort_order,
                LookupOptionModel.label,
            )
        ).all()
        grouped: dict[str, list[LookupOption]] = {key: [] for key in group_keys}
        for row in rows:
            grouped.setdefault(row.group_key, []).append(_option_to_domain(row))
        return grouped

    def upsert_many(self, options: tuple[LookupOption, ...]) -> None:
        """Create or update lookup options by group and value."""
        if not options:
            return
        existing = {
            (row.group_key, row.value): row
            for row in self._session.scalars(select(LookupOptionModel)).all()
        }
        for option in options:
            row = existing.get((option.group_key, option.value))
            if row is None:
                self._session.add(_option_to_model(option))
                continue
            row.label = option.label
            row.sort_order = option.sort_order
            row.active = option.active
        self._session.flush()


def _option_to_model(option: LookupOption) -> LookupOptionModel:
    """Convert a lookup option to a database model."""
    return LookupOptionModel(
        option_id=option.option_id,
        group_key=option.group_key,
        value=option.value,
        label=option.label,
        sort_order=option.sort_order,
        active=option.active,
    )


def _option_to_domain(row: LookupOptionModel) -> LookupOption:
    """Convert a database model to a lookup option."""
    return LookupOption(
        option_id=row.option_id,
        group_key=row.group_key,
        value=row.value,
        label=row.label,
        sort_order=row.sort_order,
        active=row.active,
    )
