# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

- Limit scan results table height and add scrollbars (Issue #16).
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
