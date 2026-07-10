from __future__ import annotations

import shutil
from pathlib import Path

SOURCE_ROOT = Path(r"C:\ImageToolsTest")
DEST_ROOT = Path(r"C:\ImageToolsTest_Copy")


def prepare_copy() -> Path:
    if DEST_ROOT.exists():
        shutil.rmtree(DEST_ROOT)
    shutil.copytree(SOURCE_ROOT, DEST_ROOT)
    return DEST_ROOT


if __name__ == "__main__":
    prepared = prepare_copy()
    print(prepared)
