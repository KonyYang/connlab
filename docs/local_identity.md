# Offline local identity

The sidebar supports local registration, sign-in, switching and sign-out. Registration signs in
immediately. Remember login is checked by default: it expires after 30 days; unchecked login uses
a browser-session cookie and expires on the server after 8 hours. Reopening retains remembered
login until expiry or explicit sign-out. Switching revokes the session before opening sign-in;
it does not navigate or reload project/data pages.

Usernames are case-insensitive, 3–64 ASCII letters/digits/dot/underscore/hyphen. Display names are
1–80 printable characters; passwords are 10–128 characters and are not trimmed. Password confirmation
is client-side. No cloud, email verification, password recovery, RBAC or global business API gating
is introduced. Anonymous `Lab User` remains available, distinctly not authenticated. Existing project
actor literals outside the shared helper are not migrated. Editable report names are not audit proofs.

## Security and recovery boundary

- `Settings.data_dir/local_identity.sqlite3` is separate from the project database. Initialization
  verifies owned schema version, tables, columns and core constraints before writing. Incompatible
  data is rejected, never migrated/deleted. Preserve the database and contact support.
- PBKDF2-HMAC-SHA256 uses 600,000 iterations with independent random 16-byte salts. Passwords are not
  persisted plaintext; comparisons are constant-time with a dummy hash for unknown users.
- Random 256-bit opaque sessions persist only SHA-256 digests and server expiries. Register/login
  revokes the presented session; sign-out revokes it. No secrets are placed in browser storage,
  response JSON or request logs. Public profile state is in-memory only.
- Cookie is host-only, HttpOnly, SameSite=Strict, path `/api/local-identity`, Secure under HTTPS.
  GET session is no-store and never changes cookies: a stale read cannot erase a newer login.
- Mutations require loopback host and peer, exact same Origin, JSON and `X-ConnLab-Identity: 1`.
  Bodies over 4 KiB and invalid fields fail without echoing passwords.
- Persistent atomic reservations precede hashing: 5 attempts/username/15 minutes, 40 globally/minute.
  Success clears the user's window, not the global budget. Expired attempt windows are cleaned;
  expired sessions are cleaned during new authentication.

This is not protection against an OS user or malicious process with access to the same local data.
Keep the app loopback-only; do not expose its business API on LAN. No destructive account reset
shortcut exists. Back up the identity database independently of public-drive project authority.

## Defaults and acceptance

Session bootstraps from the sidebar and refreshes on window focus. Generation guards prevent old
reads restoring a signed-out profile; failed sign-out retains the identity and displays the error.
New temperature imports snapshot the current display name. Late initial loading may fill an unassigned
default; switching accounts never rewrites existing testers, confirmed reports, historical records,
or manual overrides (including intentional blanks). Basic-information future confirmations use the
dynamic shared helper.

Acceptance: register → auto sign-in → refresh/reopen remembered login → switch/logout. Invalid/foreign
requests, revoked/replayed/expired sessions and throttling fail safely; existing report values remain.
