# TASK_334C Application Form Word COM Session Lifecycle Optimization Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:systematic-debugging` before changing lifecycle behavior and use `superpowers:executing-plans` to implement this plan task-by-task after approval.

**Goal:** Determine and safely reduce the remaining Application Form Word COM lifecycle cost after TASK_334B.

**Architecture:** Keep Office automation behind infrastructure gateways. Add lifecycle profiling first, then introduce an explicit ConnLab-owned Word session context only if measured evidence shows it is useful and safe. Preserve Application Form write-back field scope and document correctness.

**Tech Stack:** Python 3.11+, pytest, pywin32/Word COM behind infrastructure gateway classes, existing ConnLab OfficeFacade/application-service layering.

## Global Constraints

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current active lineage: `TASK_334B_APPLICATION_FORM_WORD_COM_PERFORMANCE_OPTIMIZATION` is complete; TASK_334C must be separately approved before implementation.
- Python files must stay below the project hard limit of 500 lines.
- UI/API routes must not directly call Word COM.
- No frontend, API contract, Basic Information, Fee Form, Customer Feedback, Test Record, LTR workbook, Report, StepInstance, AI, permission, LAN/server, or multi-user scope.
- Do not attach to or close a user-owned Word instance.
- Do not leave hidden Word processes or locked documents after success or failure.

---

## Current Evidence

TASK_334B final structured timing on a copied real Application Form:

- `word_dispatch`: about `2.48s`
- `document_open`: about `1.05s`
- `header_ltr_com_write`: about `0.80s`
- `target_index_build`: about `3.51s`
- `field_write_and_readback`: about `0.32s`
- `document_save`: about `0.10s`
- `document_close_quit`: about `3.33s`
- gateway total: about `11.65s`

This shows field writing itself is no longer the main cost. The remaining risk is that Word lifecycle operations are expensive, but the current Project Folder update path usually writes one Application Form document per operation. A reusable Word session must therefore be proven before it is introduced.

## Working Hypothesis

The remaining Application Form time may be dominated by Word application lifecycle rather than document content edits. Reusing a ConnLab-owned hidden Word application for a bounded operation could reduce repeated `DispatchEx` and `Quit` costs if the orchestrator has multiple Word documents or multiple write passes. If the real path has only one document, lifecycle reuse may not improve the full Project Folder update and should not be shipped as a risky global singleton.

## Files

Likely create:

- `backend/infrastructure/office/application_form_word_session.py`
  - ConnLab-owned Word session context if profiling proves it useful.
  - Explicit cleanup behavior for opened documents and owned Word app.
- `tests/unit/test_application_form_word_session.py`
  - fake COM cleanup tests.

Likely modify:

- `backend/infrastructure/office/application_form_word_gateway.py`
  - accept an optional explicit session object or lifecycle adapter if implemented.
  - keep existing standalone path as default unless service opts into session use.
- `backend/infrastructure/office/models.py`
  - extend timing stage names only if needed; do not break existing result shape.
- `tests/unit/test_application_form_word_gateway.py`
  - prove standalone path remains compatible.
- `tests/unit/test_project_application_form_write_back_service.py`
  - prove service behavior and blockers are unchanged.

Do not modify:

- `frontend/`
- `backend/api/`
- Basic Information services or schemas
- Fee Form / Customer Feedback generators
- Test Record / LTR sync services
- Report-generation modules

## Design

### 1. Baseline First

Before implementation, run a current-version focused smoke on a copied real Application Form and record:

- standalone gateway total time
- `word_dispatch`
- `document_open`
- `target_index_build`
- `field_write_and_readback`
- `document_save`
- `document_close`
- `word_quit`

If current timing snapshot only has combined `document_close_quit`, split the timing collector so close and quit can be observed separately before making optimization choices.

### 2. Compare Candidate Lifecycle Shapes

Run a focused smoke against copied documents:

- Shape A: current standalone path: `DispatchEx` -> `Open` -> write -> `Save` -> `Close` -> `Quit`.
- Shape B: one ConnLab-owned hidden Word app, one document: `DispatchEx` -> `Open` -> write -> `Save` -> `Close` -> `Quit`.
- Shape C: one ConnLab-owned hidden Word app, two sequential copied documents: `DispatchEx` once -> `Open/Close` doc 1 -> `Open/Close` doc 2 -> `Quit`.

Shape B is expected to match current behavior unless the abstraction reduces overhead. Shape C answers whether session reuse is valuable for future multi-document or retry paths.

The candidate only qualifies as materially faster when the focused smoke runs at least three repetitions per comparable shape in the same run and shows:

- single-document candidate median does not regress versus the standalone baseline median
- reuse candidate median improves the applicable baseline by at least `15%` or `2.0s`, whichever is easier to satisfy
- the conclusion uses medians, not the single fastest run

### 3. Introduce A Bounded Session Only If Evidence Supports It

If profiling supports implementation, create an explicit session abstraction:

```python
class ApplicationFormWordSession:
    def __enter__(self) -> "ApplicationFormWordSession": ...
    def __exit__(self, exc_type, exc, tb) -> None: ...
    def open_document(self, path: Path) -> object: ...
    def close_document(self, document: object, *, save: bool) -> None: ...
```

Rules:

- The session owns only the Word application it creates through `DispatchEx`.
- It sets the same hidden/no-alert behavior as the current gateway.
- It tracks documents opened through the session.
- It closes tracked documents before quitting the Word application.
- It never calls `GetObject` or attaches to existing visible Word.
- It can be used by tests with fake Word objects.

### 4. Keep Existing Gateway Default

The current public gateway function should continue to work without a caller-provided session.

If optional session support is implemented:

- standalone calls create and clean up their own session internally
- caller-provided session calls do not quit the session
- caller-provided session calls still close each opened document after the write
- exceptions close the current document and propagate the existing business error behavior

### 5. Preserve Correctness Before Performance Claims

Any optimized path must still preserve:

- canonical write-back fields only:
  - `ltr_number`
  - `lab`
  - `project_leader`
  - `received_date`
  - `estimated_completion_date`
  - `sample_condition`
- header LTR normalized layout
- visible read-back verification
- critical blocker semantics
- normal Word open with no recovery prompt

If a faster session path fails recovery/open validation, reject the path.

## Tasks

### Task 1: Split Close/Quit Timing

**Files:**

- Modify: `backend/infrastructure/office/application_form_word_gateway.py`
- Modify: `tests/unit/test_application_form_word_gateway.py`

**Interfaces:**

- Consumes existing `OfficeTimingSnapshot` / `OfficeTimingStage`.
- Produces separate timing stages: `document_close` and `word_quit`.

Steps:

- [ ] Add failing unit coverage that expects `document_close` and `word_quit` timing stage names when the fake COM path closes normally.
- [ ] Split the current combined close/quit timing in the gateway.
- [ ] Run:

```powershell
py -m pytest tests/unit/test_application_form_word_gateway.py -q
```

Expected: tests pass and existing `document_close_quit` compatibility is either preserved as a total stage or replaced only if no tests/API depend on the old name.

### Task 2: Add ConnLab-Owned Session Fake Tests

**Files:**

- Create: `tests/unit/test_application_form_word_session.py`
- Create: `backend/infrastructure/office/application_form_word_session.py`

**Interfaces:**

- Produces `ApplicationFormWordSession`.
- Produces cleanup behavior for gateway optional session use.

Steps:

- [ ] Write fake COM tests for success cleanup:

```python
def test_session_closes_open_documents_and_quits_owned_word_on_exit():
    ...
```

- [ ] Write fake COM tests for exception cleanup:

```python
def test_session_closes_documents_and_quits_owned_word_on_exception():
    ...
```

- [ ] Implement the minimal session context around injected fake dispatch factory.
- [ ] Run:

```powershell
py -m pytest tests/unit/test_application_form_word_session.py -q
```

Expected: cleanup tests pass.

### Task 3: Wire Optional Session Into Gateway

**Files:**

- Modify: `backend/infrastructure/office/application_form_word_gateway.py`
- Modify: `tests/unit/test_application_form_word_gateway.py`

**Interfaces:**

- Consumes optional `ApplicationFormWordSession`.
- Produces unchanged standalone gateway behavior.

Steps:

- [ ] Add fake test proving standalone gateway still creates and quits an owned session.
- [ ] Add fake test proving caller-provided session is not quit by the gateway.
- [ ] Update the gateway to use the optional session for Word app/document lifecycle.
- [ ] Run:

```powershell
py -m pytest tests/unit/test_application_form_word_session.py tests/unit/test_application_form_word_gateway.py -q
```

Expected: tests pass, with no behavior change for standalone callers.

### Task 4: Focused Real Lifecycle Smoke

**Files:**

- No production file changes required.
- Use a temporary smoke script or focused `py -c` command under `tmp/`.

**Interfaces:**

- Consumes copied real Application Form documents.
- Produces timing evidence and open/recovery evidence.

Steps:

- [ ] Copy the same real Application Form into two or three `tmp\task_334c_*` files.
- [ ] Record pre-run `WINWORD.EXE` process ids.
- [ ] Run standalone gateway write-back against copy A and record timing.
- [ ] Run optional-session gateway write-back against copy B and record timing.
- [ ] If supported, run two sequential writes in one session against copy B/C and record timing.
- [ ] Reopen final output in Word with `OpenAndRepair=False`.
- [ ] Record post-run `WINWORD.EXE` process ids.
- [ ] Check that all newly-created ConnLab-owned Word process ids are gone, without killing or treating user pre-existing Word processes as failures.

Expected:

- The smoke identifies whether session reuse materially improves the measured path.
- The document opens normally without recovery prompts.
- Word process cleanup is proven by comparing pre-run and post-run process-id sets.

### Task 5: Decide And Document Outcome

**Files:**

- Modify: `tasks/TASK_334C_APPLICATION_FORM_WORD_COM_SESSION_LIFECYCLE_OPTIMIZATION.md`
- Modify: `docs/task_board.md`

**Interfaces:**

- Produces completion notes and validation summary.

Steps:

- [ ] If session reuse is faster and safe, mark TASK_334C complete with measured improvement and explain where the optimized path is used.
- [ ] If session reuse is not faster or not safe, mark TASK_334C complete as profiled/rejected and do not ship risky lifecycle reuse beyond safe instrumentation.
- [ ] Record real timing medians, open/recovery smoke, process-id cleanup result, and test results in task files/board.

Expected:

- The task closes with evidence, not assumption.
- No follow-up implementation is implied unless separately approved.

## Test Plan

Primary unit tests:

```powershell
py -m pytest tests/unit/test_application_form_word_session.py tests/unit/test_application_form_word_gateway.py tests/unit/test_project_application_form_write_back_service.py -q
```

Required regression tests:

```powershell
py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q
```

Real smoke:

```powershell
# exact command to be added during implementation because it depends on the copied smoke fixture path
```

## Risks

- A persistent hidden Word session can leak `WINWORD.EXE` if cleanup is incomplete.
- Word modal dialogs can hang hidden automation; the implementation must keep DisplayAlerts disabled and avoid recovery-prone outputs.
- Attaching to a user-owned Word instance risks closing or modifying user documents; this task forbids that.
- COM threading behavior can vary; this task does not introduce background cross-thread Word automation.
- If the Project Folder operation only writes one Word document, session reuse may not reduce the user-visible runtime.

## Self-Review

- Spec coverage: the plan covers lifecycle timing, optional session abstraction, cleanup, real smoke, no-orphan check, and explicit reject-if-not-useful behavior.
- Placeholder scan: no implementation placeholder remains; the only smoke command is intentionally deferred because it depends on the implementation-created temporary fixture path.
- Type consistency: `ApplicationFormWordSession` is the single proposed session abstraction name across task and plan.
