# MVP Domain Model

## Project

Fields:

- id
- dl_number
- title
- product_name
- requestor
- business_unit
- project_no
- status
- root_folder
- created_at
- updated_at

Statuses for MVP:

- DRAFT
- PRECHECK_REQUIRED
- PRECHECK_PASSED
- LTR_REGISTERED
- FOLDER_CREATED

## ApplicationForm

Fields:

- id
- project_id
- source_file_id
- form_no
- form_rev
- reference_doc
- lab_test_request_number
- requested_by
- phone
- request_date
- email
- business_unit
- manufacturing_site
- project_no
- requested_completion_date
- results_format
- test_type
- sample_status
- project_type
- description_of_requested_testing
- additional_information
- subcontract_allowed
- lab_performing_tests
- lab_personnel_assigned
- date_lab_received_samples
- estimated_completion_date
- sample_condition
- extracted_at

## SampleInfo

Fields:

- id
- application_form_id
- product_name
- part_number_revision
- traceability_lot
- contact_base_material
- contact_plating
- contact_lubricant
- housing_material
- quantity

## PrecheckResult

Fields:

- id
- project_id
- application_form_id
- status: PASSED/WARNING/FAILED
- checker_version
- checked_at

## PrecheckIssue

Fields:

- id
- result_id
- level: ERROR/WARNING/INFO
- category: FORM/REQUESTOR/SAMPLE/TESTING/ATTACHMENT/LAB_SECTION/SCHEDULE
- field
- message
- expected
- actual
- suggestion
- resolved
- resolution_note
- resolved_at

## LtrRecord

Fields:

- id
- project_id
- ltr_number
- status: DRAFT/REGISTERED/CANCELLED
- requested_by
- requested_date
- application_form_file_id
- notes

## ProjectFolderRecord

Fields:

- id
- project_id
- template_path
- target_path
- created_at
- generated_files_json

## FileAsset

Fields:

- id
- project_id
- asset_type
- original_name
- stored_path
- checksum
- created_at
