"""Windows-only recycle operation with a durable, verified destination receipt.

Microsoft IFileOperation SetOperationFlags / IFileOperationProgressSink PostDeleteItem:
https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nf-shobjidl_core-ifileoperation-setoperationflags
https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nf-shobjidl_core-ifileoperationprogresssink-postdeleteitem
No permanent-delete API or automatic approval of a permanent-delete prompt is used.
"""
from pathlib import Path
import os


class RecycleError(ValueError):
    pass


def recycle_directory(path, record):
    """Recycle one ordinary local directory; record the Shell's resulting item.

    If Windows cannot recycle it, WANTNUKEWARNING retains its explicit warning;
    this adapter never answers that warning. A missing new Shell item is a failure.
    The caller owns backup verification and hashes the returned destination.
    """
    if os.name != "nt":
        raise RecycleError("Windows system Recycle Bin is required")
    from backend.infrastructure.project_library.files import checked_path
    path = checked_path(path)
    if not path.is_dir() or path.parent == path:
        raise RecycleError("Expected an ordinary non-root directory")
    import pythoncom
    from win32com.shell import shell, shellcon
    from win32com.server.policy import DesignatedWrapPolicy
    from win32com.server.exception import COMException

    class Sink(DesignatedWrapPolicy):
        _com_interfaces_ = [shell.IID_IFileOperationProgressSink]
        _public_methods_ = ["StartOperations", "FinishOperations", "PreRenameItem", "PostRenameItem",
                           "PreMoveItem", "PostMoveItem", "PreCopyItem", "PostCopyItem", "PreDeleteItem",
                           "PostDeleteItem", "PreNewItem", "PostNewItem", "UpdateProgress", "ResetTimer", "PauseTimer", "ResumeTimer"]

        def __init__(self):
            self._wrap_(self)
            self.receipt = None
            self.failure = None

        def PreDeleteItem(self, flags, item):
            if not flags & shellcon.TSF_DELETE_RECYCLE_IF_POSSIBLE:
                self.failure = "Windows did not propose a recycle operation"
                raise COMException(self.failure, scode=0x80004004)

        def PostDeleteItem(self, flags, item, result, created):
            if result < 0 or created is None:
                self.failure = "Windows did not return a system Recycle Bin item"
                return
            try:
                destination = Path(created.GetDisplayName(shellcon.SIGDN_FILESYSPATH))
                # A filesystem destination within the same drive's Recycle Bin is required.
                if destination.drive.casefold() != path.drive.casefold() or "$recycle.bin" not in [p.casefold() for p in destination.parts] or not destination.name.startswith("$R"):
                    raise RecycleError("Shell returned an unexpected recycle destination")
                receipt = {"source": str(path), "recycled_path": str(destination), "transport": "IFileOperation", "hresult": result}
                record(receipt)  # Persist before PerformOperations returns: response-loss recovery.
                self.receipt = receipt
            except Exception as exc:
                self.failure = str(exc)

        def StartOperations(self): pass
        def FinishOperations(self, result):
            if result < 0:
                self.failure = "Windows file operation failed: " + str(result)
        def PreRenameItem(self, *args): raise COMException("Unexpected rename", scode=0x80004004)
        def PreMoveItem(self, *args): raise COMException("Unexpected move", scode=0x80004004)
        def PreCopyItem(self, *args): raise COMException("Unexpected copy", scode=0x80004004)
        def PreNewItem(self, *args): raise COMException("Unexpected creation", scode=0x80004004)
        def PostRenameItem(self, *args): pass
        def PostMoveItem(self, *args): pass
        def PostCopyItem(self, *args): pass
        def PostNewItem(self, *args): pass
        def UpdateProgress(self, *args): pass
        def ResetTimer(self): pass
        def PauseTimer(self): pass
        def ResumeTimer(self): pass

    pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)
    operation = None
    try:
        operation = pythoncom.CoCreateInstance(shell.CLSID_FileOperation, None, pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IFileOperation)
        sink = Sink()
        wrapped = pythoncom.WrapObject(sink, shell.IID_IFileOperationProgressSink)
        # Documented SDK values not exposed by this installed pywin32 shellcon.
        recycle_on_delete, early_failure = 0x00080000, 0x00100000
        operation.SetOperationFlags(recycle_on_delete | early_failure | shellcon.FOF_NOERRORUI | shellcon.FOF_WANTNUKEWARNING | shellcon.FOF_SILENT)
        item = shell.SHCreateItemFromParsingName(str(path), None, shell.IID_IShellItem)
        operation.DeleteItem(item, wrapped)
        operation.PerformOperations()
        if operation.GetAnyOperationsAborted() or sink.failure or not sink.receipt or path.exists():
            raise RecycleError(sink.failure or "Recycle operation aborted or lacked a receipt")
        return sink.receipt
    finally:
        operation = None
        pythoncom.CoUninitialize()
