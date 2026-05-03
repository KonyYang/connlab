# Quick Test Commands

This file provides quick copy-paste commands for manual smoke testing.

## Prerequisites

1. Start backend:
```powershell
.\scripts\run_backend.ps1
```

2. Prepare test data in `D:\test_samples\`:
   - `request.msg` - Outlook email file
   - `application_form.docx` - Application form (optional)

---

## Test Commands

### Test 1: Import MSG Package

```powershell
# Using curl (PowerShell 7+)
curl -X POST "http://localhost:8000/api/intake-packages/import-msg" `
  -F "file=@D:\test_samples\request.msg"

# Or using Invoke-RestMethod
$formData = @{ file = Get-Item "D:\test_samples\request.msg" }
Invoke-RestMethod -Uri "http://localhost:8000/api/intake-packages/import-msg" `
  -Method POST -Form $formData
```

**Expected**: Returns `package_id`, metadata, and attachments list.

---

### Test 2: Exception Workflow Review

Replace `{PACKAGE_ID}` with the actual package ID from Test 1:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/intake-packages/{PACKAGE_ID}/exceptions/review" `
  -Method POST
```

**Expected**: Returns package status and any issues.

---

### Test 6: LTR Readiness Check

Replace `{PROJECT_ID}` with your project ID:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/projects/{PROJECT_ID}/ltr/readiness" `
  -Method GET
```

**Expected**: Returns readiness status, blockers, and warnings.

---

### Test 7: LTR Preview

```powershell
$body = @{
    year = 2026
    month = 4
    registration_type = "normal"
    mode = "local_only"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/projects/{PROJECT_ID}/ltr/preview" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

**Expected**: Returns preview object WITHOUT writing to Excel workbook.

---

### Test 8: LTR Local Commit

```powershell
$body = @{
    year = 2026
    month = 4
    registration_type = "associated"
    mode = "local_only"
    proposed_ltr_number = "DL-2026-04-001A"
    operator_confirmed = $true
    requested_by = "Test User"
    operator_note = "Test commit"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/projects/{PROJECT_ID}/ltr/commit" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

**Expected**: Returns LTR record with audit notes.

---

### Test 10: Folder Preview

```powershell
$body = @{
    template_path = "templates/project_template"
    target_root = "data/projects"
    dl_number = "DL-2026-04-001"
    plan_date = "2026-04-29"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/projects/{PROJECT_ID}/folder/preview" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

**Expected**: Returns folder plan with directories/files to create.

---

### Test 11: Evidence Placement Preview

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/projects/{PROJECT_ID}/evidence/placement-preview" `
  -Method POST
```

**Expected**: Returns evidence placement plan showing source and target paths.

---

### Test 12: Lifecycle Guards (Invalid Operation)

```powershell
# Try on non-existent project - should return 404
try {
    Invoke-RestMethod -Uri "http://localhost:8000/api/projects/nonexistent/ltr/readiness" `
      -Method GET
} catch {
    Write-Host "Correctly rejected: $($_.Exception.Response.StatusCode)"
}
```

**Expected**: HTTP 404 error with clear message.

---

### Test 13: Project Lookup

```powershell
# Search by LTR number
Invoke-RestMethod -Uri "http://localhost:8000/api/projects/lookup?q=DL-2026-04-001" `
  -Method GET

# Search by part number
Invoke-RestMethod -Uri "http://localhost:8000/api/projects/lookup?q=PN-100" `
  -Method GET

# Sample summary
Invoke-RestMethod -Uri "http://localhost:8000/api/projects/{PROJECT_ID}/sample-summary" `
  -Method GET

# Testing summary
Invoke-RestMethod -Uri "http://localhost:8000/api/projects/{PROJECT_ID}/testing-summary" `
  -Method GET
```

**Expected**: Returns matching projects or summaries.

---

## Python Verification Scripts

After completing tests, verify data integrity:

```powershell
# Verify project entities
python test_by_third\verify_entities.py --project-id {PROJECT_ID}

# Verify LTR record
python test_by_third\verify_ltr_record.py --project-id {PROJECT_ID}

# Check folder structure
python test_by_third\check_folder_structure.py --project-id {PROJECT_ID}
```

---

## Database Inspection

```powershell
# Quick database check
python -c "
import sqlite3
conn = sqlite3.connect('data/connlab.sqlite3')
cursor = conn.cursor()

# List tables
cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")
print('Tables:', [row[0] for row in cursor.fetchall()])

# Count projects
cursor.execute('SELECT COUNT(*) FROM projects')
print('Projects:', cursor.fetchone()[0])

# Count LTR records
cursor.execute('SELECT COUNT(*) FROM ltr_records')
print('LTR Records:', cursor.fetchone()[0])

conn.close()
"
```

---

## Full Manual Test Flow

For complete Phase 7 validation, follow this sequence:

1. **Import MSG** → Get `package_id`
2. **Review Exceptions** → Check for issues
3. **Select Form** (via frontend) → Create case
4. **Confirm Case** (via frontend) → Get `project_id`
5. **Check LTR Readiness** → Identify blockers
6. **Fix Blockers** (update form data if needed)
7. **Preview LTR** → Verify no workbook write
8. **Commit LTR Locally** → Get LTR number
9. **Preview Folder** → Check for conflicts
10. **Generate Folder** → Create directory structure
11. **Preview Evidence** → Verify placement paths
12. **Place Evidence** → Copy files safely
13. **Verify All** → Use Python scripts above

---

## Tips

- Use Postman or similar tool for easier API testing
- Save responses to files for later inspection
- Take screenshots of successful operations
- Document any errors or unexpected behavior
- Clean up test data after completion (optional)

For detailed test steps and expected results, see `SMOKE_TEST_GUIDE.md`.
