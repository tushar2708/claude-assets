# my-skills

A collection of custom Claude Code skills.

## Skills

| Skill | What it does |
|---|---|
| [`to-spec`](./skills/to-spec) | Turns the current conversation into a spec and publishes it to the project issue tracker, without re-interviewing the user. |
| [`grilling`](./skills/grilling) | Interviews the user relentlessly about a plan, decision, or idea until every open question is settled, using a "design tree" / "frontier" round-by-round model. |
| [`grill-me`](./skills/grill-me) | A research-backed, multi-phase interview for sharpening a feature: maps its business/product/UX/technical concepts, researches industry best practices and pitfalls for each, then interrogates the developer with the `AskUserQuestion` tool until reaching a shared understanding. Hands off to `/to-spec` at the end. |
| [`real-browser-debug`](./skills/real-browser-debug) | Drives a real, logged-in Chrome session via Playwright to capture console output, network traffic, and screenshots for debugging. |
| [`progressive-web-app`](./skills/progressive-web-app) | Guides building and auditing a Progressive Web App (manifest, service worker, installability, responsive/Lighthouse checks) against a strict evidence-based checklist. |

## Plugins

| Plugin | What it does |
|---|---|
| [`react-atomic-aesthetics`](./plugins/react-atomic-aesthetics) | Atomic-design React/JSX UI plugin enforcing canonical UI/UX aesthetic and structure rules via a planning architect agent, an implementation agent, and plan/review skills. |
| [`docsmith`](./plugins/docsmith) | Deterministic documentation governance — write, validate, score, and site-build docs by category with evergreen rules. |
| [`react-seo-planner`](./plugins/react-seo-planner) | Plans and audits SEO (and GEO/AI-visibility) for React apps: checklist-driven categories, schema templates, GEO analysis scripts, and specialist GEO agents. |

## Attribution

`to-spec` and `grilling` are copies of skills from Matt Pocock's [mattpocock/skills](https://github.com/mattpocock/skills) repo ("Skills for Real Engineers"), used as-is with only trivial wording/punctuation differences.

`grill-me` is an original, bespoke skill built as an **extension of Matt Pocock's `grilling` skill** from the same repo. It reuses `grilling`'s core "design tree" / "frontier" interview model, but adds a research-backed multi-phase process (concept mapping across business/product/UX/technical domains, a mandatory research gate, web research against curated sources, and question generation via the `AskUserQuestion` tool) not present in Matt Pocock's own `grill-me` shim, and hands its output to `/to-spec`.

Credit: [Matt Pocock](https://github.com/mattpocock), [mattpocock/skills](https://github.com/mattpocock/skills).
