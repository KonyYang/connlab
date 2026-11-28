# Portable browser storage acceptance

Validated the independent branch `codex/portable-release-storage-20261128` on Windows.
Runtime implementation through `113aa28c`. All launches used dedicated test profiles,
SQLite databases, test folders, loopback ports and isolated drive mappings.

| Scenario | Observed result |
| --- | --- |
| New installation | The packaged server started on Q: and created Projects, Library, TemporaryProjects and Template below Q:\ConnLabFiles. Hashes matched for all six seed templates. All three header XML parts in FDQF-E-036 matched the approved original. The project layout included its empty subfolders. |
| Public folder | In Edge, Settings exposed only the public project folder as an editable directory. Saving a test path and reopening Settings retained it. Workbook settings remained available. |
| File reception | Real preview and confirm requests placed the incoming copy in the expected library for both a new and an upgraded installation. The source remained intact. |
| Upgrade | An older executable registered four distinct test locations. The new executable on a different drive opened the same instance and reused all four registrations. Eight site file hashes matched before and after. One renamed record and one edited workbook were retained, two fee candidates were both listed and three missing purposes were filled. |
| Offline and restored | Moving the registered template folder produced a visible warning containing its registered path. No replacement directory appeared. Restoring the folder cleared the offline warning. |
| First launch retry | A file blocked the new drive's business root. Startup reported the affected path and preserved the file. After the test obstruction was removed, retry created the four folders and the six expected templates. |
| Distribution layout | A separate isolated test of the build script's final assembly produced a versioned ZIP containing ConnLab/Start_ConnLab.bat and the six-template seed archive. The assembly-only test used a placeholder executable. Real executable and browser runs used the production PyInstaller spec and Python 3.13. |

The first exploratory freeze used a different Python version from the previous release.
Final upgrade verification used the matching Python version and checked the database instance identifier.

Retained local acceptance evidence in this checkout:

- `tmp/browser-storage-acceptance/final/` contains the final Edge screenshots, runtime responses, template and sentinel checks and retry logs.
- `tmp/browser-storage-acceptance/final-sources.json` records the frozen input fingerprints.
- `tmp/package-layout-only-5927ce167d1e4449b0554c6f9b335113/evidence.json` records the separate packaging check.

Related startup, registration, receipt and runtime-binding tests passed (77 passed, two existing Windows symlink permission skips). The Windows junction sentinel test executed successfully. Template discovery, preservation, concurrency, explicit overrides and Office owner-file handling were also exercised. Frontend Settings and runtime tests passed (28), as did the production frontend build.
