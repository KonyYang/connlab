# Runtime Governance Freeze Rule

Last Updated: 2026-05-16
Status: active governance policy (post TASK_202)
Scope: runtime task planning and execution sequencing

## 1. Background

After TASK_194-TASK_202, the primary risk is no longer architecture ambiguity.  
The primary risk is execution drag from governance over-expansion, projection ontology explosion, and boundary-recursion task chains.

This rule freezes governance-only expansion and forces runtime slices to produce consumable outputs.

## 2. Core Policy

Starting after TASK_202, new tasks are not allowed to be only:

- governance-only
- philosophy-only
- boundary-only
- ontology-only

Exception is allowed only when implementation is genuinely blocked by a discovered architectural contradiction.  
Any exception task must document:

- concrete blocker evidence
- impact on the active implementation slice
- expiration/exit condition back to implementation slices

## 3. Runtime Slice Completion Rule

Every runtime slice must produce at least one consumable artifact.  
Do not allow abstraction-only layers without consumption validation.

Accepted consumable outputs include:

- backend runtime artifact
- projection consumer artifact
- runtime adapter
- immutable read model output
- frontend read-only prototype
- aggregation consumer
- runtime projection consumption validation

## 4. Runtime Consumer First Rule

Prefer slices that improve read-only runtime consumption:

- read-only projection consumers
- immutable runtime summaries
- frontend-consumable adapters
- fake/static runtime refresh prototypes

Do not prioritize at this stage:

- runtime engines
- orchestration systems
- lifecycle persistence systems
- complex StepInstance graphs
- execution state machines

## 5. Projection Minimality Rule

New projection DTOs are forbidden unless existing DTOs are proven insufficient.

Avoid:

- speculative future abstractions
- future-proof ontology expansion
- unnecessary projection hierarchy growth

Priority:

- minimality
- clarity
- rollback safety
- runtime consumption validation

Not required at this stage:

- architectural completeness

## 6. Workbench Replacement Rule

Current frontend Project Workbench is treated as a temporary shell.

Do not:

- incrementally beautify it
- keep adding setup widgets
- keep adding approval sections
- embed more editing surfaces

When UI implementation begins, use baseline replacement according to approved Runtime Console target mockup.  
Do not continue patching the current setup-heavy Workbench.

## 7. Workbench vs Matrix Editor Separation

### Project Workbench role: Runtime Console

Responsibilities:

- runtime overview
- attention surfacing
- projection consumption
- runtime navigation
- report sync visibility
- evidence visibility
- issue visibility
- step runtime entry

It is not:

- Matrix Editor
- setup dashboard
- workflow form
- approval workspace hybrid

### Matrix Editor role: Definition Studio

Responsibilities:

- test plan definition
- test item setup
- section/method/condition/requirement definition
- group step sequence definition
- template import
- intelligent filling assistance
- estimated completion/fee setup

It is not:

- runtime execution console
- runtime orchestration surface
- runtime attention dashboard

Matrix definition editing must remain outside Workbench.

## 8. Projection and Runtime Principles (Unchanged)

Continue strict preservation:

- Projection != Domain Identity
- Runtime Projection is not source of truth.
- Projection composition must remain independently evolvable.

Do not allow:

- projection-driven identity mutation
- projection-owned execution state
- UI-driven authority mutation
- runtime-engine creep into composition helpers

Composition helpers are pure aggregation boundaries, not runtime execution systems.

## 9. Post-TASK_202 Direction

Preferred task direction:

1. read-only runtime projection adapter slice
2. minimal runtime consumer prototype
3. Runtime Console baseline replacement
4. Matrix Editor baseline implementation

Avoid:

- governance recursion
- ontology expansion task chains
- premature runtime engines
- ORM-heavy StepInstance world modeling
- speculative runtime abstractions

Priority remains:

- runtime visibility
- traceability
- projection consumption
- incremental executable slices
- rollback safety

