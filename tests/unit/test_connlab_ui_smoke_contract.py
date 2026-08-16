from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_ui_smoke_config_supports_desktop_and_narrow_viewports(tmp_path: Path) -> None:
    config = {
        "schema": "connlab.ui-smoke",
        "version": 1,
        "endpoint": "http://127.0.0.1:9222",
        "url": "http://127.0.0.1:5173/settings",
        "viewports": [
            {"name": "desktop", "width": 1440, "height": 900},
            {"name": "narrow", "width": 514, "height": 900},
        ],
        "required_selectors": ["main", "[data-testid=save]"],
        "required_text": ["Settings"],
        "forbidden_console_patterns": ["uncaught", "failed to fetch"],
        "timeout_ms": 30000,
    }
    path = tmp_path / "ui-smoke.json"
    path.write_text(json.dumps(config), encoding="utf-8")

    completed = subprocess.run(
        ["node", str(ROOT / "scripts/connlab_ui_smoke.mjs"), "--config", str(path), "--validate-only"],
        cwd=ROOT, text=True, encoding="utf-8", capture_output=True, check=False,
    )

    assert completed.returncode == 0, completed.stderr or completed.stdout
    assert json.loads(completed.stdout)["status"] == "valid"
