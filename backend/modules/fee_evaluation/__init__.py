"""Fee-rule seed loading and deterministic matching utilities."""

from backend.modules.fee_evaluation.fee_rule_matcher import (
    FeeRuleMatchResult,
    FeeRuleMatcher,
    match_fee_rule_text,
    normalize_fee_rule_text,
)
from backend.modules.fee_evaluation.fee_rule_activation_validator import (
    FeeRuleActivationValidationError,
    validate_candidate_activation,
)
from backend.modules.fee_evaluation.fee_rule_candidate_builder import (
    FeeReferenceCandidateRow,
    build_fee_rule_library_candidate,
    fee_rule_library_to_seed_json,
)
from backend.modules.fee_evaluation.fee_rule_library_diff import (
    FeeRuleDiffEntry,
    FeeRuleFieldChange,
    FeeRuleLibraryDiff,
    diff_fee_rule_libraries,
)
from backend.modules.fee_evaluation.fee_rule_models import (
    ALLOWED_CALCULATION_STRATEGIES,
    ALLOWED_UNIT_LABELS,
    SUPPORTED_EFFECTIVE_FROM_BASES,
    CalculationStrategy,
    FeeAmount,
    FeeRule,
    FeeRuleLibrary,
    FeeRuleMatchStatus,
    FeeRuleSourceKind,
    FeeRuleSeedValidationError,
    FeeRuleVersion,
)
from backend.modules.fee_evaluation.fee_default_fill import build_fee_default_fill
from backend.modules.fee_evaluation.fee_default_fill_models import (
    FeeDefaultField,
    FeeDefaultFieldState,
    FeeDefaultFillContext,
    FeeDefaultFillResult,
    FeeFieldMetadata,
    CrSpecifiedCurrentAuthority,
    FeeStepQuantityContext,
)
from backend.modules.fee_evaluation.fee_rule_seed_loader import (
    FeeRuleSeedLoaderError,
    load_active_fee_rule_library,
    load_fee_rule_library,
)

__all__ = [
    "ALLOWED_CALCULATION_STRATEGIES",
    "ALLOWED_UNIT_LABELS",
    "SUPPORTED_EFFECTIVE_FROM_BASES",
    "CalculationStrategy",
    "FeeAmount",
    "FeeDefaultField",
    "FeeDefaultFieldState",
    "FeeDefaultFillContext",
    "FeeDefaultFillResult",
    "FeeFieldMetadata",
    "CrSpecifiedCurrentAuthority",
    "FeeStepQuantityContext",
    "FeeReferenceCandidateRow",
    "FeeRuleActivationValidationError",
    "FeeRuleDiffEntry",
    "FeeRuleFieldChange",
    "FeeRule",
    "FeeRuleLibrary",
    "FeeRuleLibraryDiff",
    "FeeRuleMatchResult",
    "FeeRuleMatchStatus",
    "FeeRuleSourceKind",
    "FeeRuleMatcher",
    "FeeRuleSeedLoaderError",
    "FeeRuleSeedValidationError",
    "FeeRuleVersion",
    "build_fee_rule_library_candidate",
    "build_fee_default_fill",
    "diff_fee_rule_libraries",
    "fee_rule_library_to_seed_json",
    "load_active_fee_rule_library",
    "load_fee_rule_library",
    "match_fee_rule_text",
    "normalize_fee_rule_text",
    "validate_candidate_activation",
]
