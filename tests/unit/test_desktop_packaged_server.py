from __future__ import annotations

from pathlib import Path

import pytest

from backend.desktop import packaged_server


def test_packaged_server_child_mode_routes_to_fee_export_child(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    command_json = tmp_path / "command.json"
    calls: dict[str, object] = {}

    def fake_child_main(argv: list[str]) -> int:
        calls["child_argv"] = argv
        return 7

    def fail_web_server(*args: object, **kwargs: object) -> None:
        raise AssertionError("child mode must not start the web server")

    monkeypatch.setattr(
        "backend.infrastructure.office.fee_evaluation_export_child.main",
        fake_child_main,
    )
    monkeypatch.setattr(packaged_server, "run_packaged_web_server", fail_web_server)

    result = packaged_server.main(
        ["--connlab-fee-export-child", "--command-json", str(command_json)]
    )

    assert result == 7
    assert calls["child_argv"] == ["--command-json", str(command_json)]


def test_packaged_server_normal_mode_starts_web_server(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: dict[str, object] = {}

    def fake_web_server(*, host: str, port: int) -> None:
        calls["host"] = host
        calls["port"] = port

    monkeypatch.setattr(packaged_server, "run_packaged_web_server", fake_web_server)

    result = packaged_server.main(["--host", "127.0.0.1", "--port", "8765"])

    assert result == 0
    assert calls == {"host": "127.0.0.1", "port": 8765}
