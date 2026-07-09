# ConnLab Operator Startup

## How To Start

1. Copy the whole folder to your computer.
2. Open the copied folder.
3. Double-click `ConnLab.exe`.

You may also see a versioned file such as `ConnLab_20260630_v0.1.0.exe`. That file is the same application with a release name that helps support confirm which version you are using.

## Important Data Rule

ConnLab keeps your local database, logs, project files, and path settings under:

```text
%LOCALAPPDATA%\ConnLab
```

Do not delete this folder unless support explicitly tells you to do so. Installing or copying a newer ConnLab release folder should not remove your existing settings or work data.

## First Run

On first run, ConnLab creates its local data folders automatically. External business paths such as LTR workbook, public drive folders, and official templates may still show as not configured until they are set in ConnLab Settings.

## Moving To A New Version

1. Close ConnLab.
2. Copy the new ConnLab release folder to the computer.
3. Start `ConnLab.exe` from the new folder.

Your existing local settings remain under `%LOCALAPPDATA%\ConnLab`.
