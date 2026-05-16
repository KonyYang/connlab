# Product

## Register

product

## Users

ConnLab is used by electronic connector laboratory engineers and lab coordinators on offline Windows workstations. These users are not programmers. Their daily context includes Outlook or exported email, Word application forms, Excel or file attachments, local project folders, LTR tracking, Matrix review, test execution follow-up, and repeated handoff checks.

The primary user job is to convert incoming request material into a traceable laboratory project, then move that project through precheck, LTR registration, Matrix authority review, test execution tracking, and safe output preparation without losing the original source material.

## Product Purpose

ConnLab is an offline Windows-first workbench for connector laboratory project preparation and Matrix-driven laboratory execution.

The historical MVP baseline supports:

- Project registry
- Application form upload and parsing
- Deterministic precheck
- LTR registration and tracking
- Project folder preview and generation
- Local SQLite persistence
- Minimal React frontend connected to FastAPI

The current Phase 11 foundation extends that baseline with Project Workbench, Matrix authority draft lifecycle, Section 2 write-back, test-record and fee generation, approval package placement, and output freshness tracking.

The next product direction is the Matrix-driven Laboratory Execution Phase. Matrix is the execution authority map, Project remains the lifecycle container. Step-level execution data, evidence, images, and lifecycle state should become the structured source for derived outputs such as Test Record, Report, Fee Evaluation, and Approval Package.

Long-term success means a non-programmer lab engineer can start from real request material, establish the authoritative Matrix, track live testing by group and step, keep evidence and outputs synchronized, and close a project without relying on ad hoc Word/Excel state as the source of truth.

## Brand Personality

Professional, calm, traceable.

ConnLab should feel like a disciplined lab notebook joined with a modern work queue. It should be quiet enough for daily use, dense enough for project operations, and explicit enough that users do not guess the next step.

Tone:

- Direct
- Operational
- Business-readable
- No playful copy
- No technical stack language in user-facing UI

## Anti-references

ConnLab must not look or behave like:

- A marketing landing page with a large hero and disconnected cards
- A generic AI-generated dashboard
- A toolbox full of unrelated buttons
- An ERP-style menu maze
- A dark neon developer tool
- A decorative glassmorphism concept UI
- A future-feature showcase that exposes Reports, AI, permissions, or deployment work as active features before task approval
- An Excel-like Matrix editor where cells remain unstructured strings
- An approval package dashboard where setup documents crowd out the live Matrix execution view

## Design Principles

1. Workflow before tools. Organize screens around project lifecycle stages, not around implementation modules.
2. State before action. Every page must show current state, blocker, and next action.
3. Traceability before convenience. Original files, extracted records, warnings, LTR, and generated folders must remain visibly connected.
4. Familiarity before novelty. Use standard product patterns: sidebar, top bar, table, badges, focused action panels, clear empty states.
5. Preview before write. Folder and file operations must show preview or conflict state before execution.
6. Matrix before output. Matrix is the execution authority map; Test Record, Report, Fee Evaluation, and Approval Package are derived outputs.
7. Step before report. Step-level execution state, data, images, evidence, and lifecycle events must be structured before report automation expands.
8. Setup supports execution. Folder, source materials, approval package, and fee evaluation should be status entries or setup surfaces, not the Workbench main visual priority once Matrix authority exists.

## Accessibility & Inclusion

Target WCAG 2.1 AA where practical for the MVP frontend.

Required considerations:

- Clear focus states for keyboard users
- Semantic color paired with text labels
- High enough contrast for status badges and errors
- No motion required to understand state changes
- Chinese UI copy should remain concise and action-oriented when localized
