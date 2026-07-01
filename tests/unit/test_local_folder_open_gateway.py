from pathlib import Path

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
