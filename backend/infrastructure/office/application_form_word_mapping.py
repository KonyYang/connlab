"""Application Form Word field mapping constants."""

APPLICATION_FORM_FIELD_LABELS: dict[str, tuple[str, ...]] = {
    "ltr_number": ("ltr number", "lab test request number", "dl number"),
    "project_number": ("project number", "project no"),
    "project_type": ("project type",),
    "test_type": ("test type",),
    "test_sample_status": ("test sample status", "sample status"),
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
}

APPLICATION_FORM_CRITICAL_FIELDS = {
    "ltr_number",
    "lab",
    "project_leader",
    "received_date",
    "estimated_completion_date",
    "sample_condition",
}
