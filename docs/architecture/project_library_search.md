# Project library: stage 1

Approved baseline: find project material, receive managed copies, and use reference
files safely. Stage 1 implements only discovery and access through `/reference`.

- Projects remains the execution workspace. Existing project and legacy registrations remain intact. Historical import/recovery
  implementations remain compatibility code only; ordinary library navigation does not
  enter them or call portable-data APIs. No registration migration or file relocation.
- Read-only catalog combines existing registry summaries, explicit member/project
  associations, workspace/folder records and legacy links. Same numbers do not merge
  identities. Equivalent Windows paths for an explicitly associated member are not
  listed twice; separate historical copies remain separate.
- Search combines number, product/sample description, recorded test item and file
  name. All query words must match; no document contents are read or indexed.
  Unrecorded legacy metadata is not inferred. Categories are filename suggestions.
- Queries inspect filesystem metadata on demand. Refresh sees external file changes.
  Each location has a 20,000-entry and 40-level traversal bound. Incomplete scans
  and unavailable locations are reported; the registration is retained.
- File access resolves a stable catalog identity plus relative path on the server.
  Paths are revalidated, redirected paths/traversal/ADS rejected. Only document and
  image types are opened directly; other files remain accessible through folders.
  Tests inject launchers and use isolated SQLite databases and temporary folders.

Stage 2: explicit receipt confirmation, independent reception root, duplicates,
supplementary conflict storage and editable received-project metadata.
Stage 3: explicit copy to a selected current project and lightweight report markers.
Full-text search, snapshot restoration expansion, synchronization and automatic
backup are excluded. Direct Office saves edit the selected existing file; stage 1
does not create historical versions or copy reference files to execution projects.

Acceptance: search by each supported field and combined terms; browse deep files;
filter by source/type; open document/containing folder; refresh after rename/delete;
retain missing locations with navigation to existing location controls; preserve all
files and project data; retain existing project identities and verify that ordinary navigation has no recovery links.

The current library workspace uses top search/receive controls, a project list and a
selected-project folder browser. Narrow windows stack these panes. Browser contents
come from actual directory entries; no file classification moves or renames materials.
Selected-file copy requires an explicit native project and target directory, a current
conflict preview, and confirmation. It shares receipt publication protections and
never updates Matrix, lifecycle, workspace bindings or portable snapshots.
