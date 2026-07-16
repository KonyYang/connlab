"""Compile source snapshots and reviewed extensions into runtime fee-rule seeds."""

from __future__ import annotations

import os
from dataclasses import replace
from pathlib import Path

from backend.modules.fee_evaluation.fee_reference_snapshot import (
    FeeReferenceSnapshotError,
    FeeReferenceRow,
    FeeReferenceSnapshot,
    load_fee_reference_snapshot,
)
from backend.modules.fee_evaluation.fee_rule_candidate_builder import fee_rule_library_to_seed_json
from backend.modules.fee_evaluation.fee_rule_extensions import (
    FeeRuleExtensionError,
    FeeRuleExtensionSet,
    FeeSourceRuleExtension,
    load_fee_rule_extensions,
)
from backend.modules.fee_evaluation.fee_rule_models import (
    FeeAmount,
    FeeRule,
    FeeRuleLibrary,
)
from backend.modules.fee_evaluation.fee_rule_seed_loader import validate_fee_rule_library


class FeeRuleCompileError(ValueError):
    """Raised when the snapshot and extensions cannot form one valid seed."""


def compile_fee_rule_library(
    snapshot: FeeReferenceSnapshot,
    extensions: FeeRuleExtensionSet,
) -> FeeRuleLibrary:
    """Compile source facts and reviewed extensions into one validated library."""
    _validate_source_identity(snapshot, extensions)
    mappings = {mapping.source_row: mapping for mapping in extensions.source_rules}
    source_rules = tuple(
        _compile_source_rule(row, mappings[row.source_row])
        for row in sorted(snapshot.rows, key=lambda item: item.source_row)
    )
    extension_rules = tuple(
        replace(rule, source_kind="reviewed_extension", source_row=None)
        for rule in extensions.extension_rules
    )
    library = FeeRuleLibrary(
        version=extensions.version,
        rules=source_rules + extension_rules,
    )
    validate_fee_rule_library(library)
    return library


def compile_fee_rule_seed_files(
    snapshot_path: Path,
    extensions_path: Path,
    output_path: Path,
) -> FeeRuleLibrary:
    """Compile validated JSON inputs and atomically replace the output seed file."""
    try:
        snapshot = load_fee_reference_snapshot(snapshot_path)
        extensions = load_fee_rule_extensions(extensions_path)
        library = compile_fee_rule_library(snapshot, extensions)
    except (FeeReferenceSnapshotError, FeeRuleExtensionError) as exc:
        raise FeeRuleCompileError("Unable to compile fee rule seed from reviewed inputs.") from exc
    serialized = fee_rule_library_to_seed_json(library)
    temporary_path = output_path.with_name(f".{output_path.name}.tmp")
    try:
        temporary_path.write_text(serialized, encoding="utf-8")
        os.replace(temporary_path, output_path)
    except OSError as exc:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise FeeRuleCompileError(f"Unable to write compiled fee rule seed: {output_path}") from exc
    return library


def _validate_source_identity(
    snapshot: FeeReferenceSnapshot,
    extensions: FeeRuleExtensionSet,
) -> None:
    """Require both layers to identify the same approved workbook authority."""
    source = snapshot.source
    version = extensions.version
    if source.source_file_name != version.source_file_name:
        raise FeeRuleCompileError("Snapshot and extensions use different source file names.")
    if source.source_sheet != version.source_sheet:
        raise FeeRuleCompileError("Snapshot and extensions use different source sheets.")
    if source.source_hash != version.source_hash:
        raise FeeRuleCompileError("Snapshot and extensions use different source hashes.")


def _compile_source_rule(
    row: FeeReferenceRow,
    mapping: FeeSourceRuleExtension,
) -> FeeRule:
    """Combine one raw source row with its reviewed runtime interpretation."""
    return FeeRule(
        rule_id=mapping.rule_id,
        display_name=row.english_description,
        aliases=_merged_aliases(
            row.english_description,
            row.chinese_description,
            *mapping.aliases,
        ),
        base_fee=FeeAmount(amount=mapping.base_fee_amount, text=row.base_fee_text),
        unit_price=FeeAmount(amount=mapping.unit_price_amount, text=row.unit_price_text),
        unit_label=mapping.unit_label,
        applicable_standard=row.applicable_standard,
        range_condition=row.range_condition,
        calculation_strategy=mapping.calculation_strategy,
        review_required=mapping.review_required,
        review_reason=mapping.review_reason,
        source_kind="unit_price_reference",
        source_row=row.source_row,
    )


def _merged_aliases(*values: str) -> tuple[str, ...]:
    """Preserve alias order while removing normalized duplicates within one rule."""
    aliases: list[str] = []
    normalized_seen: set[str] = set()
    for value in values:
        alias = value.strip()
        if not alias:
            continue
        normalized = " ".join(alias.lower().split())
        if normalized in normalized_seen:
            continue
        normalized_seen.add(normalized)
        aliases.append(alias)
    return tuple(aliases)
