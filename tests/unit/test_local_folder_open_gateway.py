from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.infrastructure.files.local_folder_open_gateway import LocalFolderOpenGateway


def test_local_folder_open_gateway_opens_existing_directory(tmp_path: Path) -> None:
    opened_paths: list[str] = []
    gateway = LocalFolderOpenGateway(launcher=opened_paths.append)

    result = gateway.open_directory(tmp_path)

    assert result.status == "opened"
    assert result.local_official_folder_path == tmp_path
    assert opened_paths == [str(tmp_path)]


def test_local_folder_open_gateway_blocks_missing_directory(tmp_path: Path) -> None:
    opened_paths: list[str] = []
    missing_path = tmp_path / "missing"
    gateway = LocalFolderOpenGateway(launcher=opened_paths.append)

    result = gateway.open_directory(missing_path)

    assert result.status == "blocked"
    assert result.local_official_folder_path == missing_path
    assert opened_paths == []


@pytest.mark.parametrize("foreground_denied", [False, True])
def test_default_windows_open_restores_and_raises_only_the_requested_folder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, foreground_denied: bool,
) -> None:
    win32gui = pytest.importorskip("win32gui")
    import os

    import win32com.client
    import win32con

    target = tmp_path / "中文 folder"
    target.mkdir()
    events = []

    def explorer_window(hwnd: int, path: str):
        return SimpleNamespace(
            HWND=hwnd, Document=SimpleNamespace(
                Folder=SimpleNamespace(Self=SimpleNamespace(Path=path)),
            ),
        )

    windows = [
        explorer_window(10, str(tmp_path / "other" / target.name)),
        explorer_window(20, str(target).upper()),
    ]

    def activate(hwnd):
        events.append(("activate", hwnd))
        if foreground_denied:
            raise win32gui.error(0, "SetForegroundWindow", "Access denied")

    monkeypatch.setattr(os, "startfile", lambda path: events.append(("open", path)))
    monkeypatch.setattr(win32com.client, "Dispatch", lambda _: SimpleNamespace(Windows=lambda: windows))
    monkeypatch.setattr(win32gui, "GetClassName", lambda _: "CabinetWClass")
    monkeypatch.setattr(win32gui, "IsIconic", lambda _: True)
    monkeypatch.setattr(win32gui, "ShowWindow", lambda hwnd, mode: events.append(("show", hwnd, mode)))
    monkeypatch.setattr(win32gui, "SetForegroundWindow", activate)
    monkeypatch.setattr(
        win32gui, "SetWindowPos",
        lambda hwnd, order, *_: events.append(("raise", hwnd, order)),
    )

    result = LocalFolderOpenGateway().open_directory(target)

    assert result.status == "opened"
    assert events[:3] == [
        ("open", str(target)),
        ("show", 20, win32con.SW_RESTORE),
        ("activate", 20),
    ]
    assert events[3:] == ([("raise", 20, win32con.HWND_TOP)] if foreground_denied else [])
