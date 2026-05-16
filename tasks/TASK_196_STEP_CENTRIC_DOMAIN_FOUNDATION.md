# TASK_196 Step-Centric Domain Foundation

> Status: done  
> Created: 2026-05-16  
> Phase: Phase 11 controlled foundation baseline, preparing Matrix-driven Laboratory Execution Phase

---

## 0. Execution Gate

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current prerequisite: `TASK_195_PROJECT_WORKBENCH_RUNTIME_CONSOLE_INFORMATION_ARCHITECTURE` complete.
- Why this task is allowed:
  - `docs/task_board.md` recommends defining and approving TASK_196 after TASK_195.
  - The user approved the TASK_196 plan and explicitly requested creating the task file and正文文档.
  - This task is documentation and domain foundation design only.

Implementation gate:

- no Python domain dataclass implementation;
- no SQLAlchemy model implementation;
- no database migration;
- no repository/service/API implementation;
- no frontend implementation;
- no read model implementation;
- no runtime status engine implementation.

---

## 1. Purpose

Define ConnLab's minimal step-centric domain foundation before any runtime implementation.

The foundation preserves:

```text
Matrix is the execution authority map, Project remains the lifecycle container.
Step is the future execution data and lifecycle unit.
```

---

## 2. In Scope

- Domain authority boundaries.
- Conceptual `StepInstance` definition.
- Stable identity rules.
- Matrix token to StepInstance mapping.
- Step lifecycle concepts.
- Runtime attention relationship.
- Derived output relationship.
- Runtime Projection Boundary.
- Data ownership boundaries.
- Future implementation slices.

---

## 3. Out Of Scope

- Python dataclasses.
- Database schema.
- API design.
- Runtime read model.
- Status/priority engine.
- Frontend/UI changes.
- Report sync engine.
- Test data import.
- Image/evidence persistence.

---

## 4. Deliverables

- `docs/step_centric_domain_foundation.md`
- `docs/task_196_step_centric_domain_foundation_plan.md`
- `tasks/TASK_196_STEP_CENTRIC_DOMAIN_FOUNDATION.md`
- task-board completion update

---

## 5. Acceptance Criteria

- Step-centric domain foundation document exists.
- It defines Step identity without collapsing repeated test items.
- It separates domain identity from runtime projection.
- It states Runtime Projection is not source of truth.
- It preserves Project as lifecycle container and Matrix as execution authority map.
- No runtime backend/frontend/API/DB/Office files are changed.

---

## 6. Validation

Document validation:

1. Confirm required files exist.
2. Confirm forbidden implementation scope is not introduced.
3. Confirm no runtime source files changed.
4. Run static governance guard tests:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

---

## 7. Stop Condition

Stop after TASK_196 completion. Do not automatically enter TASK_197.
