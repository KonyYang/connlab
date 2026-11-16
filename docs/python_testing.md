# Python test storage and native picker boundaries

Run `scripts/run_tests.ps1 -Suite Python` with the existing ConnLab Python 3.11 environment.
The gate excludes tests marked `office_integration`; it does not open business data or Office.
On Windows, `$env:PYTHONUTF8 = "1"` keeps Python parent/child log encoding consistent;
setting only `PYTHONIOENCODING` can leave child-output readers using the locale encoding.

## Ordinary artifacts and path-budget fixtures

Ordinary `tmp_path` storage remains a unique managed run under
`CONNLAB_PYTEST_ARTIFACT_ROOT` (default `D:/ConnLabTestArtifacts/pytest`). Long worktree/evidence
prefixes can consume the path budget before a test exercises the intended Windows boundary.

`portable_tmp_path` supplies compact, independent per-test directories for official-workspace
backup, relocation and generation recovery tests, and for isolated Git lifecycle tests whose
internal worktree/object-store paths also have Windows limits. Those modules locally bind `tmp_path`
to this fixture. Their business folder/file names and the production 248/260-character guards are unchanged;
the deliberate too-long-path rejection tests still execute the real guard.

The compact store defaults to `D:/ConnLabTestArtifacts/p` on Windows (a local temporary store on
other platforms). `CONNLAB_PYTEST_PORTABLE_ROOT` may select another **short, absolute local**
artifact root. It must be empty or already owned by the existing ConnLab artifact marker; a
business directory, drive root or reparse point is not accepted. Tests do not silently adopt it.
Each run reuses the existing UUID ownership markers, OS lease and completion record. Existing
seven-day retention rules apply only to verified disposable scratch; logs and acceptance evidence
belong outside managed run payloads. Interrupted/unverified runs remain retained.

An explicit `--basetemp` is caller-owned and remains authoritative for **both** fixtures. Neither
managed store is initialized or swept in that mode. A caller who deliberately provides an overlong
base can still trigger a production path guard; use a short, new, dedicated path for such runs.

## Folder picker tests

The Windows path-picker integration test replaces the current public
`windows_project_folder_dialog.pick_project_folder` boundary for both selection and cancellation.
Legacy `SHBrowseForFolder` and Tk dialogs are explicitly forbidden in that test. The native adapter
unit tests separately cover COM/resource release, quiet cancellation and native failure. Automated
Python runs therefore do not wait for an actual folder selection.

## Validation and residual boundaries

Relevant regression protection covers a long ordinary evidence root, independent compact scratch,
Unicode filenames, per-test isolation, session completion, explicit caller storage, and the real
workspace backup/relocation/recovery cases that previously failed, plus local-only Git workflow
fixtures. Test bare origins contain only synthetic test commits; no real project remote is used.
Artifact ownership, concurrent
leases and retention continue through their existing tests. Validation uses isolated directories and
SQLite only. The change is test infrastructure; it does not extend supported production path lengths,
shorten business names, alter directory permissions or migrate/clean business files.
