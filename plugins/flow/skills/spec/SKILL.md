---
name: spec
description: Turn the current conversation into a governed spec saved in its own numbered docs/specs/spec-NN-<use-case> folder, or inside a brainstorm folder as spec-NN-MM-<use-case> when it covers sprints of a layout (docsmith plan frontmatter + validation). Reminds the developer of open items and keeps the spec at draft until they are decided. No interview, just synthesis of what you've already discussed.
disable-model-invocation: true
---

## Unsupported hosts

If the active host is neither Claude Code nor Codex, tell the user this skill has no validated integration there and suggest opening a support ticket at https://github.com/tushar2708/claude-assets/issues/new.

This skill takes the current conversation context and codebase understanding and produces a spec. Do NOT interview the user — just synthesize what you already know. The only questions it asks are the ones in "Open items" and "When the session has a brainstorm layout", and the ones in the steps below.

## Open items

A spec is complete only when every open item in it is decided. An open item is a decision that the conversation, or the layout in a brainstorm session, has not settled.

1. **List them before you write.** In a brainstorm session, they are the `Open` rows of the covered sprints in the layout. Otherwise they are the decisions this conversation left undecided: questions asked and not answered, and anything marked "maybe" or "to be decided".
2. **Remind the developer.** If there are any, list each one in the chat and say why it matters. Then ask through the host's question tool, with two options:
   - "Grill the open items first (Recommended)": stop, and tell the developer to run `/flow:grill`. In a brainstorm session, give the layout path.
   - "Write the spec as a draft with the open items listed": go on.
3. **Record them.** The spec lists every open item in its `Open Questions` section, with status `Open`. Its status is `draft`. A spec with an `Open` row never gets the status `ready`.

## When the session has a brainstorm layout

The session has a layout when the developer named one, or `/flow:grill` ran in layout mode in this conversation. Read the layout and `../brainstorm/references/layout-format.md` in full before anything else. Then:

1. **Ask which sprints to cover.** One question with `multiSelect: true` and no option pre-selected. Offer each sprint that no `ready` spec covers yet, as "Sprint N: <name>", with its state and its open question count in the description. Put first, with "(Recommended)", the first such sprint in dependency order. When there are more than four options, ask more than one question, with 2 to 4 options each.
2. **Ask how many specs.** When the developer chose more than one sprint, ask one question: "One spec per sprint (Recommended)", "One spec for all the chosen sprints", or "Another grouping", where the developer writes the groups in the Other field, for example "1 and 2 together, 3 alone". Each group becomes one spec. A group may hold several sprints. A sprint is never split across specs.
3. **Check the open items** of each group, as in "Open items".
4. **Use the layout's path.** Each spec is saved as `<layout folder>/spec-NN-MM-<use-case>/spec-NN-MM-<use-case>.md`. `NN` is the number in the layout folder's name. `MM` is the next one-indexed, 2-digit number among the `spec-NN-*` folders already in the layout folder. Write one spec per group, in order.
5. **Write from the layout.** Put the line `Covers sprint <numbers> of [<layout title>](<layout path>)` directly under the title. Use the resolved decisions in the layout and the specs of the other sprints. A spec must not contradict a decision that another spec records. If you find a contradiction, stop and tell the developer that the decision needs a revision in a grill session.
6. **Fit the sprint type.** For a research or POC sprint, use the same template. The Problem Statement is what is unknown. The Solution is how the sprint finds out. The Sub-features are the pieces of work. The Done-when of the last sub-feature is the sprint's exit criterion from the layout. Out of Scope lists what the sprint must not build.

## Process

> **MANDATORY: document authoring.** Delegate document writing to a configured document-author role when the host provides one; otherwise write the document directly from this skill's template. Re-run validation yourself; never accept an unverified green claim.

0. **Precondition.** Look for `.docsmith/config.json` walking up from the current directory. If it is absent, STOP: tell the user to run `/flow:init` and wait. Write no doc, index or folder before docsmith is scaffolded.

1. Explore the repo to understand the current state of the codebase, if you haven't already. Use the project's domain glossary vocabulary throughout the spec, and respect any ADRs in the area you're touching.

2. Sketch out the seams at which you're going to test the feature. Existing seams should be preferred to new ones. Use the highest seam possible. If new seams are needed, propose them at the highest point you can. The fewer seams across the codebase, the better - the ideal number is one.

Check with the user that these seams match their expectations.

3. Use the references/wave-model.md from the `plan-it` skill before writing the spec. (Read the file from the skill. Do not try to invoke it. It will be blocked. )
4. Stamp docsmith `plan`-category frontmatter and tags on the spec — `type: plan`, `status: draft`, and a `tags:` list that includes `plan` — then route authoring through the `flow:docsmith-doc-author` subagent (Task tool, `subagent_type: flow:docsmith-doc-author`) with validate-to-green — one dispatch per file. The agent saves the spec as `docs/specs/spec-NN-<use-case>/spec-NN-<use-case>.md` (NN = next-of-largest existing numeric prefix among the folders named `spec-<NN>-*` or `brainstorm-<NN>-*` directly in `docs/specs/`; `<use-case>` = kebab-case slug of the feature). If `/flow:grill` already created the spec folder for this feature in this conversation (the folder that holds `research-output.md`), pass that folder to the agent and write the spec into it. Otherwise the agent creates the folder. In a brainstorm session, use the path in "When the session has a brainstorm layout" instead.
5. Have `flow:docsmith-doc-author` write the plan index too (one dispatch per file). If `docs/specs/INDEX.md` (or the project's equivalent index) does not exist, the agent creates it WITH docsmith frontmatter (`type: Reference` — confirm the alias in `.docsmith/config.json` `type_aliases`; `title`; `status: draft`; 2-4 kebab-case tags as a YAML block list; `stale_after` per the evergreen contract; `generated: {by, at}`), an H1, and the table header `| # | [Title](file) | Aim | Status | Notes |` with its rows, then adds the new row. If it exists, the agent appends the row, matching the existing row format `| # | [Title](file) | Aim | Status | Notes |` with Status `❌ Not Implemented`. In a brainstorm session, write `Sprint <numbers> of <layout folder name>` in the Notes cell. Never hand-write the index in the main thread.
   After every `flow:docsmith-doc-author` hand-back, run `/humanizer` on each listed file (file mode, prose only), then re-run docsmith validate.
Do NOT publish to a tracker or apply a triage label yourself. Create issues only through `/flow:add-to-roadmap` in step 7.
6. **Verify (orchestrator, never delegated).** From the repo root run `uv run .docsmith/engine/docsmith.py validate` UNSCOPED (no `--paths`). It must print `FAILURES: 0`. Relay every WARN line to the user. If there are failures, re-dispatch `flow:docsmith-doc-author` with the exact findings; do not fix them yourself. Quote the validator output in your report.
6a. **Mark ready.** Run after step 6 prints `FAILURES: 0`, for each spec. If its `Open Questions` section has no `Open` row, ask through the host's question tool: "Mark this spec ready?" with "Yes" and "No, keep it as draft". On yes, dispatch `flow:docsmith-doc-author` to set `status: ready`, then run step 6 again. A spec never becomes `ready` without the developer's yes. If any `Open` row remains, leave it at `draft`, and tell the developer that `plan-it`, `make-tasks` and `execute` will remind them of the open items.
6b. **Update the layout.** Only in a brainstorm session. Dispatch `flow:docsmith-doc-author` once for the layout, and run `/humanizer` and step 6 after it. Tell it to make these changes, and no others:
   - In the Spec column of each covered sprint, add a link to the spec.
   - In References, add the spec.
   - End the Decision cell of every `Resolved` question of the covered sprints with a link to the spec.
   - Set a covered sprint that is `proposed` to `grilling`. Set a covered sprint to `finalized` when it has no `Open` question and every spec that covers it is `ready`.
   - When every sprint is `finalized` and no question is `Open`, set the layout's `status` to `stable`.
7. **Offer task tracking.** Run only after steps 6, 6a and 6b are done. Ask through the active host's question mechanism.
   1. Ask: "Add this spec to task tracking?" Yes or no. On no, stop.
   2. Ask the epic: existing epic (ask its key or URL) or new epic.
   3. Ask the user to run `/flow:add-to-roadmap` now. Do not invoke it yourself; it is user-invoked only.
   4. Give the user the arguments to pass: spec path, spec title, epic choice, and the SF list.
   5. That skill creates one Story and one Subtask per `SF-<n>`, and writes their keys into the spec.
   6. Create no item or roadmap row yourself. Leave the `docs/specs/INDEX.md` row as is.

<spec-template>

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A LONG, numbered list of user stories. Each user story should be in the format of:

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

This list of user stories should be extremely extensive and cover all aspects of the feature.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include specific file paths or code snippets. They may end up being outdated very quickly.

Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it within the relevant decision and note briefly that it came from a prototype. Trim to the decision-rich parts — not a working demo, just the important bits.

## Sub-features

An ordered list. Each item has:

- `SF-<n>` and name
- Behavior
- User stories covered
- Depends on (earlier SF only)
- Done-when
- Tracker key (left empty; `/flow:add-to-roadmap` fills it)

Start the section with a `Tracker Story:` line, left empty. `/flow:add-to-roadmap` fills it.
No file paths. Each sub-feature becomes one wave in `/flow:plan-it`.

## Testing Decisions

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- Which modules will be tested
- Prior art for the tests (i.e. similar types of tests in the codebase)

## Out of Scope

A description of the things that are out of scope for this spec.

## Open Questions

A table of the items that are not yet decided. One row per item. Resolved rows stay in the table, so the decision is on record. When a spec is written from a layout, reuse the layout's question IDs. Otherwise number the rows `Q-1`, `Q-2`, and so on. Leave only the header row when nothing is open.

| ID | Question | Status | Decision |
|----|----------|--------|----------|
| Q-1 | <Question> | Open | |

## Further Notes

Any further notes about the feature.

</spec-template>

Note on citations: `validate` treats any inline-code token that contains a `/` and has no file extension (or has a known code/doc extension) as a repo path and warns when it does not exist. Write external names (third-party packages, module names, GitHub repos, hostnames+paths) in *italics* instead of backticks; write env-var pseudo-paths as `$VAR/x`.
