# Product

## Register

product

## Users

ConnLab is used by electronic connector laboratory engineers and lab coordinators on offline Windows workstations. These users are not programmers. Their daily context includes Outlook or exported email, Word application forms, Excel or file attachments, local project folders, LTR tracking, and repeated handoff checks.

The primary user job is to convert incoming request material into a traceable laboratory project, then move that project through precheck, LTR registration, and safe folder creation without losing the original source material.

## Product Purpose

ConnLab is an offline Windows-first workbench for connector laboratory intake and project preparation.

The current MVP supports:

- Project registry
- Application form upload and parsing
- Deterministic precheck
- LTR registration and tracking
- Project folder preview and generation
- Local SQLite persistence
- Minimal React frontend connected to FastAPI

The Phase 5 goal is to make the existing MVP flow feel like a credible laboratory workbench. The UI must clarify project state, next action, warnings, and blockers before deeper business workflows are added.

Long-term success means a non-programmer lab engineer can start from real request material, review extracted data, confirm project creation, resolve precheck issues, register LTR, and generate the project folder without using code.

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
- A future-feature showcase that exposes Matrix, Reports, or AI as active features

## Design Principles

1. Workflow before tools. Organize screens around project lifecycle stages, not around implementation modules.
2. State before action. Every page must show current state, blocker, and next action.
3. Traceability before convenience. Original files, extracted records, warnings, LTR, and generated folders must remain visibly connected.
4. Familiarity before novelty. Use standard product patterns: sidebar, top bar, table, badges, focused action panels, clear empty states.
5. Preview before write. Folder and file operations must show preview or conflict state before execution.

## Accessibility & Inclusion

Target WCAG 2.1 AA where practical for the MVP frontend.

Required considerations:

- Clear focus states for keyboard users
- Semantic color paired with text labels
- High enough contrast for status badges and errors
- No motion required to understand state changes
- Chinese UI copy should remain concise and action-oriented when localized
