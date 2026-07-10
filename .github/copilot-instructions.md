# ImageTools repository instructions

## Workflow for code changes

For any user-requested code change, follow this order:

1. Create or confirm a GitHub issue for the work.
2. Update CHANGELOG.md under [Unreleased] with a bullet that references the issue number.
3. Implement the change and verify it with relevant tests.
4. Commit the change and include a closing footer such as: Closes #<issue>.

## Required conventions

- Keep the issue -> changelog -> commit flow intact for every meaningful change.
- Use one bullet per issue in the changelog, written issue-first.
- Prefer a red/green test cycle where practical.
- Verify changes with fresh test or command output before claiming success.
- If GitHub access, the terminal, or the required workflow tooling is blocked, stop and ask the user for help rather than skipping the workflow.
