from dataclasses import dataclass

import pytest

from backend.application.project_library.existing_ltr_adoption import (
    ExistingLtrAdoptionService,
    ExistingLtrAuthorityRow,
)
from backend.domain.project_library import ProjectLibraryConflict


@dataclass
class FakeAuthority:
    row: ExistingLtrAuthorityRow | None

    def find(self, ltr_number: str):
        assert ltr_number == "DL-2026-11-013"
        return self.row


class FakeStore:
    def __init__(self, owner=None):
        self.owner = owner
        self.adopted = []

    def current_ltr_owner(self, ltr_number):
        return self.owner

    def adopt_existing_ltr(self, project_id, proof):
        self.adopted.append((project_id, proof))


def authority_row(*, description="Connector qualification"):
    return ExistingLtrAuthorityRow(
        ltr_number="DL-2026-11-013",
        sheet_name="2026",
        row_number=42,
        values=("Nov", 13, 13, "DL-2026-11-013", None, description),
    )


def test_review_and_adopt_revalidate_the_read_only_authority_row():
    store = FakeStore()
    authority = FakeAuthority(authority_row())
    service = ExistingLtrAdoptionService(store, authority)

    proof = service.review("DL-2026-11-013")
    assert proof["status"] == "found"
    assert proof["sheet_name"] == "2026"
    assert proof["row_number"] == 42

    service.adopt("local-project", proof)
    assert store.adopted == [("local-project", proof)]


def test_adopt_blocks_when_the_authority_row_changes_after_review():
    store = FakeStore()
    authority = FakeAuthority(authority_row())
    service = ExistingLtrAdoptionService(store, authority)
    proof = service.review("DL-2026-11-013")
    authority.row = authority_row(description="Changed after review")

    with pytest.raises(ProjectLibraryConflict, match="changed"):
        service.adopt("local-project", proof)
    assert store.adopted == []


def test_review_blocks_a_different_current_local_owner_before_copy():
    store = FakeStore(owner={"project_id": "already-local", "ltr_number": "DL-2026-11-013"})
    service = ExistingLtrAdoptionService(store, FakeAuthority(authority_row()))

    with pytest.raises(ProjectLibraryConflict, match="already belongs"):
        service.review("DL-2026-11-013")


def test_review_requires_an_exact_authority_row():
    service = ExistingLtrAdoptionService(FakeStore(), FakeAuthority(None))
    with pytest.raises(ProjectLibraryConflict, match="not found"):
        service.review("DL-2026-11-013")
