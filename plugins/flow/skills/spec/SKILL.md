---
name: spec
description: Turn the current conversation into a governed spec saved as a numbered docs/plans/NN doc (docsmith plan frontmatter + validation) — no interview, just synthesis of what you've already discussed.
disable-model-invocation: true
---

## Unsupported hosts

If the active host is neither Claude Code nor Codex, tell the user this skill has no validated integration there and suggest opening a support ticket at https://github.com/tushar2708/claude-assets/issues/new.

This skill takes the current conversation context and codebase understanding and produces a spec. Do NOT interview the user — just synthesize what you already know.

## Process

> **MANDATORY: document authoring.** Delegate document writing to a configured document-author role when the host provides one; otherwise write the document directly from this skill's template. Re-run validation yourself; never accept an unverified green claim.

0. **Precondition.** Look for `.docsmith/config.json` walking up from the current directory. If it is absent, STOP: tell the user to run `/flow:init` and wait. Write no doc, index or folder before docsmith is scaffolded.

1. Explore the repo to understand the current state of the codebase, if you haven't already. Use the project's domain glossary vocabulary throughout the spec, and respect any ADRs in the area you're touching.

2. Sketch out the seams at which you're going to test the feature. Existing seams should be preferred to new ones. Use the highest seam possible. If new seams are needed, propose them at the highest point you can. The fewer seams across the codebase, the better - the ideal number is one.

Check with the user that these seams match their expectations.

3. Call the Skill tool with `plan-it` before writing the spec, then use its wave-model schema.
4. Stamp docsmith `plan`-category frontmatter and tags on the spec — `type: plan`, `status: draft`, and a `tags:` list that includes `plan` — then route authoring through the `flow:docsmith-doc-author` subagent (Task tool, `subagent_type: flow:docsmith-doc-author`) with validate-to-green — one dispatch per file. The agent saves the spec as a numbered `docs/plans/NN-slug.md` (NN = next-of-largest existing numeric prefix in that folder).
5. Have `flow:docsmith-doc-author` write the plan index too (one dispatch per file). If `docs/plans/INDEX.md` (or the project's equivalent index) does not exist, the agent creates it WITH docsmith frontmatter (`type: Reference` — confirm the alias in `.docsmith/config.json` `type_aliases`; `title`; `status: draft`; 2-4 kebab-case tags as a YAML block list; `stale_after` per the evergreen contract; `generated: {by, at}`), an H1, and the table header `| # | [Title](file) | Aim | Status | Notes |` with its rows, then adds the new row. If it exists, the agent appends the row, matching the existing row format `| # | [Title](file) | Aim | Status | Notes |` with Status `❌ Not Implemented`. Never hand-write the index in the main thread.
   After every `flow:docsmith-doc-author` hand-back, run `/humanizer` on each listed file (file mode, prose only), then re-run docsmith validate.
Do NOT publish to a tracker or apply a triage label yourself. Create issues only through `/flow:add-to-roadmap` in step 7.
6. **Verify (orchestrator, never delegated).** From the repo root run `uv run .docsmith/engine/docsmith.py validate` UNSCOPED (no `--paths`). It must print `FAILURES: 0`. Relay every WARN line to the user. If there are failures, re-dispatch `flow:docsmith-doc-author` with the exact findings; do not fix them yourself. Quote the validator output in your report.
7. **Offer task tracking.** Run only after step 6 prints `FAILURES: 0`. Ask through the active host's question mechanism.
   1. Ask: "Add this spec to task tracking?" Yes or no. On no, stop.
   2. Ask the epic: existing epic (ask its key or URL) or new epic.
   3. Ask the user to run `/flow:add-to-roadmap` now. Do not invoke it yourself; it is user-invoked only.
   4. Give the user the arguments to pass: spec path, spec title, epic choice, and the SF list.
   5. That skill creates one Story and one Subtask per `SF-<n>`, and writes their keys into the spec.
   6. Create no item or roadmap row yourself. Leave the `docs/plans/INDEX.md` row as is.

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

## Further Notes

Any further notes about the feature.

</spec-template>

Note on citations: `validate` treats any inline-code token that contains a `/` and has no file extension (or has a known code/doc extension) as a repo path and warns when it does not exist. Write external names (third-party packages, module names, GitHub repos, hostnames+paths) in *italics* instead of backticks; write env-var pseudo-paths as `$VAR/x`.
