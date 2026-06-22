"""Application Form Word field mapping constants."""

APPLICATION_FORM_FIELD_LABELS: dict[str, tuple[str, ...]] = {
    "ltr_number": ("ltr number", "lab test request number", "dl number"),
    "project_number": ("project number", "project no"),
    "project_type": ("project type",),
    "test_type": ("test type",),
    "test_sample_status": ("test sample status", "sample status"),
    "description_pn": ("description p n", "description pn", "p n"),
    "product_description": ("product description", "product name", "product"),
    "test_item": (
        "test item",
        "requested testing",
        "requested testing description",
        "test to be performed",
        "tests to be performed",
    ),
    "applicable_specifications": (
        "applicable specifications",
        "applicable specification",
    ),
    "requester": ("requester", "requestor", "requested by", "requested by requestor"),
    "requested_by": ("requester", "requestor", "requested by", "requested by requestor"),
    "phone": ("phone", "telephone", "tel"),
    "email": ("email", "e mail", "e-mail of requestor"),
    "business_unit": ("business unit", "bu"),
    "location": ("mfg site", "manufacturing site", "site"),
    "manufacturing_site": ("mfg site", "manufacturing site", "site"),
    "requested_completion_date": (
        "requested completion date",
        "request completion date",
        "requested testing completion date",
    ),
    "confidential": ("confidential tests or samples", "confidential"),
    "sub_contract": ("can testing be subcontracted", "subcontracted", "sub-contract"),
    "send_report_copies_to": (
        "send copies of test results reports to",
        "send copies of test results/reports to",
    ),
    "lab": ("lab", "laboratory", "lab performing the tests"),
    "project_leader": (
        "lab personnel assigned",
        "assigned personnel",
        "assigned engineer",
        "test engineer",
        "tested by",
    ),
    "assigned_personnel": (
        "lab personnel assigned",
        "assigned personnel",
        "assigned engineer",
        "test engineer",
        "tested by",
    ),
    "received_date": (
        "date lab received samples",
        "received date",
        "sample received date",
    ),
    "estimated_completion_date": (
        "estimated completion date",
        "estimated complete date",
    ),
    "sample_condition": (
        "condition of samples when received",
        "sample condition",
        "sample received condition",
    ),
}

APPLICATION_FORM_NEXT_ROW_FIELDS = {
    "project_type",
    "test_type",
    "test_sample_status",
    "test_item",
    "applicable_specifications",
}

APPLICATION_FORM_CRITICAL_FIELDS = {
    "ltr_number",
    "requested_by",
    "requester",
    "location",
    "manufacturing_site",
    "test_item",
    "applicable_specifications",
    "lab",
}
