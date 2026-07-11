# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

- Issue #25: Implement Pause/Play and Stop functionality for active conversion jobs with a dedicated UI controls card.
- Issue #24: Consolidate active job status and prioritize summary stats at the top of the interface.
- Issue #23: Decouple controls and status indicators into top-level cards for better UI clarity.
- Issue #22: Revamp the appearance to more align with VideoTools with a new header bar, consistent icons, and updated color scheme.
- Issue #21: Revamp folder picker to match canonical VideoTools implementation with breadcrumbs, drive enumeration, and friendly labels.
- Issue #20: Implement folder selection UI with hardened drive-root navigation and interactive parent directory logic.
- Issue #19: Add live current-file and ETA summary cards during conversion.
- Issue #18: Add live session progress cards that update during conversion.
- Issue #17: Stabilize large conversion progress state to avoid page-load failures.
- Issue #16: Limit scan results table height and show paths relative to the selected root.
- Issue #15: Reset progress UI to idle after conversion completes.
- Issue #14: Fix folder metrics for in-place conversion progress.
- Issue #13: Convert images in place instead of using Converted.webp folders.
- Issue #12: Normalize folder paths for progress updates.
- Issue #11: Add folder progress reporting and browser verification.
- Issue #10: Add per-folder progress and saved-size metrics.
- Issue #9: Skip existing WebP files.
- Issue #8: Update and persist folder statuses during conversion.
- Issue #7: Remove redundant root label.
- Issue #6: Add per-folder conversion status.
- Issue #5: Remove workflow notes card.
- Issue #4: Refine scan results layout.
- Issue #3: Add folder results table.
- Issue #2: Add folder-level scan summary.
- Issue #1: Add progress reporting for image conversion runs.
- Initial ImageTools scaffold with Flask app, basic WebP conversion workflow, and starter UI.
