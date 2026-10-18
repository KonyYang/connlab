# Local project leader display name

The sidebar avatar is labelled **Project Leader** and directly opens a compact, single-field editor.
Registration, usernames, passwords, remembered-login expiry and sign-out are no longer part of the
UI. This is a local default/name setting, not authentication, permissions or proof of the operator.
The existing Settings navigation item remains in the normal sidebar navigation.

The trimmed name accepts Chinese characters and spaces, is nonblank, and is at most 80 Unicode
characters. Control/invalid Unicode characters are rejected. Empty and overlong values receive clear
inline English explanations, accessible invalid/described-by states and focus on the name field;
native generic validation bubbles are disabled. One short helper explains its default-setting purpose;
field/read/save errors have a single visible alert with field-error priority. The modal preserves interaction locks and returns
focus to the stable avatar after Escape or close. Failed saves keep the previous displayed profile;
403 suggests refreshing, server failures suggest retrying later, and network guidance says
“Could not connect. Please retry.” without claiming the server was unchanged. Only recognized name-field reasons
are shown inline; raw transport details are never user guidance. Save feedback belongs to the current
form attempt and does not reappear after cancelling/reopening; shared errors describe profile reads only.

## Persistent setting, not a login

- GET/PUT `/api/local-identity/profile` return only `{profile: {display_name} | null}`.
- `Settings.data_dir/local_profile.sqlite3` is a separate singleton store. Transactions are atomic;
  owned schema version/table/columns/constraints are validated before mutation. Unsupported data is
  preserved and rejected, never migrated or silently reset.
- The profile has no cookie, token, password, session lifetime or expiry. Restarting the application
  reads the same saved name. Only a public profile is held in frontend memory.
- Requests retain loopback host/peer checks, no-store responses, bounded 4 KiB JSON bodies and exact
  same-origin/custom-header protection for PUT. This does not gate existing project APIs.
- The Vite development proxy preserves the original Host header while forwarding `/api` to the
  local backend, so browser Origin and Host still match. The backend checks are not weakened.
  Runtime regression coverage starts a real Vite proxy and owned ephemeral upstream, proving
  same-origin save/read and rejection of foreign or absent Origin; no live user profile is changed.
- The profile flow never opens, reads, migrates or deletes `local_identity.sqlite3`. Previously
  registered account/password/session records and legacy authentication endpoints remain as dormant
  compatibility; the application UI neither calls them nor implies authentication.

Back up the independent local profile file alongside local data. Preserve incompatible files and
contact support rather than deleting them. A local OS process/user with access to these files is
outside this display-setting boundary; keep the workbench loopback-only.

## Defaults and existing information

The shared profile store bootstraps once and refreshes on window focus. Generation guards prevent
late reads from overwriting newer saved names; synchronous adapter errors cannot crash page mounting.

Temperature exports use the current saved name for `Tested By`, with no duplicate input on that page.
Saving a new name updates the next download without reimporting data or recalculating charts; other
manual report fields remain intact. Already generated files and historical records are not rewritten.

For New Project, a new unassigned draft prefers the local profile; only after initial profile loading
does the previous completion-options/Windows default apply as fallback. Once assigned, refreshed
profile/options do not overwrite that draft. User edits and intentional clears win. An existing
`project_leader` key, including a blank value, takes precedence; frozen/confirmed records receive no
new default. Switching/importing a new case snapshots the then-current profile without resetting
other fields when a profile merely loads or changes. The existing completion request carries this
selected leader onward to existing LTR/form generation; no external authoritative files are mutated
by changing the profile.

Explicit leader clears are retained as a blank JSON override by the existing intake review service,
while absent keys remain absent and eligible for new defaults. Other normalization, frozen-field
rules and required-leader completion blocking are unchanged. Old records whose blank keys were
already discarded cannot reveal the prior intention and are not backfilled or migrated.

Acceptance: edit avatar name → save → restart retains it → new project/report adopts it. Existing
source/manual/blank/frozen values survive profile/options races; changing profile only affects future
defaults. Prior registered credentials remain byte-for-byte unchanged by profile operations.
