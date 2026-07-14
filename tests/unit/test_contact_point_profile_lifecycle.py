from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.application.contact_point_profile_lifecycle_service import ContactPointProfileLifecycleService
from backend.application.contact_point_profile_lifecycle_service import ContactPointProfileLifecycleError
from backend.application.contact_point_profile_read_service import ContactPointProfileReadService
from backend.infrastructure.storage.database import create_database_engine, create_session_factory, init_db
from backend.infrastructure.storage.models import ProjectModel
from backend.infrastructure.storage.repositories.contact_point_profile_authority import ContactPointProfileAuthorityRepository
from backend.shared.config import Settings


def test_no_target_project_saves_confirms_and_keeps_later_draft_out_of_summary(tmp_path: Path) -> None:
    engine = create_database_engine(_settings(tmp_path))
    init_db(engine)
    session = create_session_factory(engine)()
    try:
        session.add(ProjectModel(project_id="P1", project_no=None, product_name="Demo", requestor="Operator", status="active"))
        session.commit()
        repository = ContactPointProfileAuthorityRepository(session)
        lifecycle = ContactPointProfileLifecycleService(repository, clock=lambda: "2026-07-14T00:00:00Z", id_factory=_ids())
        read = ContactPointProfileReadService(repository)

        initial = read.get_workspace("P1")
        assert initial["status"] == "not_started"

        saved = lifecycle.save_draft("P1", None, None, _rows(), "operator")
        assert saved["points_per_sample"] == 33
        assert read.get_summary("P1")["status"] == "not_started"

        confirmed = lifecycle.confirm(
            "P1", saved["revision_id"], saved["fingerprint"], saved["categories"], "operator"
        )
        assert confirmed["points_per_sample"] == 33
        assert read.get_summary("P1")["points_per_sample"] == 33

        later_rows = [dict(row) for row in confirmed["categories"]]
        later_rows[2]["count_per_sample"] = 30
        later = lifecycle.save_draft("P1", None, None, later_rows, "operator")
        assert later["points_per_sample"] == 39
        assert read.get_summary("P1")["points_per_sample"] == 33
    finally:
        session.close()
        engine.dispose()


def test_category_identity_is_monotonic_project_owned_and_stale_safe(tmp_path: Path) -> None:
    engine = create_database_engine(_settings(tmp_path))
    init_db(engine)
    session = create_session_factory(engine)()
    try:
        session.add_all([
            ProjectModel(project_id="P1", project_no=None, product_name="Demo", requestor="Operator", status="active"),
            ProjectModel(project_id="P2", project_no=None, product_name="Demo", requestor="Operator", status="active"),
        ])
        session.commit()
        repository = ContactPointProfileAuthorityRepository(session)
        lifecycle = ContactPointProfileLifecycleService(repository, clock=lambda: "2026-07-14T00:00:00Z", id_factory=_ids())

        saved = lifecycle.save_draft("P1", None, None, _rows(), "operator")
        saved_rows = list(saved["categories"])
        changed = [saved_rows[1], saved_rows[2], {"category_id": None, "label": "Control", "count_per_sample": 1, "record_prefix": "CTL", "included": True}]
        next_draft = lifecycle.save_draft("P1", saved["revision_id"], saved["fingerprint"], changed, "operator")
        assert [row["category_id"] for row in next_draft["categories"]] == ["ppc-2", "ppc-3", "ppc-4"]

        try:
            lifecycle.save_draft("P1", next_draft["revision_id"], saved["fingerprint"], next_draft["categories"], "operator")
        except ContactPointProfileLifecycleError as exc:
            assert "stale" in str(exc).lower()
        else:  # pragma: no cover - protects the authoritative stale boundary
            raise AssertionError("Expected stale draft rejection.")

        try:
            lifecycle.save_draft("P2", None, None, [next_draft["categories"][0]], "operator")
        except ContactPointProfileLifecycleError as exc:
            assert "not owned" in str(exc)
        else:  # pragma: no cover - protects cross-project category ownership
            raise AssertionError("Expected cross-project category id rejection.")
        assert repository.get_root("P2") is None
    finally:
        session.close()
        engine.dispose()


def test_direct_confirm_canonicalizes_expressions_and_supersedes_prior_confirmed(tmp_path: Path) -> None:
    engine = create_database_engine(_settings(tmp_path))
    init_db(engine)
    session = create_session_factory(engine)()
    try:
        session.add(ProjectModel(project_id="P1", project_no=None, product_name="Demo", requestor="Operator", status="active"))
        session.commit()
        repository = ContactPointProfileAuthorityRepository(session)
        lifecycle = ContactPointProfileLifecycleService(repository, clock=lambda: "2026-07-15T00:00:00Z", id_factory=_ids())
        first = lifecycle.confirm_direct("P1", None, None, _direct_rows(), "operator")
        assert [row["point_expression"] for row in first["categories"]] == ["1-4", "1-5", "1-24"]
        assert first["points_per_sample"] == 33
        second = lifecycle.confirm_direct(
            "P1", first["revision_id"], first["fingerprint"],
            [{"category_id": first["categories"][0]["category_id"], "prefix": "HP", "point_expression": "1-3,5"}], "operator",
        )
        assert second["categories"][0]["point_expression"] == "1-3,5"
        assert second["categories"][0]["count_per_sample"] == 4
    finally:
        session.close()
        engine.dispose()


def test_direct_confirm_rejects_duplicate_retained_ids_without_new_revision(tmp_path: Path) -> None:
    engine = create_database_engine(_settings(tmp_path))
    init_db(engine)
    session = create_session_factory(engine)()
    try:
        session.add(ProjectModel(project_id="P1", project_no=None, product_name="Demo", requestor="Operator", status="active"))
        session.commit()
        repository = ContactPointProfileAuthorityRepository(session)
        lifecycle = ContactPointProfileLifecycleService(repository, clock=lambda: "2026-07-15T00:00:00Z", id_factory=_ids())
        first = lifecycle.confirm_direct("P1", None, None, _direct_rows(), "operator")
        duplicate = first["categories"][0]["category_id"]
        before = _authority_counts(session)
        with pytest.raises(ContactPointProfileLifecycleError, match="unique"):
            lifecycle.confirm_direct("P1", first["revision_id"], first["fingerprint"], [
                {"category_id": duplicate, "prefix": "HP", "point_expression": "1-4"},
                {"category_id": duplicate, "prefix": "LP", "point_expression": "1-5"},
            ], "operator")
        assert repository.active_revision("P1").contact_point_profile_revision_id == first["revision_id"]
        assert _authority_counts(session) == before
    finally:
        session.close()
        engine.dispose()


def test_direct_confirm_allows_256_categories_and_rejects_257_without_writes(tmp_path: Path) -> None:
    engine = create_database_engine(_settings(tmp_path))
    init_db(engine)
    session = create_session_factory(engine)()
    try:
        session.add(ProjectModel(project_id="P1", project_no=None, product_name="Demo", requestor="Operator", status="active"))
        session.commit()
        repository = ContactPointProfileAuthorityRepository(session)
        identifiers = iter(range(1, 600))
        lifecycle = ContactPointProfileLifecycleService(
            repository,
            clock=lambda: "2026-07-15T00:00:00Z",
            id_factory=lambda: f"id-{next(identifiers)}",
        )
        rows = [{"category_id": None, "prefix": f"P{index}", "point_expression": "1"} for index in range(1, 257)]
        confirmed = lifecycle.confirm_direct("P1", None, None, rows, "operator")
        assert len(confirmed["categories"]) == 256
        before = _authority_counts(session)
        rejected = rows + [{"category_id": None, "prefix": "P257", "point_expression": "1"}]
        with pytest.raises(ContactPointProfileLifecycleError, match="256"):
            lifecycle.confirm_direct("P1", confirmed["revision_id"], confirmed["fingerprint"], rejected, "operator")
        assert _authority_counts(session) == before
    finally:
        session.close()
        engine.dispose()


def _rows(signal_count: int = 24) -> list[dict[str, object]]:
    return [
        {"category_id": None, "label": "High Power", "count_per_sample": 4, "record_prefix": "HP", "included": True},
        {"category_id": None, "label": "Low Power", "count_per_sample": 5, "record_prefix": "LP", "included": True},
        {"category_id": None, "label": "Signal", "count_per_sample": signal_count, "record_prefix": "SIG", "included": True},
    ]


def _direct_rows() -> list[dict[str, object]]:
    return [
        {"category_id": None, "prefix": "HP", "point_expression": "1-4"},
        {"category_id": None, "prefix": "LP", "point_expression": "1,2,3,4,5"},
        {"category_id": None, "prefix": "SIG", "point_expression": "1-24"},
    ]


def _ids():
    values = iter([
        "root", "revision-1", "category-1", "category-2", "category-3",
        "category-4", "category-5", "category-6", "revision-2", "category-7",
        "category-8", "category-9",
    ])
    return lambda: next(values)


def _authority_counts(session: Session) -> tuple[int, int, int]:
    return tuple(
        session.execute(text(f"SELECT count(*) FROM {table}")).scalar_one()
        for table in (
            "contact_point_profile_roots",
            "contact_point_profile_revisions",
            "contact_point_profile_categories",
        )
    )


def _settings(tmp_path: Path) -> Settings:
    return Settings(data_dir=tmp_path / "data", projects_dir=tmp_path / "projects", templates_dir=tmp_path / "templates", database_path=tmp_path / "data" / "connlab.sqlite3")
