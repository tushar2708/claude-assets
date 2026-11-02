---
name: update-pr
description: Review the current pull request and update its title and description with a synthesized Conventional Commit-style summary. Use only when explicitly invoked.
disable-model-invocation: true
---

# Update Pull Request

1. Determine the current branch and read the current PR. If none exists, report that and stop.
2. Review every commit between the PR base and `HEAD`; do not use only the latest commit.
3. Use a repository PR template when present. Otherwise produce a summary, grouped change categories, and a test plan that distinguishes verified from pending work.
4. Create a conventional-commit-style title for the overall change. Keep its description imperative, lowercase, and under 72 characters.
5. Show the proposed title and body, then update only after the user has approved it when approval is required by the host.
6. Write the body to a unique temporary file named `/tmp/pr_body_<repo>_<number>.md`, then update with `gh pr edit <number> --title <title> --body-file <file>`.

Never discard useful existing PR information when updating it. Do not include internal plan identifiers, phases, validation numbers, or AI-agent artifacts.
