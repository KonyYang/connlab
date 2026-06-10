"""Office gateway package."""

from backend.infrastructure.office.models import (
    ExcelTabularReadResult,
    ExcelStructureProbeResult,
    ImportedMailAttachment,
    ImportedMailPackage,
    LtrWorkbookFormat,
    LtrWorkbookSnapshot,
    OfficeFileClassification,
    OfficeFileKind,
    WordDocumentSnapshot,
    WordHeaderCellResult,
    WordSection2FieldChange,
    WordSection2WriteResult,
    TestRecordDocumentWriteResult,
    FeeEvaluationWorkbookWriteResult,
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
    LtrWorkbookDropdownEnsureResult,
    LtrWorkbookExistingRow,
    LtrWorkbookSheetPreparationResult,
    LtrWorkbookReadOnlyError,
    LtrWorkbookRowData,
    LtrWorkbookRowPointer,
    LtrWorkbookWriteConfig,
    LtrWorkbookWriteDisabledError,
    LtrWorkbookWriteError,
)
from backend.infrastructure.office.ltr_workbook_transaction_gateway import (
    LtrWorkbookBackupError,
    LtrWorkbookLockTimeoutError,
    LtrWorkbookTransactionConfig,
    LtrWorkbookTransactionContext,
    LtrWorkbookTransactionGateway,
)
from backend.infrastructure.office.outlook_msg_gateway import (
    OutlookMsgAttachmentError,
    OutlookMsgImportError,
    OutlookMsgMetadataError,
)
from backend.infrastructure.office.word_document_gateway import WordDocumentGateway
from backend.infrastructure.office.test_record_document_gateway import TestRecordDocumentGateway
from backend.infrastructure.office.fee_evaluation_workbook_gateway import FeeEvaluationWorkbookGateway
from backend.infrastructure.office.customer_feedback_workbook_gateway import (
    CustomerFeedbackWorkbookGateway,
)

__all__ = [
    "ImportedMailAttachment",
    "ImportedMailPackage",
    "ExcelWorkbookGateway",
    "ExcelTabularReadResult",
    "ExcelStructureProbeResult",
    "ExcelComLTRWorkbookGateway",
    "LtrWorkbookFormat",
    "LtrWorkbookBackupError",
    "LtrWorkbookDropdownEnsureResult",
    "LtrWorkbookExistingRow",
    "LtrWorkbookSheetPreparationResult",
    "LtrWorkbookGatewayError",
    "LtrWorkbookLockTimeoutError",
    "LtrWorkbookReadOnlyError",
    "LtrWorkbookRowData",
    "LtrWorkbookRowPointer",
    "LtrWorkbookTransactionConfig",
    "LtrWorkbookTransactionContext",
    "LtrWorkbookTransactionGateway",
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
    "WordHeaderCellResult",
    "WordSection2FieldChange",
    "WordSection2WriteResult",
    "TestRecordDocumentWriteResult",
    "FeeEvaluationWorkbookWriteResult",
    "TestRecordDocumentGateway",
    "FeeEvaluationWorkbookGateway",
    "CustomerFeedbackWorkbookGateway",
    "probe_msg_samples",
]
