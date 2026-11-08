# P3 development storage maintenance — 2026-11-08

## Scope and safeguards

User authorized the reviewed P3 cleanup, not business-data deletion. No product code, real report,
template, public workbook or runtime interpreter changes. No push or automatic task Close.
Independent planning precedes destructive operations; review, QA and integration verify actual results.

At preflight, current master no longer tracked release outputs, but six older worktrees each tracked 25,798
`dist_release` files. This is historical checkout materialization as well as possible build output;
the earlier 2.5 GB/day projection is not an established long-term growth rate.

Preserve all non-cache orphan-copy files and nontracked worktree files (SQLite, configuration,
journals and QA outputs) outside every deletion root. Preserve branches, including the two commits
that `git cherry` identifies as patch-equivalent to master. Archives use raw SHA-256 content entries
and per-source path manifests; verify CRC and every content digest before removing a source.
Only dependency/test caches are excluded. Directory links are recorded, never traversed.

The mechanical-folder-summary checkout is deferred: a log changed between inventory and archival.
The recently reused import-folder-picker checkout and this maintenance checkout are also retained.
Conda environments are inspect-only: LLaMA_Factory_Experience, ConnectorTestDocGen and TestFee all
remain registered as PyCharm interpreters. Registration is not proof of active use, but absence of
a matching project folder is not proof of disposability.

## Durable evidence and acceptance

Operational evidence and recoverable files live at
`D:\PythonProject\connlab\retained_archives\p3_20261108`, outside `tmp` and the removal roots.
The temporary one-off inventory/preservation script is not a product subsystem or scheduled cleaner.

Before each removal, verify exact absolute roots, branch/HEAD and task ownership, current files versus
the preserved manifest, no nested Git repository and no unexpected reparse point. Remove directory
links without recursion, then use ordinary Git worktree removal or exact orphan-root deletion.
Do not force a failed removal or bypass a deletion safeguard. Keep all unresolved paths.

For LLCR_Extractor/TestFlowManager, preserve refs and worktree state, check object integrity,
repack without expiring unreachable history and prune only packed duplicate loose objects after
successful validation. Do not run default reflog expiry, `prune=now` or `--aggressive`.

Acceptance: archive recoverability, unchanged business-code tree and branches, coherent worktree
registration, unchanged old-repository refs/worktree, healthy Git objects and measured storage change.
No frontend/backend full test matrix is warranted for documentation and development-copy maintenance.

## Execution outcome (November 8–9)

All 12 selected roots were removed; all branch refs were retained. Six additional worktrees were
reclaimed: `folder-partial-generation`, `ltr-save-mode`, `ltr-save-review`, `materials-tools-resume`,
`materials-tools-worktree`, and `temporary-formal-worktree`. All six old non-Git children of
`D:\PythonProject\connlab-worktrees` were archived and removed. Their exact paths, branch/HEAD facts,
per-file mappings, fresh source-hash gates and removal outcomes remain in the local evidence directory.
The removed roots contained about 5.45 GB logical file bytes on C and 16.37 GB on D, excluding linked
dependency targets. Compared with the initial free-space observation, net available space increased
approximately 4.8 GiB on C and 15.3 GiB on D (about 20 GiB total), including archive cost/background activity.

The 12-source archive is `preserved_files_safe.zip`, 452,278,514 bytes, with 7,311 deduplicated content
objects. Every stored content SHA-256 and CRC passed; each source path set and raw file bytes were
verified again immediately before removal. Dependency/test caches were not archived; tracked worktree
source remains recoverable from retained branches. No link target was traversed or deleted. Primary
`frontend/node_modules` retained its 110 immediate entries; live backend health was `ok` and the existing
frontend at `http://localhost:5173/` returned 200. Its existing IPv6 loopback binding rejected an IPv4-only
probe; no server host setting was changed.

Git's first worktree removal encountered Windows' filename-length limit after it had already removed
the registration and `.git` file. Execution stopped. A separate recovery audit proved the remaining
3,029 files (224,546,755 bytes) matched the archive, with no links or nested Git and an unchanged branch.
Only then was that exact residual directory removed with ordinary literal-path PowerShell removal.
Subsequent untouched worktrees used `git -c core.longpaths=true worktree remove`, without force.
This was inspected partial-state recovery, not replay of a completed transition. The incomplete first
archive was discarded after the safe archive and retained mechanical source were confirmed.

LLCR_Extractor retained all 301 unique OID/type/size records, including unreachable objects. They are
now packed, but total storage remains about 1.53 GiB: the predicted 100–300 MB result was not supported.
Existing packs were kept. TestFlowManager changed from 258.13 MiB loose plus 38.85 KiB packed to
965.35 KiB loose plus 123.27 MiB packed, roughly 134 MiB reclaimed. Full object checks passed before and
after; refs, HEAD, reflogs and working-tree state were preserved. No unreachable history was expired.

Retained checkouts are `import-folder-picker` (recent reuse), `mechanical-folder-summary` (observed
log change) and `report-tools-bridge` (this maintenance task). No active development service was stopped.
All Conda environments remain unchanged. Existing primary `tmp` evidence/recovery directories were
not blanket-purged. Old chats may still mention reclaimed paths; recreate a checkout from its retained
branch and restore local files if needed, rather than assuming those old directories still exist.

## Recovery and validation

Each `*.manifest.json` records the original path, retained branch where applicable, and each file's
`zip_entry`/SHA-256. `restore_preserved_copy.py <manifest.json> <new-directory>` restores a chosen copy
only into a directory that does not yet exist; it verifies every restored byte and does not recreate
directory links or caches. For worktrees it restores local files, not tracked source: reconstruct the
tracked checkout from the retained branch separately. Manifests, restore helper, operation scripts
and the verified archive must be retained together outside disposable `tmp`.

Independent QA verified ZIP identity, all 12 manifest structures/coverage, 56 representative content
hashes, and an isolated three-file restoration. Restored SQLite `integrity_check` returned `ok`.
Final QA checks removed roots, worktree registration, branch retention, shared dependencies and exact
three-document scope. Local evidence includes `archive_verification.json`, `deletion_gates.json`,
`removal_outcomes.json`, `removal_final_checks.json`, `qa_result.json`, repository integrity receipts
and `live_readonly_smoke.json`. No business-code, database schema or interpreter changes were made;
therefore a full application test/build matrix is not represented as run or required here.

Await user acceptance/Close after local integration. No push and no automatic task Close.
