"""ConnLab-owned Word COM session lifecycle for Application Form write-back."""

from __future__ import annotations

from pathlib import Path
from types import TracebackType
from typing import Callable

from backend.infrastructure.office.office_lifecycle import OfficeAutomationUnavailable


class ApplicationFormWordSession:
    """Bounded owner for one hidden Word COM application instance."""

    def __init__(
        self,
        *,
        dispatch_factory: Callable[[], object] | None = None,
        co_initialize: Callable[[], None] | None = None,
        co_uninitialize: Callable[[], None] | None = None,
    ) -> None:
        """Create a Word session with optional factories for tests."""
        self._dispatch_factory = dispatch_factory
        self._co_initialize = co_initialize
        self._co_uninitialize = co_uninitialize
        self._word: object | None = None
        self._opened_documents: list[object] = []
        self._entered = False
        self._coinitialized = False

    def __enter__(self) -> "ApplicationFormWordSession":
        """Start a ConnLab-owned hidden Word application."""
        if self._entered:
            return self
        try:
            dispatch_factory = self._dispatch_factory
            if dispatch_factory is None:
                try:
                    import pythoncom  # type: ignore[import-not-found]
                    import win32com.client  # type: ignore[import-not-found]
                except ImportError as exc:  # pragma: no cover - Windows host dependent
                    raise OfficeAutomationUnavailable(
                        "Word COM automation requires pywin32."
                    ) from exc
                self._co_initialize = pythoncom.CoInitialize
                self._co_uninitialize = pythoncom.CoUninitialize
                dispatch_factory = lambda: win32com.client.DispatchEx("Word.Application")
            if self._co_initialize is not None:
                self._co_initialize()
                self._coinitialized = True
            self._word = dispatch_factory()
            setattr(self._word, "Visible", False)
            setattr(self._word, "DisplayAlerts", 0)
            self._entered = True
            return self
        except Exception:
            if self._coinitialized and self._co_uninitialize is not None:
                self._co_uninitialize()
                self._coinitialized = False
            raise

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Close tracked documents and quit the owned Word application."""
        cleanup_error: BaseException | None = None
        try:
            try:
                self.close_all_documents(save=False)
            except BaseException as close_error:
                cleanup_error = close_error
            try:
                if self._word is not None:
                    self._word.Quit()
            except BaseException as quit_error:
                if cleanup_error is None:
                    cleanup_error = quit_error
        finally:
            self._word = None
            if self._coinitialized and self._co_uninitialize is not None:
                self._co_uninitialize()
                self._coinitialized = False
            self._entered = False
        if cleanup_error is not None and exc_type is None:
            raise cleanup_error

    def open_document(self, path: Path):
        """Open one document and track it for cleanup."""
        if self._word is None:
            raise RuntimeError("Word session is not started.")
        document = self._word.Documents.Open(
            str(Path(path).resolve()),
            ReadOnly=False,
            AddToRecentFiles=False,
        )
        self._opened_documents.append(document)
        return document

    def close_document(self, document: object, *, save: bool = False) -> None:
        """Close one tracked document, tolerating repeated close attempts."""
        if document not in self._opened_documents:
            return
        document.Close(SaveChanges=bool(save))
        self._opened_documents.remove(document)

    def close_all_documents(self, *, save: bool = False) -> None:
        """Close all documents still tracked by this session."""
        cleanup_error: BaseException | None = None
        for document in tuple(self._opened_documents):
            try:
                self.close_document(document, save=save)
            except BaseException as exc:
                if cleanup_error is None:
                    cleanup_error = exc
        if cleanup_error is not None:
            raise cleanup_error
