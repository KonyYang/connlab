"""Restore process-level defaults after tests exercising actual launch contracts."""
import os
import tempfile
import pytest

@pytest.fixture(autouse=True)
def restore_runtime_entry_environment():
    names = lambda: {key for key in os.environ if key.startswith("CONNLAB_")} | {"TMP", "TEMP"}
    snapshot = {key: os.environ.get(key) for key in names()}
    old_temporary = tempfile.tempdir
    yield
    for key in names() | snapshot.keys():
        if snapshot.get(key) is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = snapshot[key]
    tempfile.tempdir = old_temporary
