from __future__ import annotations

import ast
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]


def _read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_admin_template_has_public_default_and_both_releases_ship_only_the_example() -> None:
    template = _read_text("connlab.admin.example.toml")
    assert template == '[ltr_workbook]\nmodify_password = "DGLAB"\n'

    for relative_path in (
        "scripts/build_windows_desktop_release.ps1",
        "scripts/build_windows_browser_release.ps1",
    ):
        script = _read_text(relative_path)
        assert '"connlab.admin.example.toml"' in script
        assert 'Join-Path $releaseFolder "config"' in script
        assert 'Join-Path $releaseConfig "connlab.admin.example.toml"' in script
        assert "PROGRAMDATA" not in script.upper()
        assert '"connlab.admin.toml"' not in script


def _load_browser_submodule_filter(spec: str):
    tree = ast.parse(spec)
    prefixes = next(
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(getattr(target, "id", None) == "BROWSER_EXCLUDED_BACKEND_PREFIXES" for target in node.targets)
    )
    predicate = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "is_browser_backend_submodule"
    )
    namespace: dict[str, object] = {}
    exec(compile(ast.Module(body=[prefixes, predicate], type_ignores=[]), "browser-spec", "exec"), namespace)
    return namespace["is_browser_backend_submodule"]


def test_release_build_script_uses_versioned_folder_and_never_deletes_user_data() -> None:
    """RELEASE_001 build script creates release output without touching user data."""
    script = _read_text("scripts/build_windows_desktop_release.ps1")

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
    spec = _read_text("packaging/connlab_desktop.spec")

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
    readme = _read_text("packaging/README_FOR_OPERATOR.md")

    assert "ConnLab.exe" in readme
    assert "%LOCALAPPDATA%\\ConnLab" in readme
    assert "do not delete" in readme.lower()
    assert "copy the whole folder" in readme.lower()


def test_browser_release_script_builds_web_folder_without_business_changes() -> None:
    """RELEASE_003 browser release script packages a local web server shell."""
    script = _read_text("scripts/build_windows_browser_release.ps1")

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
    assert 'Join-Path $releaseFolder "_internal\\release_manifest.json"' in script
    assert "git_commit" in script
    assert "Get-FileHash" in script
    assert "--basetemp" in script
    assert "tmp\\pytest-browser-release" in script
    assert "tests\\unit\\test_support_diagnostic_bundle_service.py" in script
    assert "tests\\integration\\test_support_diagnostics_api.py" in script
    assert "tests\\unit\\test_llcr_cr_specialized_record_workbook_gateway.py" in script
    assert "tests\\integration\\test_matrix_editor_llcr_cr_record_generation_api.py" in script
    assert "tests\\integration\\test_llcr_cr_specialized_record_workbook_api.py" in script
    assert "tests\\integration\\test_project_test_plan_preview_api.py" not in script
    assert script.count('Invoke-TimedStep "[') == 5
    assert "[System.Diagnostics.Stopwatch]::StartNew()" in script
    assert "finally {\n        try {\n            $stopwatch.Stop()" in script
    assert "[time]" in script
    assert script.count("$LASTEXITCODE -ne 0") == 4
    assert "routes_settings" not in script
    assert "ltr-workbook" not in script
    assert "LOCALAPPDATA" not in script
    assert "%LOCALAPPDATA%" not in script


def test_browser_release_timer_reports_failures_without_masking_primary_error() -> None:
    script = _read_text("scripts/build_windows_browser_release.ps1")
    start = script.index("function Invoke-TimedStep")
    helper = script[start : script.index("\n$ProjectVersion", start)]
    probe = helper + r'''
$script:calls = 0
Invoke-TimedStep "success-step" { $script:calls += 1 }
try { Invoke-TimedStep "failure-step" { $script:calls += 1; throw "primary failure" } }
catch { Write-Output ("PRIMARY=" + $_.Exception.Message) }
Write-Output ("CALLS=" + $script:calls)
function Write-Host { throw "report failure" }
try { Invoke-TimedStep "report-step" { $script:calls += 1; throw "action wins" } }
catch { Write-Output ("REPORT=" + $_.Exception.Message) }
Write-Output ("FINAL_CALLS=" + $script:calls)
'''
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", probe], capture_output=True, text=True, encoding="utf-8"
    )
    assert result.returncode == 0
    assert "[time] success-step:" in result.stdout
    assert "[time] failure-step:" in result.stdout
    assert "PRIMARY=primary failure" in result.stdout
    assert "CALLS=2" in result.stdout
    assert "REPORT=action wins" in result.stdout
    assert "FINAL_CALLS=3" in result.stdout


def test_browser_release_spec_uses_packaged_server_and_frontend_dist() -> None:
    """RELEASE_003 browser spec bundles the server launcher and built frontend."""
    spec = _read_text("packaging/connlab_browser_server.spec")

    assert "backend.desktop.packaged_server" in spec
    assert "filter=is_browser_backend_submodule" in spec
    assert "collect_browser_backend_submodules" not in spec
    assert spec.index("filter=is_browser_backend_submodule") < spec.index("a = Analysis(")
    predicate = _load_browser_submodule_filter(spec)
    assert predicate("backend.desktop.shell") is False
    assert predicate("backend.desktop.shell.child") is False
    assert predicate("backend.desktop.shellfish") is True
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
    assert "backend.desktop.packaged_launcher" in spec
    assert "backend.desktop.path_picker_api" in spec
    assert "backend.desktop.shell" in spec
    assert '"webview"' in spec
    assert '"PyQt5"' in spec
    assert '"pythonnet"' in spec
    assert '"clr_loader"' in spec


def test_release_icon_asset_exists() -> None:
    """PyInstaller release specs use the ConnLab microscope icon asset."""
    icon = ROOT / "packaging" / "assets" / "connlab.ico"

    assert icon.is_file()
    assert icon.stat().st_size > 0


def test_browser_release_start_script_opens_fixed_local_url() -> None:
    """RELEASE_003 operator start script opens the fixed local web URL."""
    start_script = _read_text("packaging/Start_ConnLab.bat")

    assert "ConnLab_Server.exe" in start_script
    assert "http://127.0.0.1:8765/" in start_script
    assert "%~dp0" in start_script
    assert "routes_settings" not in start_script
    assert "ltr-workbook" not in start_script


def test_browser_release_smoke_starts_and_verifies_the_packaged_server() -> None:
    """The portable browser release smoke check verifies a live server, not just files."""
    script = _read_text("scripts/smoke_windows_browser_release.ps1")

    assert "Get-NetTCPConnection" in script
    assert "Start-Process -FilePath $serverExe" in script
    assert '"$baseUrl/health"' in script
    assert '"$baseUrl/"' in script
    assert "Invoke-WebRequest -UseBasicParsing" in script
    assert '"status"\\s*:\\s*"ok"' in script
    assert '<div id="root"></div>' in script
    assert "Stop-Process -Id $serverProcess.Id -Force" in script
