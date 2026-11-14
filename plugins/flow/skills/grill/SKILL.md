---
name: grill
description: A research-backed, relentless interview to sharpen a feature, or to close the open questions of one or more sprints of a brainstorm layout. Researches first, interviews the developer, builds the project's glossary, and offers ADRs as decisions settle.
disable-model-invocation: true
---

## Unsupported hosts

If the active host is neither Claude Code nor Codex, tell the user this skill has no validated integration there and suggest opening a support ticket at https://github.com/tushar2708/claude-assets/issues/new.


## Strict SOP

Run a grilling session that is grounded in research, not just intuition. Do not skip a phase. Do not start writing or implementing anything until the developer confirms a shared understanding at the end. The files this session keeps current are the exception: `research-output.md` (written by the `research` skill), the glossary files, and, in layout mode, the layout and the specs it links.

The unit of work is the **feature** the developer wants to build or the decision they want to make, or, in layout mode, the **sprints** they chose. Everything below serves one goal: expose every hidden assumption before a line of code is written.

## Choose the mode

| Mode | When | Phases |
|------|------|--------|
| **Normal** | The developer names a feature or idea | Research, Interview, Converge |
| **Layout** | The developer names a brainstorm layout (a file named `brainstorm-NN-<slug>.md`), or the conversation already has one | Read the layout, Choose the scope, Research (optional), Interview, Converge |

If the developer names a layout, use layout mode. Otherwise use normal mode.

## Normal mode

### Phase 1 — Research

Call the Skill tool with `research`. Give it the feature in the developer's words. It maps the concepts in four domains, asks whether to research and which of the five research domains, researches, and saves `research-output.md` in a new spec folder `docs/specs/spec-NN-<use-case>/`. If its text is no longer in your context (for example after a compaction), call it again.

Continue only after it reports that `research-output.md` is saved and validated. Keep the concept list it gives you.

### Phase 2 — Interview

Call the Skill tool twice: first with `grilling`, then with `domain-design`. If the text of either skill is no longer in your context, call it again.

- `grilling` runs the interview, so ask no question yourself in this phase. Give it what this session built: the concepts from Phase 1, the research briefs, and the path of `research-output.md`.
- `domain-design` runs in its "Session mode". Tell it so. In that mode it adds six duties to the interview: challenge terms against the glossary, sharpen fuzzy words, test relationships with concrete scenarios, check the user's statements against the code, update the glossary as each term is resolved, and offer ADRs. Give it the concepts from Phase 1. It does not run the design procedure and writes no code.

If the scope turns out to be too big for one spec, `grilling` offers to promote the session to a brainstorm, and the developer can also ask for it at any time. It follows `../brainstorm/references/promote.md`: the research folder `docs/specs/spec-NN-<use-case>/` becomes `docs/specs/brainstorm-NN-<use-case>/`, the research and the decisions so far are kept, and the developer is asked to run `/flow:brainstorm` in the same conversation. In promotion mode it skips the research and the interview, which are already done, and writes a layout instead of a spec. The session then continues in layout mode, below, from the step "Choose the scope", or in a later session.

### Phase 3 — Converge

The `grilling` skill runs this phase: the summary, the developer's confirmation, and the offer of `/flow:spec`. The `domain-design` skill's Session mode adds the glossary changes, the settled scenarios, the contradictions found in the code, and the ADR topics to that summary. Add nothing of your own.

## Layout mode

A layout splits a large effort into sprints and holds every open question. This mode closes those questions for the sprints the developer chooses, and keeps the layout true while it does. Read `../brainstorm/references/layout-format.md` in full before the first step. It defines the sprint states, the question rules, and the revision rules that this mode follows.

### Step 1 — Read the layout

Read, in this order:

1. The layout file.
2. `research-output.md` in the layout's folder, and any other research file there.
3. The spec of every sprint that has one, linked in the Sprints table, finalized or not. They are the decisions already made.
4. The Open questions table, for every sprint, not only the chosen ones.

Write a short list in the chat: each sprint with its state, its dependencies, and the number of open questions.

### Step 2 — Choose the scope

Ask the developer which sprints to work on in this session. Use the question tool, with `multiSelect: true`, and no option pre-selected. Offer each sprint that is not `finalized` as an option: "Sprint N: <name>". In the description give its type, its state, its open question count, and what it depends on. Put first, with "(Recommended)", the first non-finalized sprint in dependency order. When there are more than four options, ask more than one question, with 2 to 4 options each.

If a chosen sprint depends on a sprint that still has open questions, say so in the chat, name those questions, and recommend including that sprint. The developer decides.

### Step 3 — Research (optional)

The layout's folder already holds the research from the brainstorm. Ask whether to research more for this scope. If the developer says yes, call the Skill tool with `research`, and give it the layout's folder as the folder and `research-sprint-<numbers>.md` as the file name, where `<numbers>` are the chosen sprint numbers joined by dashes. If the developer says no, go on.

### Step 4 — Interview

Call the Skill tool twice: first with `grilling`, then with `domain-design`, as in Phase 2 of normal mode. Give `grilling` the layout path, the chosen sprints, the open questions of those sprints, and the research files. Tell it that this is a layout session, so its "Layout document" rules apply. The aim of the interview:

- **Close the open questions** of the chosen sprints.
- **Surface new ones.** Add each to the layout at once, under the sprint that must settle it.
- **Keep the sprints consistent.** Before you accept a decision, read the specs and open questions of the sprints before and after it in the Sprint dependencies section. Use the `If it changes` line of each edge. If the decision contradicts a decision already made, follow the revision rules in the layout format.

### Step 5 — Converge

The `grilling` skill runs this step. When every chosen sprint has zero open questions, it offers `/flow:spec`, and `/flow:spec` asks how many sprints each spec should cover. When open questions remain, it lists them per sprint. They stay in the layout for a later session. Add nothing of your own.
