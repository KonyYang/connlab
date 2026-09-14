from __future__ import annotations

from pathlib import Path

import pytest

from backend.desktop import packaged_launcher


def test_packaged_desktop_child_mode_routes_to_customer_report_child(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    command_json = tmp_path / "command.json"
    calls: dict[str, object] = {}

    def fake_child_main(argv: list[str]) -> int:
        calls["child_argv"] = argv
        return 11

    def fail_desktop() -> None:
        raise AssertionError("child mode must not start the desktop shell")

    monkeypatch.setattr(
        "backend.infrastructure.office.customer_report_subprocess_child.main",
        fake_child_main,
    )
    monkeypatch.setattr(packaged_launcher, "run_packaged_desktop", fail_desktop)

    result = packaged_launcher.main(
        ["--connlab-customer-report-child", "--command-json", str(command_json)]
    )

    assert result == 11
    assert calls["child_argv"] == ["--command-json", str(command_json)]

