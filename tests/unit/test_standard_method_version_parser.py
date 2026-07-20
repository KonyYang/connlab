from __future__ import annotations

from backend.modules.test_plan.standard_method_version_parser import (
    CatalogMethod,
    build_method_proposal,
    parse_catalog_method,
    parse_matrix_method,
    resolve_catalog_candidates,
)


def test_method_revision_is_replaced_without_importing_catalog_year() -> None:
    current = parse_matrix_method("Condition per ANSI / EIA-364-04A-2010 at room temp")
    catalog = parse_catalog_method("ANSI/EIA-364-04B-2015", source_row_number=3)

    proposal = build_method_proposal(current, (catalog,))

    assert proposal.status == "update_available"
    assert proposal.proposed_method == (
        "Condition per ANSI / EIA-364-04B-2010 at room temp"
    )
    assert proposal.catalog_year == 2015


def test_missing_revision_gets_unique_revision_and_same_revision_is_current() -> None:
    candidate = parse_catalog_method("EIA-364-18B", source_row_number=4)

    missing = build_method_proposal(parse_matrix_method("EIA-364-18"), (candidate,))
    current = build_method_proposal(parse_matrix_method("eia-364-18B"), (candidate,))

    assert missing.status == "revision_missing"
    assert missing.proposed_method == "EIA-364-18B"
    assert current.status == "current"
    assert current.proposed_method is None


def test_distinct_revisions_are_ambiguous_and_lower_catalog_is_downgrade() -> None:
    ambiguous = resolve_catalog_candidates(
        (
            CatalogMethod("EIA-364-04B", "04", "B", None, 3),
            CatalogMethod("EIA-364-04C", "04", "C", None, 4),
        )
    )
    downgrade = build_method_proposal(
        parse_matrix_method("EIA-364-04C"),
        (CatalogMethod("EIA-364-04B", "04", "B", None, 3),),
    )

    assert ambiguous["04"].status == "ambiguous"
    assert downgrade.status == "downgrade_conflict"
    assert downgrade.proposed_method is None


def test_multiple_cores_and_unrelated_letters_do_not_leak_revision_state() -> None:
    first = parse_matrix_method("Method EIA-364-04A and EIA-364-18B")
    second = parse_matrix_method("EIA-364-04 year 2015")

    assert first.status == "multiple_method_cores"
    assert second.status == "parsed"
    assert second.revision is None
