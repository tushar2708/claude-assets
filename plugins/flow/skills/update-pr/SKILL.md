---
name: update-pr
description: Review the current pull request and update its title and description with a synthesized Conventional Commit-style summary. Use only when explicitly invoked.
disable-model-invocation: true
---

# Update Pull Request

1. Determine the current branch and read the current PR. If none exists, report that and stop.
2. Find the last-updated marker at the body's end: `<!-- pr-updated-through: <sha> -->`.
3. Pick the commit range to analyze:
   - Marker present and `<sha>` is an ancestor of `HEAD`: analyze only `<sha>..HEAD`, the commits added since the last update, and merge them into the existing description.
   - No marker, or `<sha>` is not an ancestor (e.g. after a rebase): analyze every commit from the PR base to `HEAD`.
4. Use a repository PR template when present. Otherwise produce a summary, grouped change categories, and a test plan that distinguishes verified from pending work.
5. Create a conventional-commit-style title for the overall change. Keep its description imperative, lowercase, and under 72 characters.
6. Make the body's last line the marker with the current `HEAD` sha: `<!-- pr-updated-through: <full-sha> -->`. Keep exactly one marker; replace the old one, never duplicate it.
7. Show the proposed title and body, then update only after the user has approved it when approval is required by the host.
8. Write the body to a unique temporary file named `/tmp/pr_body_<repo>_<number>.md`, then update with `gh pr edit <number> --title <title> --body-file <file>`.

Never discard useful existing PR information when updating it. Do not include internal plan identifiers, phases, validation numbers, or AI-agent artifacts.
