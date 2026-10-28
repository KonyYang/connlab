"""Parse supported instrument result rows without inferring sample mappings."""

import re

_NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)"


def parse_pdf_rows(text: str, kind: str) -> list[dict]:
    """Extract recognizable rows; unknown formats are rejected rather than guessed."""
    patterns = {
        "hold": rf"^(\d+\.\d+)\s+(\S+)\s+({_NUMBER})\s+({_NUMBER})\s+({_NUMBER})\s+({_NUMBER})$",
        "hold_end1": rf"^(\d+\.\d+)\s+(\S+)\s+({_NUMBER})\s+({_NUMBER})\s+({_NUMBER})\s+({_NUMBER})$",
        "retention": rf"^(\d+)\s+(\S+)\s+({_NUMBER})\s+({_NUMBER})$",
        "mating": rf"^(\d+)\s+\d+\s+({_NUMBER})\s+({_NUMBER})\s+({_NUMBER})\s+({_NUMBER})$",
    }
    if kind not in patterns:
        raise ValueError("Unsupported test type.")
    result = []
    # Axes and footers can resemble result rows; do not parse the curve region.
    result_text = text.split('序列曲线:', 1)[0].split('序列曲线：', 1)[0]
    for line in result_text.splitlines():
        match = re.match(patterns[kind], line.strip())
        if not match:
            continue
        groups = match.groups()
        if any(row['curve'] == groups[0] for row in result):
            raise ValueError('Duplicate curve identifier in this source; review the instrument record.')
        if kind == "mating":
            result.append({"curve": groups[0], "sample": "", "mating": float(groups[1]), "withdraw": float(groups[2])})
        else:
            result.append({"curve": groups[0], "sample": groups[1], "value": float(groups[3] if kind == 'hold_end1' else groups[2])})
    return result


def verify_reviewed_pdf(source: list[dict], reviewed: list[dict], kind: str) -> list[dict]:
    """Keep measurements bound to their original curve; mappings require explicit review."""
    if kind not in {'hold', 'hold_end1', 'retention', 'mating'}:
        raise ValueError('Unsupported test type.')
    if not source or not isinstance(reviewed, list) or len(source) != len(reviewed):
        raise ValueError('All source rows must be reviewed.')
    fields = ('mating', 'withdraw') if kind == 'mating' else ('value',)
    original = {row['curve']: row for row in source}
    seen = set()
    for row in reviewed:
        if not isinstance(row, dict):
            raise ValueError('Review the result rows.')
        curve = row.get('curve')
        if curve not in original or curve in seen:
            raise ValueError('Curve identifiers must match source rows exactly.')
        seen.add(curve)
        if not isinstance(row.get('sample'), str) or not row['sample'].strip():
            raise ValueError('Confirm a sample for every source row.')
        for field in fields:
            if isinstance(row.get(field), bool) or row.get(field) != original[curve][field]:
                raise ValueError('A reviewed measurement differs from its source.')
    return reviewed
