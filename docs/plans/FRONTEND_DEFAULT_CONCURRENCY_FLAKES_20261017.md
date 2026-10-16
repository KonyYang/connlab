# Default-concurrency frontend test instability

Task: `TASK_FRONTEND_DEFAULT_CONCURRENCY_FLAKES_20261017`. Tier: standard.
Baseline: `d1aec4a4585e5ca923b1452823145099686d4bc2`.

Disposition: local corrections are complete in two test files. The final complete default-worker
frontend gate passed 974 tests / 1 existing skip, then TypeScript and Vite passed sequentially.
No worker cap, timeout increase, assertion removal or product change. User Close remains pending.

## Scope and acceptance

Diagnose and minimally repair the two default-worker failures retained by the previous task.
Keep the 256-category boundary, Fee cancellation/no-generation assertions and act-warning guard.
Do not increase timeouts, reduce default concurrency, suppress warnings, skip tests, or change real
business data. Use disposable fixtures, cache and logs only. No push or publication.

Initial candidate source scope is the two affected test files. Change product code only if evidence
shows a product defect rather than a test defect. The final complete frontend gate must use normal
worker settings and run typecheck/build sequentially. Review the exact final diff before that gate.

## Original evidence and feedback loop

The retained `approved-final-frontend-986d6933.log` in
`C:\Users\White\AppData\Local\Temp\connlab-intake-qa-frontend-40b02c31` records 972 passed,
2 failed and 1 skipped in 47.52s. The failing cases are the 256-category Add-row boundary and the Fee
preview cancellation test's act-warning guard in `afterEach`; the latter's no-generation assertions
did not fail. Git confirms frontend/backend/test/script inputs at this task's baseline equal that run.

The original reproduction command is `npm.cmd test` from `frontend`, with no worker-limit environment
overrides. Current diagnostic runs use the same default settings. A temporary tagged console record
at the existing Fee warning collector was used to capture a stack if it recurred; the existing guard
was unchanged. That temporary record has been removed from the final test change.

## Measured findings before repair

### Contact measurement boundary

An instrumented cache copy separates unchanged 256-row rendering from the global role query:

- Three initial runs: rendering 103–163ms; querying 462–646ms.
- Concurrent A/B copies: the original query takes 638–1416ms. Scoping the same named button query
  to its existing semantic column header takes 313–463ms, with the same rows, role/name and disabled
  assertion. All 91 tests in that mixed probe passed; this is comparative timing evidence, not a
  claim that the original five-second timeout was reproduced in that smaller workload.
- A 14-file workload chosen from the original slowest real test files raised the original query
  to 2017–2252ms while rendering took 197–570ms. This identifies the global accessibility query as
  the principal avoidable test cost under contention.

The minimal fix is `ContactMeasurementSetupWorkspace.test.tsx`: retain all 256 rows and
the disabled assertion, but locate the Add-row button within its existing accessible column header.
No editor or model behavior needs to change for this finding.

### Fee cancellation

The mechanism isolated is an unowned asynchronous test interaction. The production click handler
awaits the preview response, then sets its confirmation and running state; the page also performs a
background folder-hint preview. Synchronous `fireEvent.click` finishes its act scope before those
updates. An instrumented cache copy confirmed that all three preview-related updates ran outside
act. Testing Library's asynchronous query temporarily sets the act-environment flag false, which
explains why a passing query alone is not evidence of act ownership.

The same probe with `await act(async () => { fireEvent.click(button); })` put those three updates
inside act. A cache-only ownership guard produced a deterministic original RED (three escaped
updates) / awaited GREEN in 1.65s. This probe inspected React development internals solely for
diagnosis; no internal inspection, line-based guard or flag manipulation enters repository tests.
The committed behavioral test still checks cancellation, no generated download, no publication and
an empty act-warning collector. Only the asynchronous click boundary changes.

The exact historical console warning was not recaptured during this investigation, so its original
callback/scheduling order is not claimed proven. Ten isolated cancellations, 50 response-delay
variants (0–25ms), an eight-file 472-test replication and the 14-file 445-test workload passed without
it. Four original-identity default-worker diagnostic runs were bounded in advance: three passed
974 tests / 1 skip in 29.47s, 27.78s and 32.12s; the fourth failed a different existing Fee case
(`does not confirm when autosave succeeds without a pricing draft id`, waiting for its error text),
with 973 passed / 1 failed / 1 skipped in 34.60s. That failure is retained and is not a passing gate or
a reproduction of the cancellation warning. The mechanism-specific ownership probe, rather than
these passing repetitions, is the evidence for the targeted asynchronous-boundary repair.

## Minimal implementation and verification

Only the two existing tests and this evidence document are changed, plus the task board:

- Contact boundary: locate the existing Add-row semantic column header, then find its named button
  within that header. Preserve real 256-row rendering, accessible role/name and disabled assertion.
- Fee cancellation: obtain the existing button and await asynchronous act around its click. Preserve
  the original dialog lookup, Cancel action, no-generation assertions and global act-warning guard.
- The newly repeated failure in the same Fee file also required a bounded test correction. Its
  original edit could begin while Confirm still reported `Waiting for saved pricing draft.` (seen
  in the readiness A/B probe), and a default 1000ms text query was racing an 800ms real debounce.
  Reuse the existing page-readiness helper, then advance the existing debounce with Vitest fake
  timers inside async act. Assert the same error text/count, enabled Confirm and no confirmation
  synchronously after that controlled transition. Existing `afterEach` restores real timers. No
  application timing or timeout is increased. Both the default diagnostic and first two-file feedback
  reproduced its original failure before this correction; the retained A/B readiness probe passed
  ten tests but showed the original pre-readiness edit, so that pass is not claimed a RED.
- No product, backend, fixture semantics, timeout, package, concurrency or build configuration changes.

Final affected feedback: **52 passed / two files**, 11.32s, with normal worker settings. The corrected
256-category case took 336ms. The first two-file run had **51 passed / one failed**, 12.37s, on the
adjacent autosave case, and is retained as RED rather than counted as passing feedback.

### Standards review

Focused review by the implementing agent in a separate pass: **0 findings**. The exact test diff
uses existing semantic queries, async act and clock utilities. All 256 rows and behavioral assertions
remain. No new dependency, shared abstraction, product edit, warning suppression or diagnostic
internal remains in repository tests. Fake timers have the existing unconditional cleanup boundary.

### Spec review

Focused same-agent review: **0 findings**. The two requested sites receive local test corrections;
the additional same-file autosave correction addresses a failure actually repeated during this task.
Source scope is still two tests plus evidence/board. Default worker configuration and default test
timeouts are unchanged. The final complete QA pass below ran on the clean reviewed commit;
diagnostic passes are not substituted for that gate. Review is not claimed independent.

## Diagnostic artifacts

All logs are under `C:\Users\White\AppData\Local\Temp\connlab-frontend-flakes-20261017`:
`baseline-probes.log`, `mixed-load-probes.log`, `fee-delayed-response-probes.log`,
`heavy-real-file-probes.log`, `fee-concurrent-repro.log`, `original-scheduling-diagnostic.log` and
`original-scheduling-replay-*.log`, `fee-act-scope-probe.log`, `fee-ownership-red-green.log` and
`targeted-fixed-tests.log`, `targeted-final-tests.log`, and `autosave-readiness-probe.log`.
Clearly marked cache-only source/config copies are under
`frontend/node_modules/.cache/connlab-default-flakes-20261017`; they are not repository tests.

## Risks and completion criteria

Do not replace a flaky pass with a diagnosis. Require a mechanism-specific reproducer or clearly
bounded evidence, retain original failures, and distinguish timing measurements from assertions.
The final review must confirm no warning suppression, timeout extension, concurrency cap or lost
behavioral assertion. Complete default-worker frontend tests plus TypeScript/Vite must pass on the
final reviewed source. Python and real business UI/data are outside this test-focused change unless
the eventual exact diff establishes a dependency requiring them.

## Final QA and local integration evidence

The same agent performed the separate Developer, focused Reviewer and QA passes; no independent
agents are claimed for this standard task. Exact reviewed implementation subject:
`2aedce4a51e3883d4538ed7d6f135397d3d0c95e`. The worktree was clean at QA start and after completion.

Command: `scripts/run_tests.ps1 -Suite Frontend`, on the original repository with dedicated Temp
CONNLAB data/database/projects/templates/logs/local/admin/release paths, LTR path empty, local-only
mode and writes disabled. `VITEST_MAX_FORKS`, `VITEST_MIN_FORKS`, `VITEST_MAX_THREADS` and
`VITEST_MIN_THREADS` were explicitly unset. The original package, runner and Vite configuration were
unchanged, and no timeout option or profiling flag was supplied.

| Final affected validation | Result |
| --- | --- |
| Targeted final two files | 52 passed, 11.32s |
| Complete default-worker Vitest | 974 passed / 1 skipped; 106 files passed / 1 skipped; 42.95s |
| Corrected 256-category case under that full load | Passed, 1910ms (original pre-fix replay reached 4180ms; the historical run exceeded 5000ms) |
| Complete Fee file under that full load | 50 passed; cancellation guard and controlled autosave error assertion passed |
| TypeScript | `tsc -b` passed after Vitest |
| Production build | Vite passed after TypeScript, 189 modules, 1.24s |
| Complete runner | Exit 0, `All requested checks passed.` |

The sole frontend skip is the existing opt-in Matrix profiling case, unchanged by this task.
No Python or browser rerun is required by this exact diff: there is no backend, product source,
configuration or integration-contract change. The full source diff from activation is exactly the
two test files, this plan and the task board. All existing assertions remain, including role/name,
256-category disablement, no file download/publication and an empty Fee act-warning collector.

The final complete log is
`C:\Users\White\AppData\Local\Temp\connlab-frontend-flakes-20261017\final-default-frontend-2aedce4a.log`,
SHA256 `9A03534E256D8D787510F270E330BA6967593903149B3FE218A549051BD212CA`.
`final-validation.json` in that same directory records the exact subject, changed paths, final test
file hashes and results. The final executable inputs were verified unchanged before recording these
facts; subsequent evidence/board-only commits do not alter the tested state. The temporary debug
tag and diagnostic React-internal probes are absent from repository tests.

The historical cancellation warning's precise interleaving remains unobserved in this run; the
confirmed repair is the demonstrated asynchronous act-ownership defect, not a claim of reproducing
that exact old warning. A single complete pass also cannot establish reliability on every possible
host load. The default-worker gate now passes with mechanism-specific fixes and the original
failure guards retained, without reducing concurrency or extending timeouts. No real business data,
project material, push, release or publication was involved.
