"""Office gateway package."""

from backend.infrastructure.office.models import (
    ImportedMailAttachment,
    ImportedMailPackage,
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
from backend.infrastructure.office.outlook_msg_gateway import (
    OutlookMsgAttachmentError,
    OutlookMsgImportError,
    OutlookMsgMetadataError,
)
from backend.infrastructure.office.word_document_gateway import WordDocumentGateway

__all__ = [
    "ImportedMailAttachment",
    "ImportedMailPackage",
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
    "WordDocumentGateway",
    "WordDocumentSnapshot",
    "probe_msg_samples",
]
