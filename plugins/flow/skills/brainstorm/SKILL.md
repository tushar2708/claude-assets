---
name: brainstorm
description: Break a large idea into 3 or 4 sprints and save one layout file. The layout records the high-level design, how each sprint depends on the previous one, and every open question. Use when an idea is too big for one spec, when the user says "brainstorm" or asks to plan a multi-sprint effort, or when the user wants the shape of the work settled before writing specs. Later grill sessions close the open questions sprint by sprint. The developer runs it, including after a grilling session has been promoted because its scope grew.
disable-model-invocation: true
---

## Unsupported hosts

If the active host is neither Claude Code nor Codex, tell the user this skill has no validated integration there and suggest opening a support ticket at https://github.com/tushar2708/claude-assets/issues/new.

# Brainstorm

Use this skill for an idea that is too big to settle in one spec. It researches the idea, interviews the user at a high level, splits the work into 3 or 4 sprints, and saves one file, the **layout**. The layout is the map of the whole effort. Later `/flow:grill` sessions work through it one sprint at a time and turn each sprint into a spec.

This skill plans the shape of the work. It does not decide the details, and it writes no spec and no code. The only files it writes besides the research and the layout are the project's glossary files, which it keeps current as terms are resolved. Deciding details now would be eager: the answers would rest on facts nobody has yet, and later sprints would overturn them. This skill parks each detail as an open question on the sprint that must settle it.

## Promotion mode

When a grilling session is promoted because its scope grew, the `grilling` skill follows Part A of `references/promote.md` and then asks the developer to run this skill. This skill runs only when the developer invokes it, so `grilling` never calls it. If you find that the conversation already holds that material (the feature, the renamed folder, the decisions already made, the questions not yet settled, and the concepts), you are in promotion mode. In that case:

- **Skip Phase 1 and Phase 2.** Their work is already done: the research is saved in the folder, and the interview produced the decisions and the questions you were handed. Do not run `research` again, do not interview the developer, and do not create the folder.
- **Read `references/promote.md`, Part B**, and run Phases 3, 4 and 5 below with the differences it lists.
- Treat Phases 1 and 2 as done for every rule in this file, including "Do not propose sprints before Phase 2 ends".

Read `references/layout-format.md` in full before Phase 4. It defines the layout's sprint states, question rules, revision rules, and where the files live.

## Terms

| Term | Meaning | Example |
|---|---|---|
| **Layout** | The one file that holds the shape of the effort | `brainstorm-03-notifications.md` |
| **Sprint** | One chunk of the effort that a person can finish and check. Its type is research, POC, or implementation | "Sprint 2: POC of the delivery queue" |
| **Open question** | A decision in scope that is not yet made. It belongs to one sprint | "Q-4: Do failed messages retry, and how often?" |
| **Finalized** | A sprint with zero open questions and a ready spec | |

## Strict SOP

Move through five phases in order. Do not skip a phase. Do not propose sprints before Phase 2 ends. Do not write the layout before the user confirms the sprints in Phase 3.

Ask every question through the host's question tool, as the `grilling` skill's "Asking questions" section says. Before each set of questions, explain each one in the chat: what it is about and why it matters. Put your recommended option first.

## Phase 1 — Research

1. **Precondition.** Look for `.docsmith/config.json`, walking up from the current directory. If it is absent, STOP: tell the user to run `/flow:init` and wait. Write no file or folder before docsmith is set up.
2. **Pick the folder.** The layout's folder is `docs/specs/brainstorm-NN-<slug>/`. Work out `NN` with the rule in `references/layout-format.md`. `<slug>` is a kebab-case name for the idea. Do not create the folder yet: the research step creates it when it saves its file.
3. **Call the Skill tool with `research`.** Give it the idea in the user's words and the folder from step 2. It maps the concepts, asks the user whether to research and which domains, researches, and saves `research-output.md` in that folder. If its text is no longer in your context, call it again.
4. Continue only after `research-output.md` is saved and validated.

## Phase 2 — Interview at a high level

Call the Skill tool twice: first with `grilling`, then with `domain-design`. If the text of either skill is no longer in your context, call it again.

- `grilling` runs the interview. Give it the concept list and research from Phase 1, and the rules below.
- `domain-design` runs in its "Session mode". Tell it so. In that mode it adds six duties to the interview: challenge terms against the glossary, sharpen fuzzy words, test relationships with concrete scenarios, check the user's statements against the code, update the glossary as each term is resolved, and offer ADRs. It does not run the design procedure and writes no code. The glossary files are the one thing this skill writes before the layout.

The interview is **breadth-first**. Its aim is to see the whole effort, not to settle any one part. Settle these six topics, and no more:

1. **Goal.** What the effort is for, and the outcome that shows it worked.
2. **Scope.** What is in, and what is out.
3. **Constraints.** Deadlines, technology, budget, rules the work must obey.
4. **Main parts.** The big pieces, and the boundaries between them.
5. **Biggest unknowns.** The facts or decisions that the rest of the work hangs on.
6. **Ordering.** What must come before what, and why.

Rules:

- **Do not settle details.** When a question needs depth ("how exactly does X work?"), do not ask it now. Write it down as a **parked question** with the sprint it will probably belong to. A parked question becomes an open question in the layout.
- **Do not ask facts you can find.** Look in the codebase and the research first, as the `grilling` skill says.
- The interview ends when each of the six topics has an answer, or has been parked.

## Phase 3 — Choose the shape

1. **Draft the sprints.** Follow the sprint rules in `references/layout-format.md`: 3 or 4 sprints, in dependency order. For each sprint, write its name, type, goal (one sentence), exit criteria (what a person can check to say it is done), and what it depends on.
   - Put a research or POC sprint first when later sprints depend on a fact nobody has yet.
   - Write each dependency edge as two lines: what the earlier sprint passes on, and what in the later sprint must be re-checked if that changes. If you cannot write both lines, the sprints do not depend on each other. Remove the edge.
   - Put each parked question on the sprint that must settle it.
2. **Show the user the sprints** as a table in the chat, with the dependency lines under it. Explain the order.
3. **Ask the user.** One question with these options, recommended first:
   - "Use these sprints (Recommended)"
   - "Change them": the user says what to change in the Other field. Apply it, show the table again, and ask again.
   - "Too small to split: go to `/flow:grill`": stop here. Write no layout. Tell the user that the research is saved in the folder and `/flow:grill` can use it.
4. **Check for an architecture change.** Read the section of `../write-adr/SKILL.md` that says when to discuss an ADR. If the idea contains a major architecture change that meets one of its criteria, ask the user whether they also want an ADR. If they say yes, note the topic. Phase 5 tells them to run `/flow:write-adr`, because that skill runs only when the user invokes it. If no criterion is met, do not ask. If `domain-design` already offered an ADR for the same topic during the interview, do not ask again.

## Phase 4 — Write the layout

1. **Write the file.** By default, use the `flow:docsmith-doc-author` agent, once, with category `brainstorm`. If that agent is not available in the host, or the user prefers another way, write the file yourself from the `brainstorm` template. Either way, the file is `docs/specs/brainstorm-NN-<slug>/brainstorm-NN-<slug>.md`, with `type: brainstorm` and `status: draft`, and it must validate to green. Give the writer these, one section each:
   - **Goal and scope:** topics 1 and 2 from Phase 2.
   - **High-level design:** topic 4 and any decision the interview made. Each point ends with its source: a research finding ID, or "interview".
   - **Sprints:** the confirmed table. Every `Status` is `proposed` and every `Spec` is `none`.
   - **Sprint dependencies:** the two lines of each edge.
   - **Open questions:** every parked question, with an ID, its sprint, why it matters, status `Open`, and an empty Decision. Add the unknowns from topic 5 and the constraints that raise a question.
   - **Revisions:** the header row only.
   - **References:** the research file.
2. **Verify.** After the file is written, run `/humanizer` on it (file mode, prose only). From the repo root, run `uv run .docsmith/engine/docsmith.py validate` unscoped, with no `--paths`. It must print `FAILURES: 0`. Relay every WARN line to the user. If there are failures and you used `flow:docsmith-doc-author`, send it the exact findings again. Do not fix them yourself. If you wrote the file yourself, fix the findings and validate again.
3. **Check the layout** against the table below. Fix every failure.

| # | Check | Failure looks like |
|---|---|---|
| L1 | The layout has 3 or 4 sprints | 2 sprints, or 6 |
| L2 | Every sprint has an exit criterion that a person can check | "Done when it works" |
| L3 | Every dependency edge has both lines | An edge with only "Passes on" |
| L4 | Every open question has an ID, a sprint, and a "Why it matters" | A question under no sprint |
| L5 | The high-level design stays above sprint level | Class names, schemas, endpoint paths |
| L6 | Every point in the high-level design has a source | A bullet with no source |
| L7 | `research-output.md` is in the same folder | The research saved elsewhere |

## Phase 5 — Converge

1. Summarise for the user: the goal, the sprints in order with their type and goal, what each sprint passes to the next, the number of open questions per sprint, the glossary files you created or changed, and the ADR topics the user wanted, from this skill and from `domain-design`.
2. Give the path of the layout.
3. If the user wanted an ADR, tell them to run `/flow:write-adr` with the topic. Do not run it yourself.
4. Tell the user the next step: run `/flow:grill` on the layout, for one sprint or for several, to close their open questions and write their specs.
5. Write nothing more. The sprints are decided only to the level of this layout.
