# Luxious — two-person implementation handoff

Updated: 13 October 2026. Application root: this directory (`Luxious` inside the workspace's outer `Luxious` directory). Stack: Python, PySide6, Matplotlib, NumPy/SciPy, ReportLab, pyserial, bleak, python-docx.

This document describes remaining work after inspecting the current working tree. `PROJECT_PLAN.md` is the original detailed roadmap; its baseline descriptions are older than several implemented changes. Feature IDs below refer to that roadmap. HEAD is `317a699`, but substantial implementation exists as uncommitted changes: preserve and hand off the working tree, not just that commit.

This handoff is based on source inspection. Tests and real hardware were not rerun for this documentation task. The previous implementation run reported 25 passing non-hardware tests and two failures in legacy hardware tests; that is historical evidence, not current release certification.

## 1. What already exists

| Feature | Current implementation | Remaining qualification |
| --- | --- | --- |
| F01–F03: editing and quick entry | Select-point Edit, add/delete, position dialog, quick lux input and table commands, Done | Permission gaps, empty-project entry, clear-reading undo, visible validation, stable IDs/reference links |
| F04: graph | Improved markers, colorbar, value labels, preserved viewport, expected/difference rendering | Pixel hit testing, dense-label management, consistent comparison scales, coverage masks, performance, imported plan layer |
| F05: DIALux import | Coordinate CSV/text preview; expected lux; reported or calculated design average; physical readings pending | No native project parser, plan graphics, fixtures, full geometry, persistent reference dataset or verified interchange fixtures |
| F06: USB | Real COM opening and numeric ASCII line reading; fresh sample timestamps | No verified manufacturer profile/support matrix; disconnect/error handling needs work |
| F07: Bluetooth | BLE discovery; honest unsupported-profile message | Actual meter connection, GATT subscription and decoding are not implemented |
| F08: focused measurement | Capture, fresh-reading check, next pending point, Edit/Done return flow | Central device/source state, disconnect recovery, navigation/progress, simulator integration, mode enforcement |
| F09: Word import | Numeric `.docx` tables; locale parsing, spacing/origin configuration, measured/expected choice, undoable import | Real fixtures, spatial preview, orientation controls, merged/header-table handling, stale-preview fix |
| F10: languages | EN/RO/DE dictionaries, runtime switching, persisted language setting | Numerous English literals remain in dialogs, menus, status and errors; full journey QA needed |
| F11: worksheets/reports | Localized A4 PDF reports and field worksheets, map export, language choice defaulting to app language | Full localized chart/caption QA, traceability fields, company template/sign-off options, long/dense output verification |
| F12: interface cleanup | Short tabs, target preset dropdown, existing vector icon family, clean startup grid | Application-wide action/icon audit, accessible names, duplicates/dormant widgets, consistent public branding |
| F13: engineering comparison | Signed deltas, MAE/RMSE, expected-zero handling, canonical comparison CSV | Durable reference matching, moved/deleted/excluded points, conditions/calibration, clearly separated requirement types |
| Project persistence | Atomic replacement, version 2.0 output, legacy 1.0 loading, basic validation, unsaved-work prompts | Not the complete schema envisioned in the original plan; assets/history/session persistence, recovery and complete validation still missing |

Avoid rebuilding the existing foundations. Complete them against the acceptance criteria below.

**Reading semantics:** `lux=None` is pending; `lux=0` is a real measured zero. Imported DIALux design values currently populate `expected_lux`, with physical readings pending. The original request mentioned zero initialization, but implementation deliberately uses pending to avoid treating unmeasured rooms as zero-lux surveys. A visible zero placeholder can be discussed without changing that stored meaning.

## 2. People and ownership

| Person | Main responsibility | Primary files |
| --- | --- | --- |
| **Person 1 — interface and deliverables** | Review/Edit/Measure UX, graph interactions and presentation, localization, import/device dialogs, reports and final user journeys | `ui/`, `visualization/map_plotter.py`, `i18n/`, `reporting/`, UI/report tests |
| **Person 2 — data and acquisition** | DIALux/Word/CSV adapters, geometry/reference data, USB/BLE, sessions/provenance, validation/persistence, numerical correctness and recovery | `models/`, `persistence/`, `measurement_sources/`, `analysis/`, `utils/undo_commands.py`, data/device tests |

Person 1 owns integration edits in `ui/main_window.py`. Person 2 exposes services, signals and commands instead of independently refactoring that file. Person 2 owns model/schema changes; Person 1 reviews how those fields affect presentation and reports. Both add tests for their own behavior.

Use separate branches/worktrees and review changes at the integration gates below. Do not have both people editing shared files simultaneously. Agree on API/data contracts before broad refactors; do not introduce a web framework or rewrite the renderer without measured need.

## 3. Person 1 backlog

### A1 — Finish mode permissions and editing behavior [P0, F01–F03/F08]

- Introduce one mode controller/policy for Review, Edit and Measure, replacing scattered booleans where useful. Enforce policy in handlers and shortcuts, not only disabled widgets.
- Table and clear-reading handlers currently check `edit_mode` without a complete Measure guard. Clear is currently blocked in Edit, despite Edit being the intended correction interface. Resolve this consistently with the mode policy.
- Audit direct edits, hidden actions, context menus and undo/redo in Measure. Capture is the only normal measurement write; corrections go through Edit.
- Support an empty project: Create grid/Add first point must be reachable when no point can be selected.
- Keep device connection lifetime independent of modes; show disconnect/stale state on returning from Edit. Restore selection, panels, focus and viewport on Done/Escape.
- Show useful errors for invalid input, support decimal comma, keep Enter correction behavior predictable, and synchronize deselection and deletion with the table.

**Done:** Review → Edit → Done and Measure → Edit → Done work through actual UI events, including deleted selection, empty room and lost device. Unrelated shortcuts cannot mutate data in Measure. Clear/retake in Edit works through Person 2's commands.

### A2 — Finish graph clarity and responsiveness [P1, F04]

- Replace fixed physical hit radii (`0.20/0.35 m`) with display-pixel hit testing.
- Add All/Selected/None labels and overlap management for dense grids. Pending/measured/excluded states must remain distinguishable without color alone.
- Use consistent measured/expected scales when comparing maps and a zero-centered diverging scale for differences. Coordinate with Person 2's field/coverage contract.
- Add imported background plan controls: visibility, opacity and alignment UI; render geometry/fixture layers from Person 2's models.
- Avoid full interpolation on every selection/hover; cache/debounce and display only current revision results. Profile up to 2,500 points before changing rendering technology.

**Done:** graph works at 960×600 and a larger desktop size, with readable labels and legends, stable zoom and usable dense point selection. Screen and exports show the same data and scales. Record performance on a stated machine.

### A3 — Complete EN/RO/DE and action cleanup [P1, F10/F12]

- Translate remaining English literals in imports, hardware setup, mode bars, statuses, errors, project dialogs and export-language chooser. Language persistence already exists; verify it rather than reimplementing it.
- Update existing QAction text/state instead of rebuilding actions on translation; preserve mode permissions and shortcuts.
- Extend `ui/icons.py` consistently for device, import/export and edit actions. Add accessible names/tooltips to icon-only buttons.
- Audit repeated controls and dormant UI; preserve advanced engineering functions through concise disclosure. Check minimum-width German/Romanian layouts and keyboard focus.
- Apply the chosen public name consistently across window title, help, reports and package assets.

**Done:** a complete survey/import/export journey is understandable in each language; switching languages does not enable forbidden controls; no emoji controls or unexplained icons remain.

### A4 — Import/device UI and Word preview [P1, F05–F09]

- Build visual import previews showing point placement, orientation, units, source, warnings and the impending replacement.
- Fix Word preview invalidation: changing controls after Preview must disable Import or rebuild the preview on commit; current dialog can import an old preview.
- Expose Word table/header selection, axis/orientation and merged-cell policy using Person 2's adapter. Default numeric locale from app language where appropriate.
- Expose explicit USB/BLE protocol/profile selection and one active capture source. Add a clearly labeled simulator for development using the existing mock source.
- Show live value, age, progress, previous/next pending point, reconnect and paused state; provide a reachable connection workflow while focused measuring.

**Done:** preview matches committed data; cancel preserves the project; device status reflects real connection/sample state; mode changes keep an established connection intact.

### A5 — Professional final outputs [P1, F11/F13]

- Extend existing report/worksheet templates with Person 2's reference coverage, conditions, instrument/calibration and correction history summaries.
- Separate room-average requirements, per-point limits and uniformity criteria; show population and requirement source. Do not label a point-threshold check as complete room compliance.
- Verify EN/RO/DE headings, map/chart labels, decimal formatting, glyphs, repeated schedule headers, long notes, dense grids and greyscale printing.
- Add company/revision/sign-off fields if selected for release. Editable Excel/Word output is optional pending the worksheet-format decision; PDF already exists.

**Done:** rendered pages are visually inspected, UI/report values come from one snapshot, pending stays distinct from zero, formats match their file signatures, and output language matches the chosen locale.

## 4. Person 2 backlog

### B1 — Repair command/validation gaps first [P0, F02/F03 and foundations]

- **Confirmed defect:** `ClearMeasurementCommand` implements `redo()` but no `undo()`. Restore the full saved point, including timestamp, device and outlier metadata, and add a round-trip regression check.
- Give import commands an explicit sentinel for omitted metadata versus clearing it. `None` currently means preserve old design average; unrelated layout replacements can retain stale design metadata.
- Audit all project mutations, including grid regeneration and reference overrides. Add one undoable command per logical operation; stabilize IDs and traversal order without silent reuse/remapping.
- Reject non-finite readings/coordinates at model and input boundaries. Current `MeasurementPoint` checks negativity but permits NaN/infinity.
- Validate complete CSV rows before commit and report row errors instead of silently skipping malformed numeric values. Validate bounds and IDs for new points. Staging in MainWindow already prevents mutation of the live project on parser failure.
- Extend project validation to raw room geometry and settings. Loading a version number alone is not the full schema migration.

**Done:** clear/edit/delete/layout import and undo/redo restore all relevant data; invalid rows and non-finite values cannot reach the active model; failed save preserves the previous file.

### B2 — Real DIALux interchange, geometry and reference data [P1, F05/F13]

- Obtain a real user export and identify its version, quantity, scene, surface/plane and coordinate contract. Test native `.evo/.evo2` feasibility separately; do not promise native support based on CSV parsing.
- Extend beyond the current coordinate-table reader with a verified supported workflow for a background plan plus calculation points. Import luminaires only as distinct entities, not as measured points.
- Persist original units, origin/rotation/scale transform, polygonal room/zones/exclusions and portable plan assets. Keep bounding extent distinct from actual room dimensions.
- Introduce immutable design-reference points and stable survey/reference matches. Moving/deleting survey points must preserve the original design and show unmatched/excluded coverage.
- Keep reported DIALux average separate from the unweighted sample mean; keep actual readings pending until capture/manual entry.
- Add representative fixtures, malformed-file cases and a documented compatibility matrix.

**Done:** one actual supported user workflow reproduces known point coordinates, design values and plan alignment after save/reopen on another machine. Unsupported formats fail with an actionable explanation.

### B3 — Verified USB and BLE acquisition [P1, F06/F07/F08]

- Build a project-independent device service with explicit selected source and disconnected/connecting/connected/failed state. Two sources must not silently compete for capture.
- Implement one exact USB model/profile: framing, units/range/overload, baud/settings, decoding and capture freshness, backed by recorded packets and physical readings.
- Implement one exact BLE model/profile: real BleakClient lifecycle, service/characteristic discovery, notifications/commands, packet decoder and disconnected callback. Current BLE connection deliberately rejects unsupported profiles.
- Fix serial reader exception behavior: clear connection/sample state and emit useful errors on cable loss instead of sleeping indefinitely while appearing connected. Cleanly stop workers on Disconnect and application exit.
- Keep simulator explicit and separate from physical drivers. Update legacy tests that expect fake BLE connection or permissive text parsing; retain protocol-specific coverage rather than weakening validation to satisfy them.

**Done:** physical meter readings agree with capture; overload, stale sample, cable/BLE loss, reconnect and Edit-return are verified. Publish only models actually tested. Bluetooth Classic is a separate scope choice if the selected meter requires it.

### B4 — Survey sessions, recovery and engineering integrity [P1, F13]

- Persist session progress/current point, operator, scene/daylight/plane, instrument serial/calibration, capture/manual/import origin and correction/retake history. Do not serialize live transport handles or reconnect automatically on load.
- Add autosave/recovery/resume using atomic persistence without replacing the user's primary file unexpectedly. Make portable assets and references part of the documented schema.
- Fix nearest-neighbor coverage: it currently fills the entire mesh even when `extrapolate_to_walls=False`. Apply coverage and room/zone masks across all interpolation/fallback paths.
- Compare explicit matches on the same plane/scene/quantity; expose matched/pending/excluded/extra counts and distinguish whole-survey/design averages from the matched subset.
- Separate average, per-point and uniformity requirements; add sourced configurable tolerances only after definitions are agreed. Preserve zero-reference exclusions for percentage metrics.
- Add stability/sample averaging and retake support if selected, recording the method and window rather than discarding provenance.

**Done:** incomplete or edited surveys remain interpretable; recovery preserves committed readings; zero stays measured; unsupported spatial areas remain visibly unresolved; migrated legacy values and order are retained.

### B5 — Robust Word adapter and engineer data exports [P1/P2, F09/F13]

- Add real `.docx` fixtures with numeric/blank cells, decimal formats, selected tables and header/coordinate variants. Define safe treatment of horizontal and vertical merges; never silently duplicate a measurement because Word repeats merged cells.
- Support explicit orientation/axis/header mapping and preserve source/table/cell provenance. Blank cells remain missing; physical scale must be supplied or verified.
- Extend canonical export with coordinate frame, quantity/plane/scene, provenance and coverage. Preserve stable canonical headers separately from localized presentation labels.
- Investigate CAD overlays/export back to DIALux only with real consuming-app evidence. XLSX output is an optional follow-up, not implied by the existing PDF worksheet.

**Done:** preview/commit/export reproduce fixture coordinates and values; unsupported tables produce useful errors; cancellation/failure and undo preserve the previous survey.

## 5. Shared integration gates and sequence

1. **Start together:** capture the existing working tree, choose initial meter models and a real DIALux/Word sample, and agree on `Mode`, `DeviceState`, `Sample`, `DesignReference`, `SurveySession` and import-preview contracts. Person 2 leads persisted data; Person 1 leads UI permissions.
2. **First parallel work:** Person 1 completes A1 and Word stale-preview correction; Person 2 completes B1 and nearest coverage correction from B4. Integrate with behavior tests before visual expansion.
3. **Data/acquisition gate:** Person 2 builds B2/B3; Person 1 builds A2/A4 against agreed adapters and a labeled simulator. Real-device work can proceed independently of graphical polish.
4. **Traceability/output gate:** B4 data contracts feed A5 reports and B5 exports. Person 1 completes A3 localization across both people's new flows.
5. **Release gate:** Person 2 leads PyInstaller dependency/backend packaging; Person 1 leads clean-machine UI, fonts, branding and end-to-end output checks. Both review README compatibility claims and regenerate representative samples.

Shared files: Person 1 integrates `ui/main_window.py`; Person 2 owns `models/project.py`, `utils/undo_commands.py` and schema migrations. Person 1 adds translation keys after Person 2 supplies user-facing failure semantics. Agree before modifying `requirements.txt`, `Lumination.spec` or report-facing schema. Add future version migrations rather than silently reusing 2.0 for incompatible data changes.

## 6. Decisions/evidence still needed from the project owner

- Exact USB and Bluetooth meter models, protocol documentation, and access to the physical devices.
- Actual DIALux version/files and whether “lighting points” means calculation points, luminaires, or both. Native parsing and exported-plan support are separate deliverables.
- Representative Word tables, including headers/merged cells and intended physical orientation.
- Final public name: Luxious or Lumination; report/company branding.
- Worksheet formats: current PDF, or additionally editable XLSX/DOCX.
- Requirement/tolerance definitions and preferred survey conditions/metadata.

These do not block command, UI, localization or coverage fixes. They do block claims of verified external compatibility. Effort is largest and least predictable for B2/B3 until samples/devices exist; do not treat the two people's ticket counts as equal calendar effort.

## 7. Optional later backlog — select explicitly

Multiple rooms/planes, repeated visits/scenes and before/after comparisons, team survey merging/multiple meters, uncertainty summaries, reviewed requirement profiles, editable spreadsheet worksheets and verified CAD overlays. Extend the reliable field-survey companion before considering full 3D lighting simulation or glare/UGR calculations.

## 8. Validation and development entry points

Run from this application directory with the existing Windows virtual environment:

```powershell
& .\.venv\Scripts\python.exe main.py
& .\.venv\Scripts\python.exe -m pytest -q
git diff --check
```

If pytest temporary-directory permissions fail, use a fresh, explicitly chosen writable `--basetemp` directory inside the workspace. Never target a directory holding user data; pytest manages/removes its base temporary contents.

Tests to extend: `tests/test_project_undo_imports.py`, `tests/test_persistence.py`, `tests/test_ui.py`, numerical tests, plus protocol/real import fixtures. Legacy hardware expectations in `tests/test_survey_and_refinements.py` need reconciliation with honest drivers. Passing software tests alone is not evidence of real device or DIALux compatibility.

Final acceptance journey: actual supported DIALux import → confirm plan and design average → save/reopen with assets → connect verified meter → capture pending locations → Edit/add/delete/correct → Done returns to Measure without losing connection → finish survey → review matched coverage → export readable EN/RO/DE worksheets/reports → repeat on a clean Windows install.

Available personal skills: `$frontend-craft` for Person 1's native interface work; `$image-studio` only for requested bitmap artwork. The standard PDF/document skills apply to rendering and inspecting deliverables. This handoff assigns work; it does not execute it or authorize unrelated publishing.
