"""Repository classes for ConnLab MVP persistence."""

from backend.infrastructure.storage.repositories.intake import (
    ApplicationFormRepository,
    SampleInfoRepository,
)
from backend.infrastructure.storage.repositories.intake_package import (
    IntakeAssetRepository,
    IntakeCaseRepository,
    IntakeDraftRepository,
    IntakePackageRepository,
)
from backend.infrastructure.storage.repositories.external_resources import (
    ExternalResourceRepository,
)
from backend.infrastructure.storage.repositories.frozen_field_revision_request import (
    FrozenFieldRevisionRequestRepository,
)
from backend.infrastructure.storage.repositories.lookup_options import LookupOptionRepository
from backend.infrastructure.storage.repositories.precheck import PrecheckResultRepository
from backend.infrastructure.storage.repositories.project_cleanup import (
    ProjectCleanupAuditRecordRepository,
)
from backend.infrastructure.storage.repositories.project import ProjectRepository
from backend.infrastructure.storage.repositories.project_test_plan import (
    ProjectTestPlanDraftRepository,
)
from backend.infrastructure.storage.repositories.source_matrix_import import (
    SourceMatrixImportRepository,
)
from backend.infrastructure.storage.repositories.project_output_record import (
    ProjectOutputRecordRepository,
)
from backend.infrastructure.storage.repositories.records import (
    FileAssetRepository,
    LtrRecordRepository,
    ProjectFolderRecordRepository,
)

__all__ = [
    "ApplicationFormRepository",
    "ExternalResourceRepository",
    "FileAssetRepository",
    "FrozenFieldRevisionRequestRepository",
    "IntakeAssetRepository",
    "IntakeCaseRepository",
    "IntakeDraftRepository",
    "IntakePackageRepository",
    "LtrRecordRepository",
    "LookupOptionRepository",
    "PrecheckResultRepository",
    "ProjectCleanupAuditRecordRepository",
    "ProjectFolderRecordRepository",
    "ProjectRepository",
    "ProjectOutputRecordRepository",
    "ProjectTestPlanDraftRepository",
    "SourceMatrixImportRepository",
    "SampleInfoRepository",
]
