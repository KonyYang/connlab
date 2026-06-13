from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine

from backend.application.project_request_material_collection_service import (
    ProjectRequestMaterialCollectionItemRecord,
    ProjectRequestMaterialCollectionRecord,
)
from backend.infrastructure.storage.database import create_session_factory, init_db
from backend.infrastructure.storage.repositories import (
    ProjectRequestMaterialCollectionRepository,
)


def test_request_material_collection_repository_saves_and_reads_latest() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    init_db(engine)
    session_factory = create_session_factory(engine)
    session = session_factory()
    try:
        repository = ProjectRequestMaterialCollectionRepository(session)
        collection = ProjectRequestMaterialCollectionRecord(
            collection_id="collection-1",
            project_id="P1",
            workspace_id="workspace-1",
            status="partial",
            item_count=2,
            copied_count=1,
            already_present_count=0,
            conflict_count=0,
            skipped_count=1,
            missing_source_count=0,
            created_at="2026-06-13T00:00:00+00:00",
            updated_at="2026-06-13T00:00:00+00:00",
            warnings=("Request email missing",),
        )
        item = ProjectRequestMaterialCollectionItemRecord(
            item_id="item-1",
            collection_id="collection-1",
            project_id="P1",
            source_asset_id="asset-1",
            source_asset_type="attachment",
            source_role="supporting_attachment",
            dedupe_key="path:drawing.pdf",
            source_path=Path("source/drawing.pdf"),
            original_name="drawing.pdf",
            target_area="submitted_material",
            target_path=Path("target/drawing.pdf"),
            status="copied",
            action="copy",
            review_required=False,
            size_bytes=10,
            sha256="a" * 64,
        )

        repository.save_collection(collection, (item,))
        session.commit()

        latest = repository.latest_by_project("P1")
        assert latest == collection
        assert repository.list_items("collection-1") == (item,)
    finally:
        session.close()
