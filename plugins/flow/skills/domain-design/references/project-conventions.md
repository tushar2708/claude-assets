# Project conventions for domain-design

Read this whole file in Step 0, before you choose a design. The skill sets the shape of the domain code. The project sets everything else: names, error style, file layout, lint rules, test style, and the interfaces that already exist. Find them first. Follow them.

## The rule

- The project's existing conventions win on every detail this skill does not set. That includes minor details such as error handling, naming, and lint preferences.
- Where a project convention conflicts with the seven laws, the collaborator rules, or a language file, do not pick a side. Stop and ask the user, in the form below.
- Do not decide against an existing pattern on your own. Make a suggestion. Wait for the answer.

**Form of the request.** Ask through the `grilling` skill, in this form:

> I see this pattern to do `<something>` in `<file:line>`. I believe I should do things differently for `<reason>`. Should I do it?

Include the options and your recommendation. If the user says no, follow the existing pattern.

## 1. Find the instruction files

Instruction files for agents and people sit in the repository. Some are loaded for you by the host. Others are not, so do not assume you have seen them. List them yourself, then read each one in full.

**Where to look.** Start at the repository root. Then go down, one folder at a time, to every folder that holds code you will change. Look in each folder.

| File or folder | What it is |
|---|---|
| `AGENTS.md`, `.claude/AGENTS.md` | Instructions for coding agents |
| `CLAUDE.md`, `.claude/CLAUDE.md` | Instructions for Claude Code |
| `CLAUDE.local.md` | One person's private instructions. Read it if it exists, and do not copy it into project files |
| `.claude/rules/*.md` (any depth) | Rules in Markdown, one topic per file. A file may start with a `paths` field that limits it to matching files |
| `CONTRIBUTING.md` | Contribution rules |
| `GLOSSARY.md`, `GLOSSARY-MAP.md` | The project's words. See `references/glossary-format.md` |
| `docs/`, and any folder of architecture decision records | Past decisions and the reasons for them |

Why you must look yourself:

- A `CLAUDE.md` in a subfolder is loaded only when a file in that folder is read.
- `AGENTS.md` is read by the host only when no `CLAUDE.md` exists in the working directory or above it. When both exist, read both.
- Rules with a `paths` field load only when matching files are touched.

Also look for any other file or folder of rules that the repository keeps for agents or contributors. Search for names that contain `rules`, `agents`, `conventions`, or `contributing`.

**Output of this part:** the list of files you found and read, with the rules from them that affect this feature. If a file contradicts another, write both and ask the user.

## 2. Find the lint, type-check, and style configuration

The new code must pass the project's own checks without changing them. Find which checks exist, and which commands run them. The files below are the ones to look for. The format is in the third column.

| Language | File names | Format | Read it for |
|---|---|---|---|
| Go | `.golangci.yml`, `.golangci.yaml`, `.golangci.toml`, `.golangci.json` | YAML, TOML, or JSON | Enabled linters, rules that restrict imports, size and complexity limits. golangci-lint looks in the current directory, then in every parent up to the root, then in the home directory |
| Go | `go.mod` | Go module-file syntax | Module path and Go version |
| Java | `pom.xml` | XML | Plugins that run style checks, static analysis, or architecture tests, and the paths of their configuration |
| Java | `build.gradle`, `build.gradle.kts` | Groovy script, Kotlin script | The same as above |
| Java | `.editorconfig` | INI-style text | Indentation, line endings, line length |
| Python | `mypy.ini`, `.mypy.ini` | INI, with a `[mypy]` section | Type-checking strictness, per-module overrides |
| Python | `pyproject.toml` | TOML, with `[tool.mypy]`, `[tool.pyright]`, `[tool.ruff]` tables | The same, and which tools the project uses |
| Python | `setup.cfg` | INI, with a `[mypy]` section | The same |
| Python | `pyrightconfig.json` | JSON | Type-checking strictness. It wins over `pyproject.toml` when both exist |
| Python | `.ruff.toml`, `ruff.toml` | TOML, with settings at the top level | Lint and format rules. Within one folder, `.ruff.toml` wins over `ruff.toml`, which wins over `pyproject.toml` |
| TypeScript | `tsconfig.json` | JSON | Compiler strictness, paths, which files are checked. The compiler searches from the current folder up through its parents. A `jsconfig.json` plays the same part in a JavaScript project |
| TypeScript | `eslint.config.js`, `.mjs`, `.cjs`, `.ts`, `.mts`, `.cts` | A JavaScript or TypeScript module | Lint rules, including rules that restrict imports. When several exist, ESLint uses them in that order. If the project has an older ESLint configuration format instead, read that |
| TypeScript | `package.json` | JSON | The `scripts` that run lint, type-check, and tests |
| Any | `.pre-commit-config.yaml` | YAML | The checks that run on commit |
| Any | `Makefile` | Make syntax | Targets for lint, type-check, test, and build |
| Any | CI workflow files, for example under `.github/workflows/` | YAML | The checks that must pass before merge |

How to read them:

- In a monorepo, the nearest configuration file to the code you change decides the rules for mypy, Ruff, and golangci-lint. They use the closest file and do not merge files. Look next to the code, then upward.
- If the project uses an import-rule tool that is not in the table, find it through the lint configuration, the `Makefile`, or the pre-commit file.
- Do not change a lint, type, or style configuration to make new code pass. Fix the code. If the configuration is the problem, ask the user in the form above.
- Section 5 of each language file says which of these checks enforce the skill's rules. Add a rule to the project's existing tool. Do not add a second tool for the same job without asking.

**Output of this part:** a list of the checks you found, and the command that runs each. Step 15 runs them.

## 3. Find the existing patterns

Before you design anything, find 2 or 3 existing examples in the codebase of how each of these is done. Search for them. Do not rely on memory or on what feels usual.

| Look for | Question to answer |
|---|---|
| A use case, service, or handler for a similar feature | How is one structured? What does it receive? What does it return? |
| An existing interface for the same need (a repository, a clock, an ID generator, a gateway) | Can I reuse it instead of adding a second one? |
| An adapter | How does it translate errors? Where does it live? |
| The place where adapters are created | Is there already a composition root? |
| Value objects, identifiers, and enumerations | How are they declared? Do the identifier types already exist? |
| Error handling | Which error types and wrapping style does the project use? |
| Tests | Table-driven or not? Where do fakes live? Is there a contract test? How are tests named? |
| Names | Which words does the glossary, or the existing code, use for this concept? |
| Folder layout | Where do the model, use cases, interfaces, and adapters live today? |

Rules:

- **Reuse before you create.** If an interface, a fake, a clock, or an ID generator already exists and does the job, use it. Add a new one only with a reason written in `design.md`.
- **Follow the existing words.** Use the glossary's words. If there is no glossary, use the words the code already uses, and write them into the glossary in Step 2.
- **Follow the existing layout and test style**, even when it differs from the layout in Step 14. Step 14 says "or the nearest equivalent that keeps the dependency rules". Keep the dependency rules. Keep the rest of the project's layout.
- **Existing code that breaks the skill's laws stays as it is** unless the user asked for a refactor. New code follows the skill. When new code must call old code, wrap the old code behind an interface (see "Refactor mode").
- When you see a pattern that is not obvious, tell the user. Offer to record it in the project's instruction file.

**Output of this part:** the "Project conventions" table in `design.md`:

| Topic | Existing example (`file:line`) | Rule I will follow | Differs from this skill? |
|---|---|---|---|
| Use-case shape | `internal/orders/confirm.go:20` | A struct with a `Run` method | No |
| Error wrapping | `internal/orders/errors.go:8` | Sentinel errors with `%w` | No |
| Clock | `internal/clock/clock.go:5` | Reuse the existing `Clock` | No |
| Fakes | `internal/orders/fakes_test.go:12` | Mocks generated per test | Yes. Asked the user: kept the project's mocks for this feature |

(The rows above show the shape of the table. They are not a real project.)

## 4. Gate

- You listed the instruction files from the root down to each changed folder, and read them.
- You found the lint, type-check, and style configuration, and the commands that run it.
- Every topic in the table in part 3 has 2 or 3 examples from the codebase, or a written note that the codebase has none.
- Every difference between the project and this skill is either resolved by following the project, or has the user's written answer.
