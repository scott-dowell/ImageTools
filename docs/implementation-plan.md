# ImageTools implementation plan

## Working convention

- Create a GitHub issue for each significant implementation step.
- Add a changelog entry for each completed change, including the issue number.
- Keep the implementation work incremental and verified in the browser with relevant tests.

## Recommended implementation order

1. Baseline review
   - Review the VideoTools structure, Flask layout, and Bootstrap-oriented UI patterns.
   - Reuse the same simple app-shell approach: a top bar, folder selection, status cards, and a main action area.

2. Initial scaffold
   - Create a Python Flask app with a minimal home page.
   - Add a converter module with folder scanning and WebP conversion logic.
   - Add tests covering discovery and conversion behavior.

3. Core conversion workflow
   - Accept a root folder from the UI.
   - Recursively discover supported image files.
   - Convert any non-WebP image to WebP in place, replacing the original file after successful conversion.
   - Preserve a clear success/failure outcome for each file and report counts and any failures.
   - Treat WebP as the target format and avoid creating extra output folders unless a future workflow explicitly requires it.
   - Skip animated GIFs by default, since they are a special case and should not be converted through the standard workflow.
   - Keep the process stateless for now: no database or history tracking is required for the initial experience.

4. UX polish
   - Use a fresh copy of a real sample-image folder for browser verification so the UI can be exercised against actual files before each significant change.
   - The current browser validation flow is: run the fixture copy script, scan and convert the copied folder in the browser, and confirm that the converted files appear under the copied folder's Converted.webp output directory.

5. Progress and status tracking
   - Show scan results and preview counts before conversion.
   - Provide start/stop controls and clear status messaging.
   - Keep the experience lightweight and practical, similar to the VideoTools UI.
   - Confirm success of each conversion before deleting the original file.

5. Progress and status tracking
   - Track progress at two levels: folder progress and overall run progress.
   - Maintain a simple run state object with fields such as state, root path, discovered folder count, discovered image count, processed folder count, processed image count, skipped count, failed count, current folder, current file, overall progress percent, started at time, and estimated time remaining.
   - Show a progress bar for the current run plus a smaller folder-level indicator so large deep trees are easy to follow.
   - Report the current folder and current file in the UI while work is running, similar to the VideoTools approach.
   - Separate the workflow into phases such as scanning, converting, and finalizing so the UI feels responsive during long runs.
   - Use a lightweight polling endpoint or server-sent events for updates rather than forcing the user to refresh manually.
   - Keep the initial implementation simple and stateless, but make the run state easy to expose to the UI so it can be expanded later with pause/stop controls.
   - Add support for pause, resume, soft stop, and hard stop controls in a later iteration, mirroring the VideoTools approach so long-running folder trees can be controlled safely.

6. Folder and batch visibility enhancements
   - Add a folder grid view that shows each folder, the number of images discovered in it, and its current progress with a progress bar for the active folder.
   - Add quick folder actions such as copying the folder path and opening the folder in Windows Explorer.
   - Consider a lightweight preview experience for files in a selected folder, while keeping it optional so the app does not become overly complex.
   - Add a cleanup pre-step for previously converted image folders that detects legacy subfolders such as converted or converted.webp, moves the WebP files up one level, and removes the now-empty subfolder structure.
   - Report per-image and per-folder savings as well as conversion timings so the user can understand the impact of the batch run.

7. Later-phase refinements
   - Add drag-and-drop or folder browser integration.
   - Revisit whether a small local database is needed for tracking large runs, history, or resumability.
