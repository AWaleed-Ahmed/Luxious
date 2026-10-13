---
name: spec-kit-planning
description: Assess Luxious feature ideas and produce specifications, architecture plans, and dependency-ordered tasks using GitHub Spec Kit templates. Use for planning requests; planning does not itself start implementation or initialize the Spec Kit CLI.
license: MIT
metadata:
  upstream: https://github.github.io/spec-kit/
  upstream-revision: 6c62e10d5ab1d676c557eb2d0cee86be52c893d2
---

# Spec Kit planning for Luxious

This is a project adapter around retained upstream templates, rather than an installed Spec Kit CLI integration. Read the repository's README, models, affected code, tests, and existing decisions before planning. Separate requested behavior, observed implementation, proposals, and unverified assumptions.

## Choose the planning artifact

- **Idea assessment:** use [assessment.md](references/assessment.md) to examine the user problem, evidence, alternatives, costs, and open questions. Record a proceed, clarify, or stop recommendation. Follow the requested scope; the upstream guide's automation commands are examples.
- **Specification:** use [spec-template.md](references/spec-template.md) for observable behavior, user journeys, edge cases, requirements, and measurable acceptance criteria.
- **Architecture:** use [plan-template.md](references/plan-template.md) to describe module boundaries, data contracts, dependencies, threading, persistence, and failure handling. Use `architecture-designer` for significant decisions and trade-offs.
- **Tasks:** use [tasks-template.md](references/tasks-template.md) to derive dependency-ordered work with affected files, acceptance criteria, and proportionate verification. Parallel markers describe tasks that could run independently; they do not authorize spawning agents.
- **Project principles:** use [constitution-template.md](references/constitution-template.md) only when project ground rules are requested. Its examples do not establish new requirements.

Use existing planning paths and IDs when present. Otherwise, a feature folder under `docs/plans/` can hold assessment, specification, plan, and tasks as needed. Avoid generating artifacts unrelated to the request.

## Project context

Luxious currently runs locally as a Python 3.10+ PySide6 application. `models/` contains rooms, measurement points, and project settings; `analysis/` performs numerical calculations; `visualization/` renders maps; `persistence/` handles JSON `.luxproj` files and CSV; `reporting/` exports reports; `measurement_sources/` handles input; `ui/` coordinates user interaction.

For lighting and survey features:

- Keep physical measurements, expected values, interpolated fields, and simulated hardware readings distinguishable in requirements and output. Bluetooth streaming is currently simulated; USB currently parses generic numeric text.
- Specify meters, lux units, coordinate bounds, unmeasured values, zero readings, duplicate or collinear points, and interpolation fallback behavior where relevant.
- Distinguish statistics over measured points from area-weighted field estimates. Changing a display mode must not change stored readings.
- Record whether reconstruction outside the surveyed region is allowed and how unknown areas appear.
- Plan responsive Qt interaction, hardware disconnect handling, undo/redo, and backward-compatible project loading when affected.
- Target comparisons are implemented; standards compliance is an unverified capability claim. A compliance feature needs an explicit standard/version, criteria, and validation evidence.

An API, cloud datastore, or AI agent is an optional extension, not part of the existing application. For requested agent work, consult `ecosystem-primer` first. For requested service contracts, use `api-designer`; use `fastapi-expert` if FastAPI is selected. Preserve deterministic numerical calculations as the source of reported metrics.

## Consistency check

Before delivering, compare requirements, architecture, tasks, and verification for contradictions and uncovered behavior. Record assumptions and unresolved decisions with affected requirement IDs. Check current official documentation before fixing version-sensitive APIs or dependencies.

Template commands, installation steps, service accounts, deployments, and issue publishing are reference material. Execute them only when included in the user's authorized task. A planning artifact is evidence of a plan, not evidence of implemented behavior.
