"""Recognize measured temperature tables without confusing limits, fits or sample averages with maxima."""
import re

from docx.oxml.ns import qn


_TEMPERATURE = re.compile(r"temperature\s*rise|t[\s-]*rise|measured\s+rise|温升|Δ\s*T", re.I)
_CURRENT = re.compile(r"current|电流|(?:^|\s)amp", re.I)
_MAX = re.compile(r"\bmax(?:imum)?\b|最大", re.I)
_NOT_MEASURED = re.compile(
    r"\b(?:avg|average|mean|allow(?:ed|able)?|limit|spec(?:ification)?|requirement|target|"
    r"channel|ambient|fit(?:ted)?|source row)\b|≤|≥|平均|允许|限值", re.I)
_NON_CANDIDATE = re.compile(
    r"\b(?:avg|average|mean|allow(?:ed|able)?|limit|spec(?:ification)?|requirement|target|"
    r"ambient|fit(?:ted)?|source row)\b|≤|≥|平均|允许|限值", re.I)
_SAMPLE_MAX = re.compile(r"#\s*\d|\d\s*#|sample|single|group\s*\d|样品", re.I)
_NUMBER = re.compile(r"[-+]?\d+(?:[.,]\d+)?")
_NON_MEASUREMENT_ROW = re.compile(r"^(?:max(?:imum)?\s+)?(?:avg\b|average\b|mean\b|limit\b|allow(?:ed|able)\b|"
                                  r"acceptance\b|spec(?:ification)?\b|requirement\b|target\b|fit(?:ted)?\b|"
                                  r"calculated\b|model\b|限值|平均|允许)", re.I)


def _select_rows(table, rows, kept):
    for i, row in enumerate(rows):
        if i not in kept:
            table.remove(row)


def _select_columns(table, rows, columns):
    for row in rows:
        for index, cell in enumerate(row.findall(qn("w:tc"))):
            if index not in columns:
                row.remove(cell)
    grid = table.find(qn("w:tblGrid"))
    if grid is not None:
        for index, col in enumerate(grid.findall(qn("w:gridCol"))):
            if index not in columns:
                grid.remove(col)


def review_temperature_table(table, cells_text, context, index, review):
    if len(cells_text) < 2 or not cells_text[0]:
        return None
    header = cells_text[0]
    rows = table.findall(qn("w:tr"))
    first = header[0].strip()
    captions = [n for n, text in enumerate(context) if _TEMPERATURE.search(text)]
    label = " ".join(context[captions[-1]:]) if captions else ""
    first_column = " ".join(r[0] for r in cells_text[1:] if r)
    # A conclusions summary may use two merged header rows; it already contains
    # one maximum for each condition and is not an underlying measurements table.
    summary_columns = all((_MAX.search(v) and _TEMPERATURE.search(v) and not _NOT_MEASURED.search(v))
                          or re.fullmatch(r"Calculated current", v, re.I) for v in header[1:])
    if (re.fullmatch("Test Condition[s]?", first, re.I) and summary_columns
            and any(_MAX.search(v) and _TEMPERATURE.search(v) for v in header)):
        subheader = cells_text[1]
        data_start = 1
        if len(subheader) > len(header) and subheader[0] == "":
            column_headers = []
            for value, cell in zip(header, rows[0].findall(qn("w:tc")), strict=True):
                span = cell.find(f"{qn('w:tcPr')}/{qn('w:gridSpan')}")
                width = int(span.get(qn("w:val"), 1)) if span is not None else 1
                if not 1 <= width <= len(subheader):
                    raise ValueError("The temperature summary header has an invalid merged column.")
                column_headers.extend([value] * width)
            if len(column_headers) == len(subheader):
                header = [" ".join(filter(None, pair)) for pair in zip(column_headers, subheader, strict=True)]
                data_start = 2
        indices = [i for i, row in enumerate(cells_text) if i >= data_start and row
                   and not _NON_MEASUREMENT_ROW.search(row[0])]
        data_rows = [cells_text[i] for i in indices]
        if review.decisions is not None:
            _select_rows(table, rows, set(range(data_start)) | set(indices))
        summary = dict(label=label or "Maximum temperature rise by condition", headers=header, rows=data_rows)
        review.temperatures.append(summary)
        return summary
    current_cols = [i for i, col in enumerate(header) if not _NOT_MEASURED.search(col) and
                    (_CURRENT.search(col) or re.search(r"\b(conditions?|group)\b|工况", col, re.I))]
    max_cols = [i for i, col in enumerate(header) if _MAX.search(col) and not _NOT_MEASURED.search(col)]
    is_temperature = bool(label or _TEMPERATURE.search(first) or _TEMPERATURE.search(first_column)
                          or any(_TEMPERATURE.search(v) for v in header))
    if not is_temperature:
        return None
    vertical = current_cols and (max_cols or not any(_NUMBER.match(v.strip()) for v in header[1:]))
    if vertical and len({len(r) for r in cells_text}) == 1:
        data_indices = [i for i, row in enumerate(cells_text[1:], 1) if
                        not any(_NON_MEASUREMENT_ROW.search(row[c]) for c in current_cols)]
        candidates = [c for c, title in enumerate(header) if c not in current_cols and
                      not _NON_CANDIDATE.search(title) and any(_NUMBER.search(cells_text[i][c]) for i in data_indices)]
        if not candidates and not max_cols:
            return None
        label = label or "Measured temperature rise by condition"
        data = dict(label=label, headers=[header[c] for c in current_cols] + ["Measured maximum"], rows=[])
        selected = max_cols[0] if len(max_cols) == 1 else None
        if selected is None:
            options = []
            for c in max_cols or candidates:
                values = [[cells_text[i][j] for j in [*current_cols, c]] for i in data_indices]
                options.append(dict(value=f"c{c}", label=header[c], cells=values[0] if values else [], rows=values))
            data["decision_id"] = key = f"t{index}-maximum"
            data["options"] = options
            value = review.choice(dict(id=key, kind="temperature", label=label, options=options))
            selected = int(value[1:]) if value is not None else None
        if selected is not None:
            columns = sorted([*current_cols, selected])
            data["headers"] = [header[c] for c in columns]
            data["rows"] = [[cells_text[i][c] for c in columns] for i in data_indices]
            if review.decisions is not None:
                _select_columns(table, rows, columns)
                _select_rows(table, rows, {0, *data_indices})
        review.temperatures.append(data)
        return data
    # Numeric current columns distinguish T-rise detail from sequence, requirement
    # and step/result tables containing an incidental temperature row.
    if not (_CURRENT.search(first) or _TEMPERATURE.search(first) or label and not first):
        return None
    if not any(_NUMBER.search(v) for v in header[1:]):
        return None
    candidates = [i for i, row in enumerate(cells_text[1:], 1) if len(row) == len(header)
                  and row[0] and not _NON_CANDIDATE.search(row[0])
                  and any(_NUMBER.search(v) for v in row[1:])]
    maxima = [i for i in candidates if _MAX.search(cells_text[i][0]) and
              not _NOT_MEASURED.search(cells_text[i][0]) and not _SAMPLE_MAX.search(cells_text[i][0])]
    label = label or "Measured temperature rise"
    data = dict(label=label, headers=header, rows=[])
    if len(maxima) == 1:
        selected = maxima[0]
    else:
        options = [dict(value=f"r{i}", label=cells_text[i][0], cells=cells_text[i]) for i in candidates]
        if not options:
            raise ValueError(f"No measured rows were found in {label}. Check the source table and its units.")
        data["decision_id"] = key = f"t{index}-maximum"
        data["options"] = options
        value = review.choice(dict(id=key, kind="temperature", label=label, options=options))
        selected = int(value[1:]) if value is not None else None
    if selected is not None:
        data["rows"] = [cells_text[selected]]
        if review.decisions is not None:
            _select_rows(table, rows, {0, selected})
    review.temperatures.append(data)
    return data
