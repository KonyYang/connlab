"""Minimal ConnLab desktop shell for the existing frontend dev server."""

from __future__ import annotations

from backend.desktop.path_picker_api import DesktopPathPickerApi, PyWebViewPathPicker


DEFAULT_FRONTEND_URL = "http://localhost:5173"


def run_desktop_shell(frontend_url: str = DEFAULT_FRONTEND_URL) -> None:
    """Open ConnLab in a desktop window with the Settings path-picker bridge."""
    try:
        import webview  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError(
            "ConnLab desktop shell requires pywebview. Start the existing "
            "backend and frontend as usual, then install the desktop runtime "
            "before running 'py -m backend.desktop.shell'."
        ) from exc

    window_holder: dict[str, object] = {}
    picker = PyWebViewPathPicker(window_provider=lambda: window_holder.get("window"))
    api = DesktopPathPickerApi(picker=picker)
    window = webview.create_window(
        "ConnLab",
        frontend_url,
        js_api=api,
        width=1280,
        height=820,
        min_size=(1024, 680),
    )
    window_holder["window"] = window
    webview.start(_install_desktop_bridge, window)


def desktop_bridge_script() -> str:
    """Return JavaScript that installs the frontend desktop path-picker contract."""
    return """
window.connlabDesktopPathPicker = {
  pickExternalResourcePath: function(resourceType) {
    return window.pywebview.api.pickExternalResourcePath(resourceType);
  },
  pickMatrixImportSource: function(initialDirectory) {
    return window.pywebview.api.pickMatrixImportSource(initialDirectory);
  }
};
"""


def _install_desktop_bridge(window: object) -> None:
    window.evaluate_js(desktop_bridge_script())


def main() -> None:
    """Command-line entry point for `py -m backend.desktop.shell`."""
    run_desktop_shell()


if __name__ == "__main__":
    main()
