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

The LTR workbook password is administrator-managed and is not available in ConnLab Settings. The release includes only the secret-free template `config\connlab.admin.example.toml`. Before LTR workbook operations, the deployment administrator must copy it outside the release folder to `%PROGRAMDATA%\ConnLab\config\connlab.admin.toml`, enter the deployment value, and apply the organization's file-permission policy. ConnLab never creates or overwrites that file.

For a one-time upgrade from a version that stored the password in `connlab.local.toml`, the administrator must copy the value manually to the administrator file. ConnLab does not migrate or remove the old key. A future managed deployment may select the same file contract with `CONNLAB_ADMIN_CONFIG_PATH`.

## Moving To A New Version

1. Close ConnLab.
2. Copy the new ConnLab release folder to the computer.
3. Start `ConnLab.exe` from the new folder.

Your existing local settings remain under `%LOCALAPPDATA%\ConnLab`.
