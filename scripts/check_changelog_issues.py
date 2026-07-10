from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Set

CHANGELOG_PATH = Path(__file__).resolve().parents[1] / "CHANGELOG.md"


def get_changelog_issue_numbers() -> Set[str]:
    text = CHANGELOG_PATH.read_text(encoding="utf-8")
    return {match.group(1) for match in re.finditer(r"Issue\s*#(\d+)", text)}


def get_repo_issue_numbers() -> Set[str]:
    result = subprocess.run(
        ["gh", "issue", "list", "--state", "all", "--limit", "100", "--json", "number"],
        capture_output=True,
        text=True,
        check=True,
    )
    issues = result.stdout.strip()
    if not issues:
        return set()
    data = __import__("json").loads(issues)
    return {str(item["number"]) for item in data}


def main() -> int:
    changelog_issue_numbers = get_changelog_issue_numbers()
    repo_issue_numbers = get_repo_issue_numbers()

    missing = sorted(repo_issue_numbers - changelog_issue_numbers)
    if missing:
        print(f"Missing changelog entries for issue(s): {', '.join('#' + number for number in missing)}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
