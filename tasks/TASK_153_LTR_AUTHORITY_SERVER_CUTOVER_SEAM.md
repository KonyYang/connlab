# TASK_153 LTR Authority Server Cutover Seam

> Status: proposed
> Created: 2026-05-09
> Phase: Phase 10E - External resource settings and LTR workbook authority

---

## 1. Purpose

Document and harden the seam that will later allow ConnLab to switch LTR authority from public-drive Excel to a server/database-backed authority.

This is not a server implementation task. It is a boundary cleanup task after the Excel-backed authority is working.

---

## 2. Dependencies

Depends on `TASK_151`.

---

## 3. Scope

In scope:

- Document the LTR authority interface and current Excel adapter.
- Verify New Project and Workbench do not import Excel/COM details directly.
- Ensure local SQLite is treated as structured copy, not official authority while Excel mode is active.
- Add tests or static checks that prevent UI/API route code from directly using workbook gateways.
- Add a migration note for future server authority.

Out of scope:

- No server.
- No authentication.
- No LAN deployment.
- No report generation.

---

## 4. Acceptance Criteria

- Future cutover path is documented.
- Excel-specific concerns are behind the adapter boundary.
- UI and high-level application services speak in terms of LTR application/authority, not workbook cells.
- The board identifies the next server-readiness task only if MVP scope allows it.

