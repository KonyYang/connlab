"""Label aliases used by the DOCX application form parser."""

from __future__ import annotations

LABEL_ALIASES: dict[str, set[str]] = {
    "form_no": {"form no", "form number"},
    "form_rev": {"form rev", "rev", "revision", "revision level"},
    "reference_doc": {"reference doc", "reference document"},
    "lab_test_request_number": {
        "lab test request number",
        "lab test requirement number",
        "ltr number",
        "ltr no",
    },
    "requested_by": {"requested by", "requester", "requestor", "requested by requestor"},
    "phone": {"phone", "phone number", "telephone", "tel"},
    "request_date": {"date", "request date"},
    "email": {"email", "e-mail"},
    "business_unit": {"business unit", "bu"},
    "manufacturing_site": {"mfg site", "manufacturing site", "manufacture site"},
    "project_number": {"project #", "project no", "project number", "project"},
    "requested_completion_date": {
        "requested testing completion date",
        "completion date",
    },
    "results_format": {"results format"},
    "test_type": {"test type"},
    "sample_status": {"sample status"},
    "project_type": {"project type"},
    "post_testing_disposition": {"post-testing disposition", "post testing disposition"},
    "requested_testing_description": {
        "description of requested testing",
        "requested testing",
        "test request",
        "testing requested",
    },
    "confidential": {"confidential"},
    "subcontract": {"subcontract", "sub contract", "subcontract permission"},
    "additional_information": {"additional information"},
    "send_copies_recipients": {
        "send copies",
        "send copies recipients",
        "send copy to",
        "send copies of test results/reports to",
    },
    "lab": {"lab", "lab performing the tests"},
    "assigned_personnel": {"assigned personnel", "assigned person", "project leader"},
    "received_date": {"received date"},
    "estimated_completion_date": {"estimated completion date"},
    "sample_condition": {"sample condition"},
}

SAMPLE_ALIASES: dict[str, set[str]] = {
    "product_name": {"product name", "product", "product description"},
    "part_number": {
        "part number",
        "part number/revision",
        "part number / revision",
        "part no",
        "pn",
        "p n",
    },
    "revision": {"revision", "rev"},
    "lot_or_traceability": {
        "lot",
        "traceability",
        "lot/traceability",
        "lot traceability",
        "lot no",
        "traceability manufacturing lot info",
    },
    "material": {"material", "contact base material"},
    "plating": {"plating", "contact plating"},
    "lubricant": {"lubricant", "contact lubricant"},
    "housing_material": {"housing material"},
    "quantity": {"quantity", "qty"},
}
