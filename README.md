# ImageTools

A small Flask-based image conversion app inspired by the workflow and UI style of the VideoTools project.

## Goals

- Browse a root folder from the UI.
- Scan recursively for image files.
- Convert supported images to WebP.
- Keep output in a safe per-folder `Converted.webp` directory.

## Initial plan

See [docs/implementation-plan.md](docs/implementation-plan.md) for the implementation roadmap.

## Working conventions

- Create a GitHub issue for each significant change.
- Record the issue number in the changelog entry for that change.
- Follow the issue -> changelog -> commit flow for incremental work.
- Prefer a red test first approach where practical, especially for new behavior or bug fixes.

## Quick start

```powershell
cd C:\ImageTools
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5002
