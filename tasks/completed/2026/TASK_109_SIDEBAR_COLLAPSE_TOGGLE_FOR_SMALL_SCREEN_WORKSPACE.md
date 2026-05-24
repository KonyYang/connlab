# TASK_109_SIDEBAR_COLLAPSE_TOGGLE_FOR_SMALL_SCREEN_WORKSPACE

## Status

done

## Purpose

Add a sidebar collapse/expand control so small laptop users can allocate more horizontal space to the main work area.

## Scope

- Frontend shell only.
- Add sidebar toggle control.
- Collapsed state keeps icon-only navigation.
- Persist user preference locally across refresh.
- No route/business/API behavior changes.

## Validation

```powershell
npm run build
py -m pytest tests\unit\test_frontend_shell_files.py -q
```

## Stop Rule

Stop after implementation and task board update.
