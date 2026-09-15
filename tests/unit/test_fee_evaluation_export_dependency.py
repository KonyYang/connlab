from __future__ import annotations

from backend.api import dependencies


def test_fee_export_dependency_builds_direct_native_service(monkeypatch) -> None:
    expected = object()
    calls: list[tuple[object, object]] = []

    def build_direct(*, session, settings):
        calls.append((session, settings))
        return expected

    monkeypatch.setattr(
        dependencies,
        "build_direct_confirmed_matrix_fee_evaluation_export_service",
        build_direct,
    )
    session = object()
    settings = object()

    result = dependencies.get_confirmed_matrix_fee_evaluation_export_service(
        session,
        settings,
    )

    assert result is expected
    assert calls == [(session, settings)]
