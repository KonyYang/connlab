# TASK_151 New Project LTR Workbook Authority

> Status: proposed
> Created: 2026-05-09
> Phase: Phase 10E - External resource settings and LTR workbook authority

---

## 1. Purpose

Make New Project `Apply LTR Number` use the configured LTR workbook as the current authoritative number source and write target.

The long-term architecture is structured server data, but the current lab reality is shared/public-drive Excel. ConnLab must satisfy that reality without hard-coding Excel into UI or high-level project workflow.

---

## 2. Current Code Reality

Current behavior:

- New Project `Apply LTR Number` calls `complete-new-project`.
- The backend confirms the intake case, creates/loads the project, and registers an LTR.
- Auto numbering currently searches local SQLite `LtrRecord` values.
- This means local SQLite can assign a number without seeing numbers already present in the public workbook.

Existing related capability:

- LTR workbook preview/write commit services exist.
- Settings can load workbook path/write settings from `connlab.local.toml` or environment variables.
- External resource registry can store an `ltr_workbook` path.

Gap:

- New Project is not currently treating the configured workbook as the authority for number calculation and write.

---

## 3. Scope

In scope:

- Introduce or clarify an application-level LTR number authority boundary.
- Configure current authority as Excel workbook-backed.
- Read current numbers from configured LTR workbook before auto-numbering.
- Preview workbook write target before commit.
- Use existing lock, backup, short transaction write path.
- Write workbook first, then persist local SQLite `LtrRecord`.
- If workbook write fails, do not create a local registered LTR as if the official application succeeded.
- Preserve specified-number behavior and suffix-token rules from `TASK_137`/`TASK_138`/`TASK_147`.
- Surface actionable errors in New Project when workbook settings are missing, invalid, locked, or write-disabled.

Out of scope:

- No server implementation.
- No data migration from workbook into server.
- No native Settings file picker.
- No Matrix, Report, AI review, email sending, permissions, or LAN deployment.

---

## 4. Authority Design

The business flow should depend on an authority concept, not on Excel directly.

Conceptual boundary:

```text
New Project completion
  -> LTR number authority
      -> current adapter: configured Excel workbook
      -> future adapter: server/database
```

This keeps the future server cutover concentrated in one adapter boundary.

---

## 5. Workflow

Auto number:

1. Load configured active LTR workbook path.
2. Read workbook numbers for the target year/month.
3. Merge or compare with local SQLite records as a diagnostic only.
4. Calculate next `DL-YYYY-MM-NNN`.
5. Preview write target row.
6. Lock workbook and create backup.
7. Re-read or re-check numbers inside the short transaction.
8. Write workbook row.
9. Persist local `LtrRecord`.
10. Return project id, project status, LTR number, workbook path, sheet, row, backup path.

Specified number:

1. Normalize and validate specified input.
2. Verify it does not conflict with workbook numbers.
3. Write workbook row.
4. Persist local `LtrRecord`.

---

## 6. Development Mode

During development, the workbook path should point to a local simulated public-drive file, configured through Settings.

Example local structure:

```text
D:\test_samples\connlab_external_resources\
  ltr\LTR_number_update.xlsx
  ltr\backups\
  ltr\locks\
```

Code must not distinguish local path vs public-drive path. Both are configured resources.

---

## 7. Tests And Validation

Expected validation:

```powershell
py -m pytest tests\unit\test_ltr_number_rules.py tests\unit\test_ltr_workbook_write_commit_service.py tests\integration\test_ltr_workbook_write_commit_api.py -q
py -m pytest tests\integration\test_new_project_completion_api.py -q
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "new_project or ltr"
cd frontend
npm run build
```

Manual smoke:

1. Configure a local simulated LTR workbook in Settings.
2. Import a New Project package.
3. Click `Apply LTR Number`.
4. Confirm the assigned number comes from workbook-visible numbers.
5. Confirm workbook row is written.
6. Confirm local SQLite contains the same LTR record only after workbook write success.

---

## 8. Acceptance Criteria

- New Project no longer assigns official LTR numbers from local SQLite alone.
- Configured LTR workbook is the current authority.
- Workbook write failure blocks official LTR registration.
- Local SQLite remains the structured copy after successful write.
- The design remains adapter-ready for future server authority.

