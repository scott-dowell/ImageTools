# ImageTools implementation plan

## Working convention

- Create a GitHub issue for each significant implementation step.
- Add a changelog entry for each completed change, including the issue number.
- Keep the implementation work incremental and verified in the browser with relevant tests.

## Current implementation status

The core ImageTools workflow is now implemented and verified. The project has progressed beyond the initial scaffold into a working browser-driven conversion experience with live progress reporting, folder-level status, and in-place WebP conversion.

## Recommended implementation order

| Area | Status | Notes |
| --- | --- | --- |
| Baseline review | Completed | Reviewed the VideoTools structure, Flask layout, and Bootstrap-oriented UI patterns, and reused the same simple app-shell approach. |
| Initial scaffold | Completed | Created the Flask app, converter module, and regression tests for discovery and conversion behavior. |
| Core conversion workflow | Completed | Supports root-folder selection, recursive discovery, safe in-place WebP conversion, and clear success/failure reporting. |
| UX polish | Completed | Uses a fresh copy of sample-image fixtures for browser verification before meaningful UI changes. |
| Progress and status tracking | Completed | Shows scan counts, live run status, folder-level progress, current-file detail, ETA, and saved-byte totals. Pause/resume/stop controls are implemented. |
| Folder and batch visibility enhancements | Mostly completed | Includes the folder results table, relative path display, scrollable results, and live summary cards. |
| Later-phase refinements | Partially completed | Sidebar layout reordered for workflow clarity. Pause/stop controls added. |

## Outstanding work

- Add quick folder actions such as copy path and open in Explorer.
- Add a lightweight file preview experience for selected folders.
- Add a cleanup step for legacy converted folders.
- Add richer per-image and per-folder savings details.
- Consider drag-and-drop or folder-browser integration for easier input selection.
- Revisit whether a small local database is needed for history, resumability, or longer-term tracking.
