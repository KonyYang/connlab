# ConnLab Browser Release Startup

## How To Start

1. Copy the whole folder to your computer.
2. Open the copied folder.
3. Double-click `Start_ConnLab.bat`.

If ConnLab reports that its local address is already in use, another ConnLab
server (often an older version) is still running. Close that server's console
window, then run `Start_ConnLab.bat` again. The launcher will not stop another
process or open a browser tab to that existing server.

ConnLab starts a local server on your computer and opens:

```text
http://127.0.0.1:8765/
```

If the browser does not open automatically, type that address into Microsoft Edge.

## Important Data Rule

ConnLab keeps your local database, logs, project files, and path settings under:

```text
%LOCALAPPDATA%\ConnLab
```

Do not delete this folder unless support explicitly tells you to do so. Installing or copying a newer ConnLab release folder should not remove your existing settings or work data.

## First Run

On first run, ConnLab creates its local data folders automatically. External business paths such as LTR workbook, public drive folders, and official templates may still show as not configured until they are set in ConnLab Settings.

Before applying LTR numbers on a new computer:

1. Open ConnLab Settings.
2. Set and save `LTR registration workbook`.
3. Ask the deployment administrator to provision `%PROGRAMDATA%\ConnLab\config\connlab.admin.toml` from the release's secret-free `config\connlab.admin.example.toml`.
4. Restart ConnLab if it was already open while these settings were changed.

Ordinary path settings remain under `%LOCALAPPDATA%\ConnLab\config`. The administrator password file remains outside the replaceable release folder and is not managed in ConnLab Settings.

For a one-time upgrade from a version that stored the password in `connlab.local.toml`, the administrator must copy the value manually to the administrator file. ConnLab does not migrate or remove the old key. A future managed deployment may select the same file contract with `CONNLAB_ADMIN_CONFIG_PATH`.

## Moving To A New Version

1. Close the ConnLab server window.
2. Copy the new ConnLab release folder to the computer.
3. Start `Start_ConnLab.bat` from the new folder.

Your existing local settings remain under `%LOCALAPPDATA%\ConnLab`.

## Reporting A Problem

1. Leave ConnLab running after the problem occurs, if practical.
2. Open **Settings**.
3. Under **Support diagnostics**, select **Export diagnostic package**.
4. Send the downloaded `ConnLab_Diagnostics_*.zip` file to support together with a short description of what you clicked.

Fee Form publication and Project Folder failures now show a **Stage** and **Diagnostic ID**.
Include that ID or a screenshot with the ZIP. Export soon after the failure, before logs rotate.
Windows error 32 indicates a sharing violation; access denied (5) alone does not prove an open file.
Do not delete project folders, recovery journals, or your local database to bypass an error.

The diagnostics include bounded stage timings, original Windows/Office error codes and safe stack
frames, plus the release identity. Full paths, request/form contents, and passwords are not intentionally
recorded by operation diagnostics. A folder or file permission problem is reported, never automatically
repaired by changing permissions or terminating an operator's Office process.

The package contains recent application logs and release identification only. It excludes project files, the local database, and ConnLab settings files. Local file paths and common secret assignments are redacted during export.
