# claude-assets

Claude Code plugins and skills.

## Install

Install every plugin and skill:

```sh
curl -fsSL https://raw.githubusercontent.com/tushar2708/claude-assets/main/install.sh | bash
```

Update everything:

```sh
curl -fsSL https://raw.githubusercontent.com/tushar2708/claude-assets/main/install.sh | bash -s -- update
```

Then restart Claude Code, or run `/reload-plugins`.

| Detail | Value |
|---|---|
| Needs | `git` and the `claude` CLI on `PATH`. |
| Clone path | `~/.claude-assets`. Set `CLAUDE_ASSETS_DIR` to change it. |
| Skills | Linked from `~/.claude/skills/<name>`. An existing folder is never overwritten. |
| Preview | Set `DRY_RUN=1` to print the steps only. |

## Skills

| Skill | What it does |
|---|---|
| [`real-browser-debug`](./skills/real-browser-debug) | Drives a real, logged-in Chrome session via Playwright to capture console output, network traffic, and screenshots for debugging. |
| [`progressive-web-app`](./skills/progressive-web-app) | Guides building and auditing a Progressive Web App (manifest, service worker, installability, responsive/Lighthouse checks) against a strict evidence-based checklist. |

## Plugins

| Plugin | What it does |
|---|---|
| [`react-atomic-aesthetics`](./plugins/react-atomic-aesthetics) | Atomic-design React/JSX UI plugin enforcing canonical UI/UX aesthetic and structure rules via a planning architect agent, an implementation agent, and plan/review skills. |
| [`docsmith`](./plugins/docsmith) | Deterministic documentation governance — write, validate, score, and site-build docs by category with evergreen rules. |
| [`react-seo-planner`](./plugins/react-seo-planner) | Plans and audits SEO (and GEO/AI-visibility) for React apps: checklist-driven categories, schema templates, GEO analysis scripts, and specialist GEO agents. |
| [`flow`](./plugins/flow) | Dev workflow: interview, spec, plan, tasks, implement, review, docs governance, and roadmap tracking. |

## Attribution

`flow:grilling` and the base of `flow:spec` come from Matt Pocock's [mattpocock/skills](https://github.com/mattpocock/skills) repo ("Skills for Real Engineers").

`flow:grill` extends Matt Pocock's `grilling` skill. It adds concept mapping, a research gate, and `AskUserQuestion` interviews.

Credit: [Matt Pocock](https://github.com/mattpocock), [mattpocock/skills](https://github.com/mattpocock/skills).
