from pathlib import Path

from scripts import check_changelog_issues


def test_get_changelog_issue_numbers_extracts_issue_refs(tmp_path):
    changelog_path = tmp_path / "CHANGELOG.md"
    changelog_path.write_text("- First change (Issue #1).\n- Second change (Issue #11).\n", encoding="utf-8")

    original_path = check_changelog_issues.CHANGELOG_PATH
    check_changelog_issues.CHANGELOG_PATH = changelog_path
    try:
        assert check_changelog_issues.get_changelog_issue_numbers() == {"1", "11"}
    finally:
        check_changelog_issues.CHANGELOG_PATH = original_path


def test_main_fails_when_issues_are_missing(tmp_path, monkeypatch, capsys):
    changelog_path = tmp_path / "CHANGELOG.md"
    changelog_path.write_text("- First change (Issue #1).\n", encoding="utf-8")

    monkeypatch.setattr(check_changelog_issues, "CHANGELOG_PATH", changelog_path)
    monkeypatch.setattr(check_changelog_issues, "get_repo_issue_numbers", lambda: {"1", "2"})

    exit_code = check_changelog_issues.main()
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "#2" in captured.err
