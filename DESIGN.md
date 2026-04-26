---
name: ConnLab
description: Offline connector laboratory workbench for intake, precheck, LTR, and folder preparation
colors:
  canvas: "#f4f7fb"
  surface: "#fbfdff"
  surface-muted: "#e8eef6"
  ink: "#172033"
  ink-muted: "#647084"
  border: "#d8e0ea"
  primary: "#1f66d1"
  primary-strong: "#164aa3"
  ready: "#0f8ea8"
  success: "#2f8f68"
  warning: "#9a641c"
  danger: "#c2413a"
  sidebar: "#eef4fb"
  sidebar-hover: "#e7f0fb"
  sidebar-active-border: "#bfd7f2"
typography:
  headline:
    fontFamily: "Aptos, Segoe UI, Microsoft YaHei, system-ui, sans-serif"
    fontSize: "24px"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  title:
    fontFamily: "Aptos, Segoe UI, Microsoft YaHei, system-ui, sans-serif"
    fontSize: "18px"
    fontWeight: 700
    lineHeight: 1.25
  body:
    fontFamily: "Aptos, Segoe UI, Microsoft YaHei, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "Aptos, Segoe UI, Microsoft YaHei, system-ui, sans-serif"
    fontSize: "12px"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "0.08em"
rounded:
  sm: "6px"
  md: "10px"
  lg: "16px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "24px"
  xxl: "32px"
components:
  button-primary:
    backgroundColor: "{colors.primary-strong}"
    textColor: "{colors.surface}"
    rounded: "{rounded.md}"
    padding: "10px 16px"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "10px 16px"
  status-warning:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.warning}"
    rounded: "{rounded.sm}"
    padding: "4px 8px"
---

# Design System: ConnLab

## 1. Overview

**Creative North Star: "The Lab Ledger Workbench"**

ConnLab should feel like a disciplined lab ledger with modern workbench controls. It is not a landing page, not a developer console, and not an ERP menu maze. The interface should disappear into the work: import, review, precheck, register, preview, generate.

The system uses a low-saturation cool workbench palette because the physical scene is daytime laboratory administration on a Windows workstation. The palette should feel calm, clean, and operational, with enough contrast for dense project work. Color exists to signal state and action, not to decorate.

**Key Characteristics:**

- Left-navigation product shell, not a centered hero page
- Project-first workflow with visible status and next action
- Dense but readable tables, forms, and issue panels
- Restrained blue, cyan, green, warning, and danger state colors
- Familiar controls with consistent hover, focus, disabled, and error states

## 2. Colors

The palette is a restrained cool workbench system: pale blue-gray canvas, cold-white surfaces, blue primary actions, cyan ready states, green success states, and low-saturation warning/error colors.

### Primary

- **Workbench Blue**: Used for current navigation, selected workflow step, and primary actions. It must stay focused on action and selection.
- **Deep Workbench Blue**: Used for primary button depth and high-confidence actions.

### Secondary

- **Ready Cyan**: Used only for actionable ready states and informational status.
- **Confirmed Green**: Used only for completed, passed, or confirmed states.

### Tertiary

- **Warning Amber**: Used for warnings that require review but do not always block progress.
- **Blocker Red**: Used for failed or blocked states and destructive-risk warnings.

### Neutral

- **Cool Lab Canvas**: Main app background.
- **Cold White Surface**: Panels, inputs, and table surfaces.
- **Light Sidebar Layer**: Persistent navigation surface, kept lighter than content text and quieter than cards.
- **Blue Gray Divider**: Borders and separators.
- **Muted Ink**: Secondary labels, metadata, helper text.

### Named Rules

**The State Owns Color Rule.** Color is reserved for current selection, next action, and semantic state. Decorative color blocks are prohibited.

**The No Pure Neutral Rule.** Do not use pure black or pure white. Every neutral is slightly blue-tinted to match the cool workbench atmosphere.

## 3. Typography

**Display Font:** Aptos, Segoe UI, Microsoft YaHei, system-ui, sans-serif  
**Body Font:** Aptos, Segoe UI, Microsoft YaHei, system-ui, sans-serif  
**Label/Mono Font:** Cascadia Code or Consolas for IDs only

**Character:** One pragmatic sans stack keeps the product familiar on Windows. It should support Chinese labels cleanly and keep dense data readable.

### Hierarchy

- **Headline** (700, 24px, 1.2): Page titles and major workbench headings.
- **Title** (700, 18px, 1.25): Panel titles, step titles, and section headers.
- **Body** (400, 14px, 1.55): Forms, table cells, descriptions, and issue text.
- **Label** (700, 12px, 1.2): Field labels, table headers, metadata, and badges.

### Named Rules

**The No Display Font Rule.** Product labels, buttons, tables, and workflow steps use the same sans family. Decorative display type is prohibited.

## 4. Elevation

ConnLab uses tonal layering and borders first. Shadows may appear only for app shell separation or hover feedback, and must remain subtle. The product should feel stable, not floating.

### Shadow Vocabulary

- **Shell Lift** (`0 12px 32px rgba(31, 26, 15, 0.10)`): Reserved for the main shell or large elevated surface.
- **Interactive Lift** (`0 4px 12px rgba(31, 26, 15, 0.08)`): Optional hover response for clickable rows or panels.

### Named Rules

**The Flat By Default Rule.** Surfaces are flat at rest. Use borders and background tone before shadow.

## 5. Components

### Buttons

- **Shape:** Gently rectangular, not pill-like (10px radius).
- **Primary:** Deep Workbench Blue background with Cold White Surface text, used for the next action only.
- **Hover / Focus:** Slight tonal shift and visible focus ring. No animated layout movement.
- **Secondary:** Cold White Surface background, Blue Gray Divider border, Workbench Ink text.
- **Disabled:** Muted surface with muted text. Disabled buttons must explain why nearby.

### Chips

- **Style:** Small rectangular badge with semantic text and light tinted background.
- **State:** Use for workflow status, issue severity, and completion state.

### Cards / Containers

- **Corner Style:** Medium radius for panels (10px to 16px).
- **Background:** Cold White Surface on Cool Lab Canvas.
- **Shadow Strategy:** Flat by default, subtle hover only when clickable.
- **Border:** Blue Gray Divider border.
- **Internal Padding:** 16px to 24px depending on density.

### Inputs / Fields

- **Style:** Cold White Surface background, Blue Gray Divider border, 10px radius.
- **Focus:** Primary accent focus ring and border shift.
- **Error / Disabled:** Error text paired with border color and helper message.

### Navigation

- **Style:** Persistent left sidebar with top bar context.
- **Default:** Muted Ink text on a light blue-gray navigation layer.
- **Active:** Cold White Surface selected row with Workbench Blue text and pale blue border. Do not use thick side stripes.
- **Disabled:** Muted text and unavailable label for future items.

### Workflow Stepper

- **Style:** Sequential stages with status badge, next action, and blocking reason.
- **Behavior:** Only the active step expands into the action panel. Completed and blocked steps remain summarized.

## 6. Do's and Don'ts

### Do:

- **Do** use a left-navigation app shell with a top context bar.
- **Do** make every page answer current state, blocker, and next action.
- **Do** use tables or dense rows for project lists.
- **Do** show precheck issues as business-readable cards.
- **Do** pair every semantic color with text, not color alone.
- **Do** keep all file and folder actions behind preview or confirmation.
- **Do** keep API calls centralized in `frontend/src/api/client.ts`.

### Don't:

- **Don't** expose Matrix, Report, AI review, permissions, or installer work as active UI.
- **Don't** use a landing-page hero for workflow screens.
- **Don't** create a toolbox page full of disconnected buttons.
- **Don't** show raw backend errors as final user guidance.
- **Don't** use gradient text, decorative glassmorphism, colored side-stripe cards, or identical icon-card grids.
- **Don't** require users to understand SQL, API paths, or backend state names.
- **Don't** claim real email or Word intake is implemented during Phase 5.
