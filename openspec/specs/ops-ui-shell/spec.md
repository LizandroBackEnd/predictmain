# Ops UI Shell Specification

## Purpose

Defines the shared industrial dashboard shell for PredictMain operations screens: layout chrome, navigation, light/dark theming aligned to the Kombai ops canvas, Tabler icon convention, and Shadcn primitive wiring. Excludes the RAG technical assistant.

## Requirements

### Requirement: Dashboard Shell Layout

The system MUST render authenticated-ops screens inside a shared App Router dashboard layout that provides navigation chrome and a main content region, and MUST NOT include a RAG assistant navigation entry in this change.

#### Scenario: Operator opens an ops route

- GIVEN the operator navigates to an in-scope dashboard route
- WHEN the dashboard layout renders
- THEN the page MUST show shared shell chrome (brand/nav + main content area)
- AND the navigation MUST expose links to Operations, Assets (or asset entry), Telemetry, and Predictions/Risk surfaces defined by this change
- AND the navigation MUST NOT include an Asistente técnico / RAG entry

#### Scenario: Unknown nested content still keeps shell

- GIVEN a valid dashboard child page
- WHEN the child page content is empty or loading
- THEN the shell chrome MUST still render
- AND the main content region MUST remain available for page-level empty/loading UI

### Requirement: Light And Dark Theme Parity

The system MUST support explicit light and dark themes using CSS variables aligned to the ops canvas palettes, and MUST allow the operator to switch theme without leaving the current route.

#### Scenario: Toggle theme on an ops screen

- GIVEN the operator is viewing any in-scope dashboard screen
- WHEN the operator activates the theme toggle
- THEN the UI MUST switch between light and dark token sets
- AND the current route MUST remain unchanged
- AND severity and series color tokens MUST remain distinguishable in both themes

#### Scenario: Theme preference persists for the session

- GIVEN the operator selects dark or light theme
- WHEN the operator navigates between in-scope dashboard routes
- THEN the selected theme MUST remain applied across those navigations within the browser session (or longer if persistence is implemented)

### Requirement: Tabler Icons Only In Ops UI

Dashboard shell and in-scope ops screens MUST use `@tabler/icons-react` for UI icons and MUST NOT introduce Lucide icons for those surfaces in this change.

#### Scenario: Shell navigation icons render

- GIVEN the dashboard shell navigation is visible
- WHEN icons are displayed for nav items and the theme control
- THEN those icons MUST come from Tabler Icons
- AND the build MUST NOT require `lucide-react` for the in-scope ops shell

### Requirement: Shadcn Primitive Foundation

The dashboard shell MUST be built on Shadcn UI primitives under `src/components/ui/` and MUST consume Tailwind utility classes for layout and spacing.

#### Scenario: Shared primitives are reusable

- GIVEN more than one ops screen needs a button, badge, or panel primitive
- WHEN those screens render interactive chrome
- THEN they MUST reuse shared Shadcn primitives from `src/components/ui/`
- AND screen-specific composition MUST stay under the owning route’s `_components/` when used by only one surface
