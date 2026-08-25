from backend.application.matrix_record_sample_quantity import (
    parse_simple_positive_sample_count,
    resolve_matrix_record_sample_count,
)


def test_simple_positive_sample_count_accepts_alphabetic_footnotes_only() -> None:
    assert parse_simple_positive_sample_count("3(a)") == 3
    assert parse_simple_positive_sample_count("3(a)(b)") == 3
    assert parse_simple_positive_sample_count("3(a)+3(b)") is None
    assert parse_simple_positive_sample_count("0(a)") is None
    assert parse_simple_positive_sample_count("3.5(a)") is None


def test_split_sample_count_still_requires_record_specific_note() -> None:
    expression = "3(a)+3(b)"

    assert resolve_matrix_record_sample_count(expression, None, "llcr") is None
    assert (
        resolve_matrix_record_sample_count(
            expression,
            "3 pcs for LLCR; 3 pcs for CR",
            "llcr",
        )
        == 3
    )
