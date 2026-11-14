# Promote a grilling session to a brainstorm

A grilling session can outgrow one spec. This file says how to turn the session in progress into a brainstorm: the research is kept, the decisions already made are kept, and a layout is written instead of a spec. The developer then continues, sprint by sprint, in the same session or in a later one.

The file has two parts:

- **Part A** is run by the `grilling` skill, in the session that is being promoted. It ends by asking the developer to run `/flow:brainstorm`.
- **Part B** is run by the `brainstorm` skill, which the developer runs in the same conversation. It finds the material from Part A there and runs in promotion mode: the research and the interview are already done, so it skips them and runs only the steps that are left.

Read this file in full, then follow your part. Read `layout-format.md` in this folder in full before Part B.

## When to promote

Promote when the developer asks. They may say the scope is bigger than expected, or ask to split the work, or mention a "phase 2" or a "first we need to". Do it at once.

You may also offer it yourself. Offer it when **two or more** of these hold:

| # | Signal |
|---|---|
| S1 | After two rounds, more than 10 questions are still waiting in the queue |
| S2 | The questions fall into three or more groups, and the answers in one group depend on facts that nobody has yet |
| S3 | The decisions so far already imply an order of work with three or more steps, and each step needs decisions of its own |
| S4 | The developer has twice put a decision off to "later" or to "another phase" |

Offer it once per session. If the developer declines, do not offer it again unless they raise it.

Before you offer, explain in the chat what promotion does: the research and the decisions made so far are kept, the work is split into 3 or 4 sprints, a layout is saved instead of a spec, and the developer chooses when to continue. Then ask through the question tool, with "Promote to a brainstorm (Recommended)" first and "Keep grilling" second.

Promotion is not possible once a spec exists for this feature. If a spec file is already in the feature's folder, stop and tell the developer. They can keep the spec, or start `/flow:brainstorm` on a new, larger scope.

## Part A: in the grilling session

### 1. Stop asking questions, and capture the session

Do not ask the next round. Write down, in the chat, so that nothing is lost:

1. **Decisions made.** Every decision the developer has settled in this session: from the `Decision` cells of the research document, the glossary changes, and the conversation.
2. **Questions not yet settled.** The queue: waiting questions, pending follow-ups, and any question you were about to ask.
3. **Concepts.** The concept list from the research.
4. **Slug and feature name.** The kebab-case slug of the feature, and its name in the developer's words.

### 2. Find the folder, and keep the research

Look for `research-output.md` in the feature's spec folder `docs/specs/spec-NN-<slug>/`.

- **The folder holds only research files.** Rename the folder to `brainstorm-NN-<slug>`, keeping the same `NN`. That number is free, because the spec was never written. Use `git mv` if the folder is tracked by git (check with `git ls-files`), and `mv` if it is not. The research file keeps its name and its decisions.
- **There is no research file.** Create `docs/specs/brainstorm-NN-<slug>/`, with `NN` from the rule in `layout-format.md`. Then run the `research` skill with that folder. It asks the developer whether to research.
- **The folder holds other files.** Stop and tell the developer which files. Do not guess.

Then, from the repo root, run `uv run .docsmith/engine/docsmith.py validate` unscoped. It must print `FAILURES: 0`. Relay every WARN line.

### 3. Ask the developer to run the brainstorm skill

The `brainstorm` skill runs only when the developer invokes it, so do not call it yourself. Tell the developer, in the chat:

- the research is saved and the folder is ready: give its path;
- the decisions made and the questions not yet settled are written above, from step 1;
- they should run `/flow:brainstorm` now, **in this same conversation**, because that material lives here. The skill will see it, skip the research and the interview, and write the layout.

Then stop. Write no layout and no spec, and ask no further question about the feature.

## Part B: in the brainstorm skill

You are in promotion mode. Phase 1 (research) and Phase 2 (the interview) of the `brainstorm` skill are **already done**: skip both. Do not run `research` again, do not interview the developer, and do not create the folder. Use the material that Part A left in the conversation.

### 4. Choose the shape

Follow Phase 3 of the `brainstorm` skill, steps 1 to 4, using the material from Part A:

- Put each **decision made** on the sprint that owns it.
- Put each **question not yet settled** on the sprint that must settle it.
- If the developer's decisions show that the work is small after all, say so and offer to keep grilling instead. Write no layout in that case, and undo nothing: the renamed folder stays, and the spec is written into it later as `spec-NN-<slug>`.

### 5. Write the layout

Follow Phase 4 of the `brainstorm` skill, with these differences:

- **Open questions.** Write a row for every question not yet settled, with status `Open`. Also write a row for every decision made, with status `Resolved` and the decision in one sentence. Number all rows `Q-1`, `Q-2`, and so on.
- **Sprint states.** A sprint that has at least one `Resolved` row starts as `grilling`. Every other sprint starts as `proposed`.
- **High-level design.** Include the decisions made, each with its source: a research finding ID, or "interview".
- **Extra check.** Check that every decision made before the promotion appears as a `Resolved` row or in the high-level design. Add this to the checks in Phase 4 of `brainstorm`.

### 6. Continue

Summarise as Phase 5 of `brainstorm` does, and add the number of decisions carried over. Then ask through the question tool:

- "Continue now with Sprint N (Recommended)": N is the first sprint in dependency order that has open questions. Go on in this same session with layout mode of `grill`, from the step "Choose the scope", with the layout and the research already read. If the interview skills are no longer in your context, call them again.
- "Stop here": tell the developer to run `/flow:grill` on the layout later, for one sprint or for several.

Writing the layout ends the promotion. Write no spec.
