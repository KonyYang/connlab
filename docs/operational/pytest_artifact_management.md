# Managed pytest artifacts

## Scope and storage

The original unreviewed proposal is retained at `a3999f4f`; do not cherry-pick its generic
`tmp` sweep. This replacement manages only disposable pytest fixture output. It does not
adopt, enumerate recursively, or clean existing `connlab/tmp`, `%TEMP%`, worktrees,
acceptance evidence, databases, business files, or interrupted business-write recovery data.

On Windows the default is `D:\ConnLabTestArtifacts\pytest`, regardless of checkout drive
or current working directory. Set `CONNLAB_PYTEST_ARTIFACT_ROOT` to an explicit absolute
local directory to use an isolated CI/test store. There is no silent fallback to C: when
D: is absent or unwritable; pytest fails with the storage path and reason instead.

An explicit pytest `--basetemp` takes precedence, including one supplied through pytest's
existing argument configuration. Such a run neither initializes nor sweeps managed storage.
Its output and pytest's own clearing semantics remain the caller's responsibility. The
packaging scripts' existing explicit basetemp values are unchanged.

## Lifecycle and deletion boundary

The root must be new/empty or already contain a valid `.connlab-pytest-root.json` ownership
record. Existing nonempty unmarked directories are refused, not automatically enrolled.
Each session gets a UUID-named `run-*` container and its own `scratch` basetemp. There is
no shared basetemp for concurrent pytest processes to erase.

The session holds an OS file lease until pytest configuration teardown completes, after
fixtures/session cleanup. A durable `.finished.json` record declares successful teardown
of the manager, including normal sessions whose tests failed. Abrupt termination does
not create that record: those runs remain for manual investigation, even after the OS
releases the lease. PID reuse and an old mtime never prove that a run is finished.

Before each default pytest session, retention considers only runs that:

- Have matching root/run/completion identities and no unexpected files beside `scratch`.
- Have a valid completion time older than seven days and no newer tree modification.
- Have no active lease, unreadable entry, unsafe ancestor, special file, or junction.
- Still have the same directory identity, ownership and contents at the pre-delete check.

Root/ancestor links and reparse points are refused. Wholly internal symlinks (such as
pytest's `*-current`) can be unlinked without traversal; escaping, cyclic or broken
links preserve the run. Windows junctions always preserve the run. Cleaners serialize
on a root maintenance lease. They delete scratch payload before ownership records,
so a locked payload leaves its records intact for a later safe retry.

Only these generated `scratch` payloads and then their known management files are deleted.
Unknown root entries are untouched. The seven-day rule does not apply to generic `tmp`
directories or files merely because their names resemble QA output.

Cleanup failures are printed to stderr and do not fail tests or the cleaner. A failure to
initialize a new session's storage is a setup error; continuing in an unintended location
would hide the disk-growth problem. A completion-record failure releases the lease but
retains the run as unfinished, with a diagnostic.

## Commands and compatibility

Existing `scripts/run_tests.ps1` continues to invoke pytest normally. The root conftest
applies the same policy to that runner and direct pytest; no second runner-specific
deletion command is needed.

```powershell
# Preview only; default invocation never deletes.
& 'C:\PythonEnvs\connlab\.venv\Scripts\python.exe' scripts/clean_tmp.py --dry-run

# Explicitly apply the policy to already managed disposable test runs only.
& 'C:\PythonEnvs\connlab\.venv\Scripts\python.exe' scripts/clean_tmp.py --delete

# A private test store; does not enroll an existing generic tmp directory.
$env:CONNLAB_PYTEST_ARTIFACT_ROOT = 'D:\MyIsolatedTestStore\pytest'
& 'C:\PythonEnvs\connlab\.venv\Scripts\python.exe' -m pytest tests/unit/test_logging.py
```

`--root` selects a marked store; `--tmp-dir` is a safe alias, not permission to sweep
arbitrary directories. `--retention-days` accepts a finite value of at least one day
(default seven); automatic pytest retention always uses seven. `--quiet` keeps warnings
visible. Invalid CLI arguments fail normally; ordinary cleanup failures return zero.
The script uses no new dependencies and performs no application/Office/database startup.

## Verification and remaining limits

The public test seams are managed-run start/finish/cleanup, real pytest child sessions,
and the cleaner CLI. Acceptance uses only newly created isolated directories, including
real two-process pytest execution, Windows lease/junction/open-file checks, metadata
corruption, preview/apply separation, failure/retry, and explicit-basetemp compatibility.

Historical storage is deliberately not migrated. A separate read-only inventory and User
approval are required before deleting any legacy output. Aborted sessions and unreadable,
modified or linked runs can accumulate until reviewed; the manager favors retention over
guessing. Evidence that must outlive the disposable retention window belongs outside the
managed root. This is a cooperative local test store, not a defense against an adversarial
process rewriting filesystem objects during deletion.
