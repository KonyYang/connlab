# TASK_334D Project Folder Application Form Word Session Integration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task after explicit user approval. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove whether the 334C explicit Word COM session path shortens the real Project Folder Application Form write-back operation, then integrate it only if the production-path evidence gate passes.

**Architecture:** Keep the optimization behind the existing Office infrastructure boundary. The Project Folder Application Form write-back service remains the application-level owner of the operation, while `OfficeFacade` owns the optional Word session lifecycle and delegates to `WordDocumentGateway`; the application layer must not import or construct `ApplicationFormWordSession`.

**Tech Stack:** Python 3.11+, FastAPI application services, Windows Microsoft Word COM through pywin32, pytest.

## Global Constraints

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current active task: `TASK_334D_PROJECT_FOLDER_APPLICATION_FORM_WORD_SESSION_INTEGRATION`.
- This task is allowed because `TASK_334C` is complete and production Project Folder session wiring was explicitly left as a separate decision.
- Backend only.
- Do not change frontend, Project Folder API response contracts, progress modal UI, Application Form field scope, Application Form header layout, Basic Information behavior, Fee Form, Customer Feedback, Test Record, LTR workbook, Report generation, StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope.
- Do not introduce a global long-lived Word singleton.
- Do not attach to or close user-owned visible Word sessions.
- Use ConnLab-owned hidden Word instances only.
- Application code may call an Office port method such as `write_word_application_form_fields_with_owned_session(...)`, but must not import pywin32 or `ApplicationFormWordSession`.
- Integration is conditional: if interleaved production-path A/B timing does not pass the evidence gate, do not wire the session path into Project Folder.

---

## Current Real Chain

The current production write-back path is:

```text
ProjectFolderRequiredFormsService
  -> ProjectApplicationFormWriteBackService.write_back(project_id)
    -> OfficeFacade.write_word_application_form_fields(target, fields)
      -> WordDocumentGateway.write_application_form_fields(target, fields)
        -> write_application_form_fields_with_com(target, normalized_fields)
```

`TASK_334C` already added an optional session capability at the low-level COM writer. This task decides whether and how to expose that capability through the production path.

## File Structure

- Modify: `backend/infrastructure/office/office_facade.py`
  - Add a facade-owned scoped helper for Application Form write-back, for example `write_word_application_form_fields_with_owned_session(...)`.
  - The helper creates and owns `ApplicationFormWordSession` inside infrastructure.
  - Preserve existing method behavior for callers that do not pass a session.
- Modify: `backend/infrastructure/office/word_document_gateway.py`
  - Pass the optional session through to `write_application_form_fields_with_com()`.
  - Keep standalone default behavior unchanged.
- Modify: `backend/application/project_application_form_write_back_service.py`
  - Add a bounded call to a session-owning Office port method only if the evidence gate passes.
  - Do not import `ApplicationFormWordSession` in this file.
  - Keep `write_back(project_id)` semantics unchanged to callers.
- Modify: `tests/unit/test_application_form_word_gateway.py`
  - Cover optional session pass-through without invoking real COM.
- Modify: `tests/unit/test_project_application_form_write_back_service.py`
  - Cover production-path use of the session-aware Office seam if integrated.
- Modify: `tasks/TASK_334D_PROJECT_FOLDER_APPLICATION_FORM_WORD_SESSION_INTEGRATION.md`
  - Record evidence, integration decision, validation, and final stop point.
- Modify: `docs/task_board.md`
  - Update status and validation after implementation.

No frontend files should change in TASK_334D.

## Evidence Gate Details

Before wiring production behavior, run a same-process interleaved comparison:

```text
warm-up: current, candidate
pair 1: current, candidate
pair 2: candidate, current
pair 3: current, candidate
pair 4: candidate, current
pair 5: current, candidate
```

If five pairs are too expensive for live Office smoke, use at least three paired runs and record why.

Candidate qualifies only when:

- median Application Form write-back time improves by at least `15%` or `2.0s`
- Required Forms regression tests pass; optional Required Forms service graph timing may be recorded only if an equivalent candidate graph is built
- final document opens with `OpenAndRepair=False`
- no ConnLab-created `WINWORD.EXE` process remains after cleanup

## Task 1: Add a Narrow Infrastructure Session Seam

**Files:**

- Modify: `backend/infrastructure/office/office_facade.py`
- Modify: `backend/infrastructure/office/word_document_gateway.py`
- Test: `tests/unit/test_application_form_word_gateway.py`

**Interfaces:**

- Consumes: `ApplicationFormWordSession` inside `backend.infrastructure.office.office_facade`
- Produces:
  - existing `write_word_application_form_fields(...)` preserving current behavior
  - new facade-owned helper `write_word_application_form_fields_with_owned_session(...)`
  - optional gateway parameter used only from infrastructure/facade/tests

- [ ] Add failing gateway test for optional session pass-through.

Expected test shape:

```python
def test_application_form_writer_receives_optional_session(monkeypatch, tmp_path):
    captured = {}
    source = tmp_path / "request.docx"
    source.write_bytes(b"fake")
    session = object()

    def fake_requires_com(path):
        return True

    def fake_write(path, fields, *, word_session=None):
        captured["word_session"] = word_session
        return WordSection2WriteResult(changed_fields=(), unchanged_fields=())

    monkeypatch.setattr(
        "backend.infrastructure.office.word_document_gateway.application_form_requires_com",
        fake_requires_com,
    )
    monkeypatch.setattr(
        "backend.infrastructure.office.word_document_gateway.write_application_form_fields_with_com",
        fake_write,
    )

    gateway = WordDocumentGateway()
    gateway.write_application_form_fields(
        source,
        {"ltr_number": "DL-2026-05-011"},
        application_form_word_session=session,
    )

    assert captured["word_session"] is session
```

- [ ] Implement the optional parameter in `WordDocumentGateway.write_application_form_fields()`.

Signature target:

```python
def write_application_form_fields(
    self,
    source_path: Path,
    fields: dict[str, str],
    *,
    application_form_word_session: object | None = None,
) -> WordSection2WriteResult:
```

- [ ] Implement the facade-owned session helper in `OfficeFacade`.

Signature target:

```python
def write_word_application_form_fields_with_owned_session(
    self,
    source_path: Path,
    fields: dict[str, str],
) -> WordSection2WriteResult:
    with ApplicationFormWordSession() as word_session:
        return self._word_gateway.write_application_form_fields(
            source_path,
            fields,
            application_form_word_session=word_session,
        )
```

Keep the existing `write_word_application_form_fields(...)` method unchanged in behavior. It may share implementation with the new helper, but it must not start a long-lived session.

- [ ] Run:

```powershell
py -m pytest tests/unit/test_application_form_word_gateway.py -q
```

Expected: pass.

## Task 2: Build Production-Path A/B Timing Harness

**Files:**

- Prefer temporary smoke code under `tmp/` or an ad hoc local command; do not commit environment-specific sample paths.
- If a reusable test helper is needed, create it under `tests/manual/` with no hardcoded user desktop paths.

**Interfaces:**

- Consumes: existing Project Folder Application Form write-back service and the facade-owned session helper from Task 1.
- Produces: timing table with current median, candidate median, improvement %, optional required-forms observation, Word pid cleanup, and OpenAndRepair result.

Candidate measurement rule:

- Current path uses `ProjectApplicationFormWriteBackService` with the normal Office writer.
- Candidate path uses the same `ProjectApplicationFormWriteBackService` with a candidate Office writer whose `write_word_application_form_fields(...)` delegates to `OfficeFacade.write_word_application_form_fields_with_owned_session(...)`.
- The service setup, project data, target copied document, Basic Information snapshot, output-record behavior, and field payload must otherwise be equivalent.
- Do not measure only `WordDocumentGateway` and call that a production-path candidate.

- [ ] Run one current-path baseline using a copied Application Form.

Record:

```text
mode=current
total_seconds=
word_dispatch=
document_open=
field_write_and_readback=
document_close=
word_quit=
```

- [ ] Run one candidate-path baseline using the same application service path and a candidate Office writer backed by a facade-owned ConnLab session.

Record the same timing fields.

- [ ] Run interleaved A/B pairs.

Minimum result table:

```text
run,order,current_seconds,candidate_seconds,current_doc_ok,candidate_doc_ok
1,current-first,...,...,true,true
2,candidate-first,...,...,true,true
3,current-first,...,...,true,true
```

- [ ] If measuring Required Forms service graph timing, build both service graphs with identical dependencies except the Application Form Office writer mode.

Record:

```text
mode=current|required-forms
required_forms_total_seconds=
application_form_write_back_seconds=
required_forms_observation_only=true
fee_form_seconds=
customer_feedback_seconds=
test_record_seconds=
```

- [ ] Decide whether the candidate passes the evidence gate.

Decision text must be added to the TASK file before any production wiring:

```text
Evidence gate: PASSED
Reason: median Application Form write-back improved from Xs to Ys (Z%), Required Forms regression tests passed, and no equivalent Required Forms service graph timing gate was claimed.
```

or:

```text
Evidence gate: FAILED
Reason: candidate median improved by only X%, below the required 15%/2.0s threshold.
Production wiring was not changed.
```

## Task 3: Wire Project Folder Only If Evidence Passes

**Files:**

- Modify: `backend/application/project_application_form_write_back_service.py`
- Modify: `backend/infrastructure/office/office_facade.py`
- Test: `tests/unit/test_project_application_form_write_back_service.py`

**Interfaces:**

- Consumes: facade-owned Office port method from Task 1.
- Produces: Project Folder Application Form write-back uses a facade-owned ConnLab session for the scoped write-back operation only if Task 2 passes.

- [ ] If Task 2 fails, skip this task and record the skip in the TASK file.

- [ ] If Task 2 passes, add a focused session-owned write-back path.

Preferred shape inside the application service:

```python
write_result = self._office.write_word_application_form_fields_with_owned_session(
    target,
    fields,
)
```

`ProjectApplicationFormWriteBackService` must not import `ApplicationFormWordSession`. The Office port/facade owns the session lifecycle inside infrastructure. Do not create module-level or app-level global Word sessions.

- [ ] Add service test proving the Office dependency calls the session-owning Office port method when the evidence gate has approved integration.

Use a fake Office dependency; do not invoke COM.

- [ ] Run:

```powershell
py -m pytest tests/unit/test_project_application_form_write_back_service.py -q
```

Expected: pass.

## Task 4: Regression Tests

**Files:**

- Existing unit/integration tests only unless Task 3 adds a new helper.

- [ ] Run Word/session regression:

```powershell
py -m pytest tests/unit/test_application_form_word_session.py tests/unit/test_application_form_word_gateway.py tests/unit/test_project_application_form_write_back_service.py -q
```

Expected: pass.

- [ ] Run Required Forms regression:

```powershell
py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q
```

Expected: pass.

- [ ] Run diff check:

```powershell
git diff --check
```

Expected: no whitespace errors; CRLF warnings are acceptable in this repository.

## Task 5: Real Smoke And Documentation

**Files:**

- Modify: `tasks/TASK_334D_PROJECT_FOLDER_APPLICATION_FORM_WORD_SESSION_INTEGRATION.md`
- Modify: `docs/task_board.md`

- [ ] Run final focused smoke after any production wiring.

Record:

```text
project_id=
mode=
pre_word_pids=
post_word_pids=
application_form_write_back_seconds=
full_required_forms_seconds=
open_and_repair_false_result=
orphan_word_processes=
```

- [ ] Update TASK file completion notes.

Completion notes must state whether production wiring was integrated or rejected.

- [ ] Update `docs/task_board.md`.

The board must include:

- task status
- last updated date
- validation summary
- timing summary
- next stop point

## Risks

- Word COM variance can make single-run timing misleading. This is why the evidence gate requires paired interleaved runs.
- Passing an infrastructure session type into the application layer would violate layering. Keep the session hidden behind `OfficeFacade`; application service tests should assert the port method is called, not that a session object is passed.
- Any Word session cleanup bug can leave hidden `WINWORD.EXE`. The pid baseline check is mandatory.
- If only one Application Form is written per operation, reuse may not improve full Project Folder time enough to justify wiring.

## Self-Review

- Spec coverage: covers production-path evidence, optional session pass-through, conditional integration, process cleanup, and Word open validation.
- Placeholder scan: no unresolved placeholder markers.
- Boundary check: no frontend/API-contract/field-scope/header-layout changes are authorized.
- Type consistency: optional session path is named consistently as `application_form_word_session`.

## Approval Gate

Implementation is not approved yet. Wait for explicit user approval before modifying Python implementation files.
