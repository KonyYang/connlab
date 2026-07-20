"""Pure parser and proposal policy for EIA-364 Matrix Method revisions."""

from __future__ import annotations

import re
from dataclasses import dataclass


_HYPHENS = str.maketrans({value: "-" for value in "‐‑‒–—−"})
_MATRIX_CORE = re.compile(r"364\s*-\s*(?P<number>\d{2})(?P<revision>[A-Z])?", re.I)
_CATALOG_CODE = re.compile(
    r"(?:ANSI\s*/\s*)?EIA\s*-\s*364\s*-\s*"
    r"(?P<number>\d{2})(?P<revision>[A-Z])"
    r"(?:\s*-\s*(?P<year>\d{4}))?",
    re.I,
)


@dataclass(frozen=True, slots=True)
class MatrixMethod:
    original: str
    status: str
    core: str | None = None
    revision: str | None = None
    number_end: int | None = None
    revision_span: tuple[int, int] | None = None


@dataclass(frozen=True, slots=True)
class CatalogMethod:
    source_code: str
    core: str
    revision: str
    year: int | None
    source_row_number: int | None


@dataclass(frozen=True, slots=True)
class CatalogResolution:
    status: str
    candidate: CatalogMethod | None = None


@dataclass(frozen=True, slots=True)
class MethodProposal:
    status: str
    method_core: str | None
    proposed_method: str | None = None
    matched_standard_code: str | None = None
    catalog_revision: str | None = None
    catalog_year: int | None = None
    source_row_number: int | None = None
    reason: str | None = None


def parse_matrix_method(value: str | None) -> MatrixMethod:
    """Parse exactly one EIA-364 method core while retaining original spans."""
    original = value or ""
    normalized = original.translate(_HYPHENS)
    matches = list(_MATRIX_CORE.finditer(normalized))
    if not matches:
        return MatrixMethod(original=original, status="no_method_core")
    if len(matches) != 1:
        return MatrixMethod(original=original, status="multiple_method_cores")
    match = matches[0]
    revision = match.group("revision")
    revision_span = match.span("revision") if revision else None
    return MatrixMethod(
        original=original,
        status="parsed",
        core=match.group("number"),
        revision=revision.upper() if revision else None,
        number_end=match.end("number"),
        revision_span=revision_span,
    )


def parse_catalog_method(
    value: str | None,
    *,
    source_row_number: int | None = None,
) -> CatalogMethod | None:
    """Parse one catalog code with an immediate revision and optional year."""
    source = (value or "").strip()
    matches = list(_CATALOG_CODE.finditer(source.translate(_HYPHENS)))
    if len(matches) != 1:
        return None
    match = matches[0]
    year = match.group("year")
    return CatalogMethod(
        source_code=source,
        core=match.group("number"),
        revision=match.group("revision").upper(),
        year=int(year) if year else None,
        source_row_number=source_row_number,
    )


def resolve_catalog_candidates(
    candidates: tuple[CatalogMethod | None, ...],
) -> dict[str, CatalogResolution]:
    """Resolve one deterministic candidate or ambiguity for each method core."""
    grouped: dict[str, list[CatalogMethod]] = {}
    for candidate in candidates:
        if candidate is not None:
            grouped.setdefault(candidate.core, []).append(candidate)
    resolved: dict[str, CatalogResolution] = {}
    for core, items in grouped.items():
        revisions = {item.revision for item in items}
        if len(revisions) != 1:
            resolved[core] = CatalogResolution(status="ambiguous")
            continue
        selected = sorted(
            items,
            key=lambda item: (
                -(item.year or 0),
                item.source_code.casefold(),
                item.source_row_number or 0,
            ),
        )[0]
        resolved[core] = CatalogResolution(status="resolved", candidate=selected)
    return resolved


def build_method_proposal(
    matrix: MatrixMethod,
    candidates: tuple[CatalogMethod | None, ...],
) -> MethodProposal:
    """Build one conservative row-local proposal."""
    if matrix.status != "parsed" or matrix.core is None:
        return MethodProposal(status=matrix.status, method_core=matrix.core)
    resolution = resolve_catalog_candidates(candidates).get(matrix.core)
    if resolution is None:
        return MethodProposal(status="catalog_missing", method_core=matrix.core)
    if resolution.status == "ambiguous" or resolution.candidate is None:
        return MethodProposal(status="ambiguous", method_core=matrix.core)
    candidate = resolution.candidate
    details = {
        "method_core": matrix.core,
        "matched_standard_code": candidate.source_code,
        "catalog_revision": candidate.revision,
        "catalog_year": candidate.year,
        "source_row_number": candidate.source_row_number,
    }
    if matrix.revision == candidate.revision:
        return MethodProposal(status="current", **details)
    if matrix.revision and matrix.revision > candidate.revision:
        return MethodProposal(status="downgrade_conflict", **details)
    if matrix.revision_span:
        start, end = matrix.revision_span
        proposed = matrix.original[:start] + candidate.revision + matrix.original[end:]
        status = "update_available"
    else:
        insertion = matrix.number_end or len(matrix.original)
        proposed = matrix.original[:insertion] + candidate.revision + matrix.original[insertion:]
        status = "revision_missing"
    return MethodProposal(status=status, proposed_method=proposed, **details)
