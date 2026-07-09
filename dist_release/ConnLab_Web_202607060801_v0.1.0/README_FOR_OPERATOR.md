# ConnLab Browser Release Startup

## How To Start

1. Copy the whole folder to your computer.
2. Open the copied folder.
3. Double-click `Start_ConnLab.bat`.

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
3. Set and save `LTR workbook password`.
4. Restart ConnLab if it was already open while these settings were changed.

These values are saved under `%LOCALAPPDATA%\ConnLab\config` and are kept when a newer ConnLab release folder is copied to the computer.

## Moving To A New Version

1. Close the ConnLab server window.
2. Copy the new ConnLab release folder to the computer.
3. Start `Start_ConnLab.bat` from the new folder.

Your existing local settings remain under `%LOCALAPPDATA%\ConnLab`.
