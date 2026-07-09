from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_release_build_script_uses_versioned_folder_and_never_deletes_user_data() -> None:
    """RELEASE_001 build script creates release output without touching user data."""
    script = (ROOT / "scripts" / "build_windows_desktop_release.ps1").read_text(
        encoding="utf-8"
    )

    assert "[Console]::OutputEncoding" in script
    assert "pyproject.toml" in script
    assert 'Get-Date -Format "yyyyMMddHHmm"' in script
    assert "ConnLab_${ReleaseDate}_v${ProjectVersion}" in script
    assert "npm run build" in script
    assert "PyInstaller" in script
    assert "dist_release" in script
    assert "ConnLab.exe" in script
    assert "LOCALAPPDATA" not in script
    assert "%LOCALAPPDATA%" not in script


def test_pyinstaller_spec_uses_packaged_launcher_and_frontend_dist() -> None:
    """RELEASE_001 spec bundles the packaged launcher and built frontend."""
    spec = (ROOT / "packaging" / "connlab_desktop.spec").read_text(encoding="utf-8")

    assert "backend.desktop.packaged_launcher" in spec
    assert "assets" in spec
    assert "connlab.ico" in spec
    assert "icon=str(app_icon)" in spec
    assert "frontend_dist" in spec
    assert "frontend/dist" in spec.replace("\\", "/")
    assert "collect_data_files" in spec
    assert "backend.modules.fee_evaluation.seeds" in spec
    assert "*.json" in spec
    assert "CONNLAB_RELEASE_NAME" in spec
    assert "console=False" in spec


def test_operator_readme_documents_copy_folder_and_preserve_settings() -> None:
    """Operator instructions explain copy-and-run and settings preservation."""
    readme = (ROOT / "packaging" / "README_FOR_OPERATOR.md").read_text(
        encoding="utf-8"
    )

    assert "ConnLab.exe" in readme
    assert "%LOCALAPPDATA%\\ConnLab" in readme
    assert "do not delete" in readme.lower()
    assert "copy the whole folder" in readme.lower()


def test_browser_release_script_builds_web_folder_without_business_changes() -> None:
    """RELEASE_003 browser release script packages a local web server shell."""
    script = (ROOT / "scripts" / "build_windows_browser_release.ps1").read_text(
        encoding="utf-8"
    )

    assert "[Console]::OutputEncoding" in script
    assert 'Get-Date -Format "yyyyMMddHHmm"' in script
    assert "ConnLab_Web_${ReleaseDate}_v${ProjectVersion}" in script
    assert "Assert-BrowserFrontendReleaseGuards" in script
    assert "Import Matrix will replace the current source session" in script
    assert "connlab_browser_server.spec" in script
    assert "ConnLab_Server.exe" in script
    assert "Start_ConnLab.bat" in script
    assert "127.0.0.1:8765" in script
    assert "_internal\\frontend_dist" in script
    assert "frontend\\dist\\*" in script
    assert "--basetemp" in script
    assert "tmp\\pytest-browser-release" in script
    assert "routes_settings" not in script
    assert "ltr-workbook" not in script
    assert "LOCALAPPDATA" not in script
    assert "%LOCALAPPDATA%" not in script


def test_browser_release_spec_uses_packaged_server_and_frontend_dist() -> None:
    """RELEASE_003 browser spec bundles the server launcher and built frontend."""
    spec = (ROOT / "packaging" / "connlab_browser_server.spec").read_text(
        encoding="utf-8"
    )

    assert "backend.desktop.packaged_server" in spec
    assert "assets" in spec
    assert "connlab.ico" in spec
    assert "icon=str(app_icon)" in spec
    assert "frontend_dist" in spec
    assert "frontend/dist" in spec.replace("\\", "/")
    assert "collect_data_files" in spec
    assert "backend.modules.fee_evaluation.seeds" in spec
    assert "*.json" in spec
    assert "CONNLAB_RELEASE_NAME" in spec
    assert "console=True" in spec
    assert "packaged_launcher" not in spec


def test_release_icon_asset_exists() -> None:
    """PyInstaller release specs use the ConnLab microscope icon asset."""
    icon = ROOT / "packaging" / "assets" / "connlab.ico"

    assert icon.is_file()
    assert icon.stat().st_size > 0


def test_browser_release_start_script_opens_fixed_local_url() -> None:
    """RELEASE_003 operator start script opens the fixed local web URL."""
    start_script = (ROOT / "packaging" / "Start_ConnLab.bat").read_text(
        encoding="utf-8"
    )

    assert "ConnLab_Server.exe" in start_script
    assert "http://127.0.0.1:8765/" in start_script
    assert "%~dp0" in start_script
    assert "routes_settings" not in start_script
    assert "ltr-workbook" not in start_script
