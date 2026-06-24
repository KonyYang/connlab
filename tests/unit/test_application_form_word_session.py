from __future__ import annotations

from pathlib import Path

from backend.infrastructure.office.application_form_word_session import (
    ApplicationFormWordSession,
)


def test_session_closes_open_documents_and_quits_owned_word_on_exit() -> None:
    word = _FakeWordApplication()
    calls: list[str] = []

    with ApplicationFormWordSession(
        dispatch_factory=lambda: word,
        co_initialize=lambda: calls.append("coinitialize"),
        co_uninitialize=lambda: calls.append("couninitialize"),
    ) as session:
        first = session.open_document(Path("first.docx"))
        second = session.open_document(Path("second.docx"))

    assert first.closed
    assert second.closed
    assert word.quit_called
    assert calls == ["coinitialize", "couninitialize"]


def test_session_closes_documents_and_quits_owned_word_on_exception() -> None:
    word = _FakeWordApplication()

    try:
        with ApplicationFormWordSession(dispatch_factory=lambda: word) as session:
            document = session.open_document(Path("request.docx"))
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    else:
        raise AssertionError("Expected caller exception.")

    assert document.closed
    assert word.quit_called


def test_session_close_document_is_idempotent() -> None:
    word = _FakeWordApplication()

    with ApplicationFormWordSession(dispatch_factory=lambda: word) as session:
        document = session.open_document(Path("request.docx"))
        session.close_document(document, save=False)
        session.close_document(document, save=False)

    assert document.close_count == 1
    assert word.quit_called


def test_session_quits_owned_word_when_document_close_fails_on_exit() -> None:
    word = _FakeWordApplication(fail_close=True)

    try:
        with ApplicationFormWordSession(dispatch_factory=lambda: word) as session:
            session.open_document(Path("request.docx"))
    except RuntimeError as exc:
        assert "close failed" in str(exc)
    else:
        raise AssertionError("Expected close failure.")

    assert word.quit_called


def test_session_keeps_document_tracked_when_close_fails() -> None:
    word = _FakeWordApplication(fail_close=True)

    with ApplicationFormWordSession(dispatch_factory=lambda: word) as session:
        document = session.open_document(Path("request.docx"))
        try:
            session.close_document(document, save=False)
        except RuntimeError as exc:
            assert "close failed" in str(exc)
        else:
            raise AssertionError("Expected close failure.")

        document.fail_close = False
        session.close_document(document, save=False)

    assert document.close_count == 1
    assert word.quit_called


class _FakeDocuments:
    def __init__(self, *, fail_close: bool = False) -> None:
        self.opened: list[_FakeDocument] = []
        self.fail_close = fail_close

    def Open(self, path: str, **kwargs):
        document = _FakeDocument(path, fail_close=self.fail_close)
        self.opened.append(document)
        return document


class _FakeDocument:
    def __init__(self, path: str, *, fail_close: bool = False) -> None:
        self.path = path
        self.closed = False
        self.close_count = 0
        self.fail_close = fail_close

    def Close(self, *, SaveChanges: bool) -> None:
        if self.fail_close:
            raise RuntimeError("close failed")
        self.closed = True
        self.close_count += 1


class _FakeWordApplication:
    def __init__(self, *, fail_close: bool = False) -> None:
        self.Documents = _FakeDocuments(fail_close=fail_close)
        self.Visible = True
        self.DisplayAlerts = 1
        self.quit_called = False

    def Quit(self) -> None:
        self.quit_called = True
