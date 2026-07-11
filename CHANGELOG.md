# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

- Revamp folder picker to match canonical VideoTools implementation with breadcrumbs, drive enumeration, and friendly labels (Issue #21).
- Fix folder-browser parent navigation so the picker moves up to the parent folder instead of reloading the current view (Issue #20).
- Harden folder browsing at drive roots so inaccessible folders no longer break navigation when moving up from a subfolder (Issue #20).
- Add folder browser selection to the UI so users can choose a root folder without typing the path manually (Issue #20).
- Add live current-file and ETA summary cards during conversion (Issue #19).
- Add live session progress cards that update during conversion (Issue #18).
- Stabilize large conversion progress state to avoid page-load failures during long runs (Issue #17).
- Limit scan results table height and add scrollbars (Issue #16).
- Show folder paths relative to the selected root in the results table (Issue #16).
- Reset progress UI to idle after conversion completes (Issue #15).
- Fix folder metrics for in-place conversion progress (Issue #14).
- Convert images in place instead of using Converted.webp folders (Issue #13).
- Keep completed folders marked as done after a conversion run finishes (Issue #8).

- Initial ImageTools scaffold with Flask app, basic WebP conversion workflow, and starter UI.
- Add progress reporting for image conversion runs (Issue #1).
- Add folder-level scan summary (Issue #2).
- Add folder results table (Issue #3).
- Refine scan results layout (Issue #4).
- Remove workflow notes card (Issue #5).
- Add per-folder conversion status (Issue #6).
- Remove redundant root label (Issue #7).
- Update folder statuses during conversion (Issue #8).
- Skip existing WebP files (Issue #9).
- Add per-folder progress and saved-size metrics (Issue #10).
- Add folder progress reporting and browser verification (Issue #11).
- Normalize folder paths for progress updates (Issue #12).
