# Config migrations

Each row is one rule for `ROOT/.docsmith/config.json`. The `update` skill checks every row against the project's file. A rule applies only when its "Outdated when" condition is true, so running the skill twice changes nothing the second time.

Add a row here for every release that changes a default which projects keep in their own `config.json`. Do not add a row for a change that the engine's loader already supplies.

## How to read the file

Read the raw `config.json`, not the effective configuration. The engine's loader merges the file over the shipped defaults: dictionaries merge key by key, and lists and values are replaced whole. This gives two cases:

- **A key that is absent from the file** already has the shipped value. Do nothing.
- **A key that is present in the file** keeps the project's value, even when the shipped default has changed. This is where a project goes out of date, and every row below is such a case.

A built-in category that is missing from the file needs no edit either, because its shipped default is merged in. Do not add one. If a built-in category is present in the file and differs from the shipped default (`DEFAULT_CATEGORIES` in `docsmith_lib/config.py` of the shipped engine), report it as "customized" and change nothing.

## Rules

| ID | Added for | Outdated when | Edit | Mode | What fails without it |
|---|---|---|---|---|---|
| M1 | Spec status `ready` | `frontmatter.allowed_statuses` is present and does not contain `ready` | Insert `"ready"` directly after `"draft"`. If the list has no `"draft"`, append `"ready"` at the end | Auto | A document with `status: ready` fails the frontmatter check |
| M2 | `ready` has the same drift leniency as `draft` | `validate.drift_skip_statuses` is present, contains `"draft"`, and does not contain `"ready"` | Insert `"ready"` directly after `"draft"` | Auto | A `ready` spec that names files not yet built gets drift warnings that a `draft` spec does not |
| M3 | Specs live under `docs/specs/` | `categories.plan.dir_patterns` contains `"docs/plans/**"`, or `categories.plan.archive_dir` is `"docs/plans/archive"` | Replace `"docs/plans/**"` with `"docs/specs/**"`, and `"docs/plans/archive"` with `"docs/specs/archive"` | Ask | The plan category governs a folder that no skill writes to, and the stale-plan check looks in the wrong archive |
| M4 | The category folders exist | The first static prefix of a category's first `dir_patterns` entry is not a folder in the project, for example `docs/specs` | Create the folder with an empty `.gitkeep` file | Auto | Nothing fails. The folder is where the skills save the documents of that category |
| M5 | The engine version is stamped | `engine_version` differs from `ENGINE_VERSION` in `docsmith_lib/__init__.py` of the shipped engine | Done by `scaffold --sync-engine` in the engine step. Do not edit it by hand | Auto | Nothing fails. The number only tells a reader which engine was last synced |

## What the modes mean

- **Auto:** the edit only adds a value or a folder. Apply it after the single confirmation for all additions.
- **Ask:** the edit changes a value the project already has. Show the old and the new value, and ask before each one.

## Notes on M3

M3 changes where the plan category is governed. It does not move any document. If `docs/plans/` exists and holds files, list them and tell the developer that the current layout is `docs/specs/spec-NN-<slug>/spec-NN-<slug>.md`. Do not move them.
