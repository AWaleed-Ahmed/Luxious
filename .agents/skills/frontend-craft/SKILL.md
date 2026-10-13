---
name: frontend-craft
description: Plan, build, and visually verify Luxious interfaces, especially PySide6 survey screens, measurement tables, and Matplotlib room maps. Use for UI design or polish; follow the existing stack and use web guidance only for a requested web interface.
metadata:
  source: frontend-skills.zip
  adaptation: Luxious PySide6 desktop interface
---

# Frontend Craft for Luxious

Adapted from the user-provided frontend skill. Read `ui/styles.py`, the affected widgets, translations, and map renderer before designing changes. Preserve the requested scope and existing authorization; record a design plan when it helps, without introducing a new approval gate for work already requested.

## Plan the interface

For a substantial screen change, record the surveyor's task, layout, token choices, assets, and observable done criteria in `docs/plans/`. Reuse the existing palette, typography, spacing, and Qt styles where suitable. Keep the room map and measurement workflow prominent, and use visual hierarchy to distinguish controls, recorded values, results, and warnings.

Read [anti-generic.md](references/anti-generic.md) when deciding visual direction or interface copy. Adapt its website examples to an engineering desktop tool rather than applying them mechanically.

## Build in the existing stack

- Use PySide6 widgets, layouts, signals, focus order, shortcuts, accessible names, and Qt styles for the desktop UI. Respect the 960 × 600 minimum window and high-DPI behavior.
- Keep drawing code in the existing Matplotlib visualization layer. Retain physical scale, units, coordinate orientation, colorbar meaning, and readable labels.
- Make manual entry, active-point selection, capture, advance, undo, and missing readings understandable. Preserve distinctions between measured, expected, and difference displays.
- Use `i18n/translations.py` for user-facing text and verify English, Romanian, and German text fits affected controls.
- Prefer existing icons or vector/code assets. Use `image-studio` only when an actual bitmap illustration or promotional asset is needed. Scientific maps, contours, readings, and report figures must come from project data and the numerical renderer.
- Keep long-running acquisition and computation from blocking interaction. Follow the application's threading and event-loop conventions.

For an explicitly requested web interface, first confirm the chosen web stack. Use semantic HTML, labels, visible keyboard focus, responsive layouts, reduced motion, and meaningful alternative text. Do not introduce a web framework while editing the desktop application.

## Verify what changed

Use existing UI tests or focused workflow checks appropriate to the change. For substantial desktop layout changes, capture and inspect screenshots at the minimum window size, default 1380 × 860 size, and a larger or high-DPI configuration. Check clipping, dock resizing, table readability, contrast, focus visibility, keyboard operation, and translated text.

For web work, use browser screenshots at representative narrow, medium, and wide viewports. Browser tools are relevant to the web interface rather than native Qt widgets.

Report the changed files, behavior, visual checks, and anything that could not be verified. An offscreen widget test does not establish that the desktop layout was visually inspected.
