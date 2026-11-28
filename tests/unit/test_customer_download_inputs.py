from hashlib import sha256
from io import BytesIO
import subprocess
import sys
from types import SimpleNamespace

import pytest

from backend.application.customer_download_inputs import CustomerDownloadInputs
from backend.infrastructure.files.customer_report_choices import CustomerReportChoices


def test_input_is_bound_to_exact_bytes_and_retries_reuse_one_job(tmp_path):
    def inspect(path):
        path.seek(0)
        return {"source_sha256": sha256(path.read()).hexdigest(), "fields": [{"id": "row-a"}]}

    def prepare(source, output, decisions, *, expected_source_sha256):
        source.seek(0)
        assert sha256(source.read()).hexdigest() == expected_source_sha256
        if decisions.get("row-a") not in {"keep", "omit"}:
            raise ValueError("Confirm the sample")
        output.write_bytes(decisions["row-a"].encode("ascii"))

    def launch(**kw):
        assert kw["source_path"].read_bytes() == b"keep"
        return {"operation_id": "123", "status": "queued"}

    inputs = CustomerDownloadInputs(inspect, prepare)
    choices = CustomerReportChoices(tmp_path / "choices")
    source = BytesIO(b"internal")
    p = inputs.inspect(source, "DL-123-CR.docx", choices, "tools", tmp_path)
    ticket = p["input_id"]
    with pytest.raises(ValueError, match="Confirm the sample"):
        inputs.generate(ticket, {}, tmp_path / "template", SimpleNamespace(start=launch))
    job = inputs.generate(ticket, {"row-a": "keep"}, tmp_path / "template", SimpleNamespace(start=launch))
    assert job["operation_id"] == "123"
    assert source.closed
    # The second confirmation cannot launch Word again.
    assert inputs.generate(ticket, {"row-a": "keep"}, tmp_path / "template", SimpleNamespace(read=lambda _: job)) == job
    assert choices.read("tools", p["source_sha256"]) == {"row-a": "keep"}
    assert choices.read("project:other", p["source_sha256"]) == {}
    assert choices.read("tools", sha256(b"changed").hexdigest()) == {}


def test_discard_and_expiry_release_unconfirmed_inputs_without_starting_jobs(tmp_path):
    now = [0.]
    inputs = CustomerDownloadInputs(lambda source: {"source_sha256": "a" * 64}, None, clock=lambda: now[0])
    choices = SimpleNamespace(read=lambda *args: {})
    sources = [BytesIO(b"source") for _ in range(3)]
    def select(source):
        return inputs.inspect(source, "report.docx", choices, "tools", tmp_path)["input_id"]
    first, second = (select(source) for source in sources[:2])
    inputs.discard(first)
    assert sources[0].closed and not sources[1].closed
    now[0] = 3601.
    inputs.discard(select(sources[2]))
    assert all(source.closed for source in sources)
    with pytest.raises(LookupError):
        inputs.generate(second, {}, None, None)
    assert list(tmp_path.iterdir()) == []


def test_pending_original_is_reclaimed_after_abrupt_backend_exit(tmp_path):
    # Bypass Python finalizers: a killed backend must not leave a private Word original on disk.
    script = """
import os, sys
from contextlib import nullcontext
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from backend.api.routes_customer_download import _inspect
from backend.application.customer_download_inputs import CustomerDownloadInputs
store = CustomerDownloadInputs(lambda f: {"source_sha256": f.read().hex()}, None)
reply = _inspect(SimpleNamespace(data_dir=Path(sys.argv[1])), store, SimpleNamespace(read=lambda *args: {}),
                 "tools", "private.docx", lambda: nullcontext(BytesIO(b"internal")))
assert reply["source_sha256"] == b"internal".hex() and reply["input_id"]
os._exit(0)
"""
    subprocess.run([sys.executable, "-c", script, str(tmp_path)], check=True, timeout=45)
    assert list(tmp_path.iterdir()) == []
