from types import SimpleNamespace

from backend.application.contact_point_profile_legacy_suggestion import ContactPointProfileLegacySuggestionService


def test_legacy_suggestion_is_read_only_and_requires_uniform_included_targets() -> None:
    service = ContactPointProfileLegacySuggestionService(_LegacyRepository(uniform=True))

    suggestion = service.get_uniform_suggestion("P1")

    assert suggestion == [
        {
            "category_id": None, "category_ordinal": 0, "label": "High Power",
            "count_per_sample": 4, "record_prefix": "HP", "included": True,
        }
    ]
    assert _LegacyRepository(uniform=False).calls == []
    assert ContactPointProfileLegacySuggestionService(_LegacyRepository(uniform=False)).get_uniform_suggestion("P1") is None


class _LegacyRepository:
    def __init__(self, uniform: bool) -> None:
        self.uniform = uniform
        self.calls: list[str] = []

    def get_active_revision(self, project_id: str):
        self.calls.append(project_id)
        return SimpleNamespace(measurement_plan_revision_id="legacy-revision")

    def targets(self, revision_id: str):
        return [
            SimpleNamespace(eligible=True, included=True, measurement_plan_target_snapshot_id="target-a"),
            SimpleNamespace(eligible=True, included=True, measurement_plan_target_snapshot_id="target-b"),
        ]

    def families(self, target_id: str):
        count = 4 if self.uniform or target_id == "target-a" else 5
        return [SimpleNamespace(label="High Power", count_per_sample=count, record_prefix="HP", included=True)]
