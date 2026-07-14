from pathlib import Path

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


def _rows(signal_count: int = 24) -> list[dict[str, object]]:
    return [
        {"category_id": None, "label": "High Power", "count_per_sample": 4, "record_prefix": "HP", "included": True},
        {"category_id": None, "label": "Low Power", "count_per_sample": 5, "record_prefix": "LP", "included": True},
        {"category_id": None, "label": "Signal", "count_per_sample": signal_count, "record_prefix": "SIG", "included": True},
    ]


def _ids():
    values = iter([
        "root", "revision-1", "category-1", "category-2", "category-3",
        "category-4", "category-5", "category-6", "revision-2", "category-7",
        "category-8", "category-9",
    ])
    return lambda: next(values)


def _settings(tmp_path: Path) -> Settings:
    return Settings(data_dir=tmp_path / "data", projects_dir=tmp_path / "projects", templates_dir=tmp_path / "templates", database_path=tmp_path / "data" / "connlab.sqlite3")
