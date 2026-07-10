# ImageTools implementation plan

## 1. Baseline review

- Review the VideoTools structure, Flask layout, and Bootstrap-oriented UI patterns.
- Reuse the same simple app-shell approach: a top bar, folder selection, status cards, and a main action area.

## 2. Initial scaffold

- Create a Python Flask app with a minimal home page.
- Add a converter module with folder scanning and WebP conversion logic.
- Add tests covering discovery and conversion behavior.

## 3. Core conversion workflow

- Accept a root folder from the UI.
- Recursively discover supported image files.
- Convert each image to WebP and write outputs into a `Converted.webp` folder under the source folder.
- Report counts, sizes, and any failures.

## 4. UX polish

- Show scan results and preview counts before conversion.
- Provide start/stop controls and clear status messaging.
- Keep the experience lightweight and practical, similar to the VideoTools UI.

## 5. Future enhancements

- Add quality/size presets.
- Add drag-and-drop or folder browser integration.
- Add a queue and progress stream for larger batch jobs.
- Support more formats and optional original-file deletion.
