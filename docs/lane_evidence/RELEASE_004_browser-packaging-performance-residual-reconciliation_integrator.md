# RELEASE_004 Integrator Evidence - Browser Packaging Performance Residual Reconciliation

**Date:** 2026-07-22
**Role:** Integrator
**Lane:** `release-004-browser-packaging-performance-residual-reconciliation`
**Status:** `integrator_accepted`

## Accepted Package

- `packaging/connlab_browser_server.spec`
- `scripts/build_windows_browser_release.ps1`
- `tests/unit/test_desktop_release_scripts.py`
- `docs/release_004_browser_release_packaging_performance_plan.md`
- RELEASE_004 task, plans, Planner/Developer/Reviewer/QA/reconciliation evidence, this
  Integrator evidence, and an exact board closeout hunk.

The package uses the native `collect_submodules` filter with exact subtree matching,
retains `backend.desktop.packaged_server`, keeps the four desktop-runtime excludes, and
adds primary-error-safe Stopwatch reporting. It contains no frontend/product/API/schema
or external-lane paths.

## Validation

- `py -m pytest tests\unit\test_desktop_release_scripts.py -q`: **8 passed**.
- Python compilation of the spec and static test: passed.
- PowerShell `Parser.ParseFile` for the build script: passed.
- Staged whitelist, forbidden-scope, diff, trailing-whitespace, and line-count checks:
  passed.

No release script, real release build, PyInstaller packaging, release-folder smoke,
generated-output probe, HTTP smoke, or `dist_release/**` access occurred. These remain
a separately user-approved future validation gate. Remote push was intentionally not
performed.

## Decision

**Integrator gate: accepted.** The lane is complete/accepted as a static packaging
contract only; it makes no runtime, artifact-shape, package-size, or performance claim.
