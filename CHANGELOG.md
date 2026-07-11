# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

- Issue #48: Fix real-time conversion stats (converted/skipped counts) not updating in the header cards during processing.
- Issue #47: Align summary card groups with the vertical columns of the main dashboard layout for better visual continuity.
- Issue #46: Reorganize summary cards into "Source" (Folder Stats) and "Results" (Conversion Progress) groups for better visual hierarchy.
- Issue #45: Add a new summary card for Folder count and Total images size to the dashboard header.
- Issue #44: Fix hidden overflow cropping on the dashboard row that was clipping card bottom borders regardless of content height.
- Issue #43: Remove footer to eliminate card bottom clipping caused by overflow constraints in the fixed-height layout.
- Issue #42: Fix card clipping issue by removing fixed-top navbar and allowing flexbox to naturally manage viewport height without padding offsets.
- Issue #41: Apply a strict maxHeight to the results-scroll container to ensure the table is always self-contained and never pushes outside the card or overlaps the footer.
- Issue #40: Fix CSS stacking and height constraints to ensure the results card is always clipped by its container and never overlaps the footer.
- Issue #39: Enforce strict height constraints and overflow rules on dashboard layout to prevent results card from overlapping the footer.
- Issue #38: Fix dashboard layout to prevent scan results from overlapping the footer by properly using flexbox margins and layout constraints.
- Issue #37: Restructure scan results UI and CSS to ensure the table scrolls vertically within the card and does not overlap the footer.
- Issue #36: Align navbar brand to the left and settings/status to the right using a fluid layout to match VideoTools.
- Issue #35: Relocate the control disclaimer text to the Controls card header.
- Issue #34: Move scan result summary text to the card header for better space utilization.
- Issue #33: Widen scan results table to eliminate horizontal scroll and adjust height to fill the card.
- Issue #32: Implement a two-column dashboard layout, moving Scan results to a dedicated right-hand panel.
- Issue #31: Move the conversion control disclaimer text into the card header to save space.
- Issue #30: Remove the example placeholder text from the root folder input.
- Issue #29: Move Quality setting to a new Settings dialog and rename the configuration card header.
- Issue #28: Relocate convert button to the controls card as the primary action.
- Issue #27: Move controls card below the browse configuration card for a more logical workflow.
- Issue #26: Replicate VideoTools card header style across all cards in the UI.
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
