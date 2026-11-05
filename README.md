# claude-assets

Portable skills and plugins for Claude Code and Codex.

## Claude Code

### Install/Update

Installs every plugin and standalone skill. Safe to run on a fresh machine or over an existing install.

```sh
curl -fsSL https://raw.githubusercontent.com/tushar2708/claude-assets/main/install.sh | bash -s -- --claude
```

Restart Claude Code or run `/reload-plugins` afterwards.

### Uninstall

Removes the plugins, the marketplace, and the skill links.

```sh
curl -fsSL https://raw.githubusercontent.com/tushar2708/claude-assets/main/install.sh | bash -s -- --claude uninstall
```

## Codex

### Install/Update

Installs every plugin and standalone skill. Safe to run on a fresh machine or over an existing install.

```sh
curl -fsSL https://raw.githubusercontent.com/tushar2708/claude-assets/main/install.sh | bash -s -- --codex
```

Start a new Codex session afterwards.

### Uninstall

Removes the plugins, the marketplace, and the skill links.

```sh
curl -fsSL https://raw.githubusercontent.com/tushar2708/claude-assets/main/install.sh | bash -s -- --codex uninstall
```

## Notes

- Uninstall keeps the local clone at `~/.claude-assets`. Delete that folder yourself if you no longer need it.
- Plugins carry no version number. Every commit is a new version, so re-run the installer to update in place.

| Detail | Value |
|---|---|
| Needs | `git` and the selected `claude` or `codex` CLI on `PATH`. |
| Clone path | `~/.claude-assets`. Set `CLAUDE_ASSETS_DIR` to change it. |
| Claude skills | Linked from `~/.claude/skills/<name>`. An existing folder is never overwritten. |
| Codex skills | Linked from `~/.codex/skills/<name>`. An existing folder is never overwritten. |
| Preview | Set `DRY_RUN=1` to print the steps only. |

## Plugins

Each plugin is listed in the marketplace and installed by the commands above. See the plugin's own README for usage.

### [`flow`](./plugins/flow)

A spec-driven development workflow: from an idea to reviewed code.

- **Workflow:** interview (`grill`), spec (`spec`), plan (`plan-it`), tasks (`make-tasks`), execution (`execute`), and review (`review`).
- **Roadmap and trackers:** `add-to-roadmap` and `sync-issues`, which keep `roadmap.md` in step with Jira, GitHub, Asana, or another tracker.
- **Documentation:** docsmith-governed docs (`docs`, `write-doc`, `write-adr`, `write-prd`, `update-docs`, `fix-findings`) and `explaining-code` for HTML walkthroughs.
- **Debugging and prototyping:** `diagnosing-bugs`, `prototype`, `explain-feature`, and `answer-properly`.
- **Planning and commits:** `create-n-day-plan`, `create-detailed-days`, `create-priming`, `commit`, `commit-no-verify`, and `update-pr`.
- **Sessions:** `handoff` compacts a conversation for the next agent.

### [`react-atomic-aesthetics`](./plugins/react-atomic-aesthetics)

Rules and agents for building React UI with a consistent look and atomic component structure.

- **Rules:** `ui-rulebook`, the canonical UI and UX rules that the other pieces follow.
- **Agents:** `architect` plans a UI change against the rules and the existing codebase. `implementer` builds it.
- **Skills:** `plan` (plan a UI change before coding) and `review` (review an existing or just-built UI).

### [`myhooks`](./plugins/myhooks)

Manages Claude Code hook rules.

- **Skills:** `setup` (install, verify, and test the hooks system), `add-update` (add or change a rule), and `enable-disable` (toggle one rule without touching the others).
- **Codex:** Codex has no hook adapter. In Codex, these skills explain that and offer a portable policy instead.

## Attribution

`flow:grilling` and the base of `flow:spec` come from Matt Pocock's [mattpocock/skills](https://github.com/mattpocock/skills) repo ("Skills for Real Engineers").

`flow:grill` extends Matt Pocock's `grilling` skill. It adds concept mapping, a research gate, and `AskUserQuestion` interviews.

Credit: [Matt Pocock](https://github.com/mattpocock), [mattpocock/skills](https://github.com/mattpocock/skills).
