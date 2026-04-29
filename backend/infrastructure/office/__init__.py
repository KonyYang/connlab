"""Office gateway package."""

from backend.infrastructure.office.models import (
    ImportedMailAttachment,
    ImportedMailPackage,
    LtrWorkbookFormat,
    LtrWorkbookSnapshot,
    OfficeFileClassification,
    OfficeFileKind,
    WordDocumentSnapshot,
)
from backend.infrastructure.office.msg_compatibility import (
    MsgCompatibilityResult,
    MsgCompatibilityStatus,
    probe_msg_samples,
)
from backend.infrastructure.office.office_facade import OfficeFacade
from backend.infrastructure.office.office_lifecycle import (
    OfficeAutomationUnavailable,
    OfficeLifecycleManager,
)
from backend.infrastructure.office.excel_workbook_gateway import (
    ExcelWorkbookGateway,
    LtrWorkbookGatewayError,
    UnreadableLtrWorkbookError,
    UnsupportedLtrWorkbookError,
)
from backend.infrastructure.office.excel_com_ltr_workbook_gateway import (
    ExcelComLTRWorkbookGateway,
    LtrWorkbookReadOnlyError,
    LtrWorkbookRowData,
    LtrWorkbookRowPointer,
    LtrWorkbookWriteConfig,
    LtrWorkbookWriteDisabledError,
    LtrWorkbookWriteError,
)
from backend.infrastructure.office.outlook_msg_gateway import (
    OutlookMsgAttachmentError,
    OutlookMsgImportError,
    OutlookMsgMetadataError,
)
from backend.infrastructure.office.word_document_gateway import WordDocumentGateway

__all__ = [
    "ImportedMailAttachment",
    "ImportedMailPackage",
    "ExcelWorkbookGateway",
    "ExcelComLTRWorkbookGateway",
    "LtrWorkbookFormat",
    "LtrWorkbookGatewayError",
    "LtrWorkbookReadOnlyError",
    "LtrWorkbookRowData",
    "LtrWorkbookRowPointer",
    "LtrWorkbookWriteConfig",
    "LtrWorkbookWriteDisabledError",
    "LtrWorkbookWriteError",
    "LtrWorkbookSnapshot",
    "MsgCompatibilityResult",
    "MsgCompatibilityStatus",
    "OfficeAutomationUnavailable",
    "OfficeFacade",
    "OfficeFileClassification",
    "OfficeFileKind",
    "OfficeLifecycleManager",
    "OutlookMsgAttachmentError",
    "OutlookMsgImportError",
    "OutlookMsgMetadataError",
    "UnreadableLtrWorkbookError",
    "UnsupportedLtrWorkbookError",
    "WordDocumentGateway",
    "WordDocumentSnapshot",
    "probe_msg_samples",
]
