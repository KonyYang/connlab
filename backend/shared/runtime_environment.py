"""Explicit runtime identity and one policy for default business output locations."""
from pathlib import Path
import json
import os
import tomllib

ENVIRONMENT_VARIABLE = "CONNLAB_ENVIRONMENT"
OUTPUT_ROOTS = {"development": Path("D:/ConnLabDevFiles"), "release": Path("D:/ConnLab")}
DEVELOPMENT_OUTPUT_FOLDERS = {"Materials": "Library", "TemporaryMaterials": "TemporaryProjects"}

def runtime_environment() -> str:
    value = os.environ.get(ENVIRONMENT_VARIABLE, "development")
    if value not in OUTPUT_ROOTS:
        raise ValueError("ConnLab environment must be development or release.")
    return value

def output_path(environment: str, purpose: str, *, root: Path | None = None) -> Path:
    if environment not in OUTPUT_ROOTS:
        raise ValueError("Unknown ConnLab environment.")
    part = Path(purpose)
    if not purpose or part.is_absolute() or len(part.parts) != 1 or purpose in {".", ".."} or any(c in purpose for c in "\\/:*"):
        raise ValueError("Use one output purpose, not an arbitrary path.")
    folder = DEVELOPMENT_OUTPUT_FOLDERS.get(purpose, purpose) if environment == "development" else purpose
    return (root or OUTPUT_ROOTS[environment]) / folder

def apply_entry_defaults(environment: str, defaults: dict[str, object]) -> None:
    """Replace only inherited managed defaults; explicit operator overrides remain valid."""
    previous = json.loads(os.environ.get("CONNLAB_MANAGED_ENV_DEFAULTS", "{}"))
    managed = {}
    for name, value in previous.items():
        if name not in defaults and os.environ.get(name) == value:
            os.environ.pop(name, None)
    for name, value in defaults.items():
        if name not in os.environ or os.environ[name] == previous.get(name):
            os.environ[name] = str(value)
            managed[name] = str(value)
    os.environ[ENVIRONMENT_VARIABLE] = environment
    os.environ["CONNLAB_MANAGED_ENV_DEFAULTS"] = json.dumps(managed)


def configure_process_temporary_storage(settings) -> Path:
    """Upload spool and owned child-process temporary files share this data instance's storage."""
    import tempfile
    root = settings.data_dir / "tmp"
    root.mkdir(parents=True, exist_ok=True)
    os.environ["TMP"] = os.environ["TEMP"] = str(root)
    tempfile.tempdir = str(root)
    return root


def prepare_entry_config(environment: str, defaults: dict[str, object]) -> dict:
    """Discard inherited owned paths before reading this entry's selected configuration."""
    previous = json.loads(os.environ.get("CONNLAB_MANAGED_ENV_DEFAULTS", "{}"))
    for name, value in previous.items():
        if os.environ.get(name) == value:
            os.environ.pop(name, None)
    os.environ.pop("CONNLAB_MANAGED_ENV_DEFAULTS", None)
    apply_entry_defaults(environment, defaults)
    config_path = Path(os.environ["CONNLAB_LOCAL_CONFIG_PATH"])
    if not config_path.is_file():
        return {}
    with config_path.open("rb") as stream:
        return tomllib.load(stream).get("paths", {})


def configured_library_root(configured_paths: dict) -> Path | None:
    value = os.getenv("CONNLAB_LIBRARY_ROOT") or configured_paths.get("library_root")
    if not value:
        return None
    root = Path(str(value)).expanduser()
    if not root.is_absolute():
        raise ValueError("Choose an absolute project library path.")
    return root.resolve()
