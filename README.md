# claude-assets

Portable skills and plugins for Claude Code and Codex.

## Claude Code

### Install

Install every plugin and standalone skill:

```sh
curl -fsSL https://raw.githubusercontent.com/tushar2708/claude-assets/main/install.sh | bash -s -- --claude
```

Restart Claude Code or run `/reload-plugins` afterwards.

### Update

```sh
curl -fsSL https://raw.githubusercontent.com/tushar2708/claude-assets/main/install.sh | bash -s -- --claude update
```

### Uninstall

Removes the plugins, the marketplace, and the skill links.

```sh
curl -fsSL https://raw.githubusercontent.com/tushar2708/claude-assets/main/install.sh | bash -s -- --claude uninstall
```

## Codex

### Install

Install every plugin and standalone skill:

```sh
curl -fsSL https://raw.githubusercontent.com/tushar2708/claude-assets/main/install.sh | bash -s -- --codex
```

Start a new Codex session afterwards.

### Update

```sh
curl -fsSL https://raw.githubusercontent.com/tushar2708/claude-assets/main/install.sh | bash -s -- --codex update
```

### Uninstall

Removes the plugins, the marketplace, and the skill links.

```sh
curl -fsSL https://raw.githubusercontent.com/tushar2708/claude-assets/main/install.sh | bash -s -- --codex uninstall
```

## Notes

- Uninstall keeps the local clone at `~/.claude-assets`. Delete that folder yourself if you no longer need it.

| Detail | Value |
|---|---|
| Needs | `git` and the selected `claude` or `codex` CLI on `PATH`. |
| Clone path | `~/.claude-assets`. Set `CLAUDE_ASSETS_DIR` to change it. |
| Claude skills | Linked from `~/.claude/skills/<name>`. An existing folder is never overwritten. |
| Codex skills | Linked from `~/.codex/skills/<name>`. An existing folder is never overwritten. |
| Preview | Set `DRY_RUN=1` to print the steps only. |

## Skills

| Skill | What it does |
|---|---|

## Plugins

| Plugin | What it does |
|---|---|
| [`react-atomic-aesthetics`](./plugins/react-atomic-aesthetics) | Atomic-design React/JSX UI plugin enforcing canonical UI/UX aesthetic and structure rules via a planning architect agent, an implementation agent, and plan/review skills. |
| [`flow`](./plugins/flow) | Dev workflow: interview, spec, plan, tasks, implement, review, docs governance, and roadmap tracking. |

## Attribution

`flow:grilling` and the base of `flow:spec` come from Matt Pocock's [mattpocock/skills](https://github.com/mattpocock/skills) repo ("Skills for Real Engineers").

`flow:grill` extends Matt Pocock's `grilling` skill. It adds concept mapping, a research gate, and `AskUserQuestion` interviews.

Credit: [Matt Pocock](https://github.com/mattpocock), [mattpocock/skills](https://github.com/mattpocock/skills).
