---
name: grilling
description: Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases.
---

## Unsupported hosts

If the active host is neither Claude Code nor Codex, tell the user this skill has no validated integration there and suggest opening a support ticket at https://github.com/tushar2708/claude-assets/issues/new.

## Asking questions

Every question that you ask the user must use the available question tool in the harness. For Claude Code, it would be "AskUserQuestion", And in the case of Codex, it would be "request_user_input". In the case of Codex, if the tool is not available, without going into plan mode, either go to plan mode on your own or share the limitation with the user and ask them to put you in plan mode. 

But under no condition are you allowed to ask questions in chat without using the question tool available in the harness. If you are using any other harness (then Claude Code or Codex), figure out what ask question tool exists in that harness. And you can only ask any question in chat if You have verified each and every available tool, and confirmed with the user If any such tool exists or not. Only once you have actively verified each and every option are you allowed to ask any question in chat? (Apart from asking the user what tool to use )

If you have verified that the harness has no tool to ask questions, ask in chat, one question at a time, and number the questions in order. Use this format:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Word each question so "yes" accepts your recommended answer.

This applies to each and every question that you are asking at every stage of the interview. In Codex, add a suffix to every question where you need multiple selection answers. "This question may need more htan one responses, but this harness does not support multi-select questions, so use the option "Other" to mention multiple choices if you want to."

## The interview

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled — the questions you can ask _now_ without guessing at answers you haven't heard yet.

Each round:

1. Compute the frontier. A question whose answer depends on another still-open question belongs to a later round, not this one.
2. Ask the frontier questions in the host's supported batch size. If more remain, prioritize by impact and continue next round.
3. Wait for the answers. Each answer reshapes the tree: settled decisions push the frontier outward and unblock later questions. Recompute the frontier and start the next round.

Keep the questions in a queue. Frontier questions beyond the batch size wait their turn in the queue, and newly unlocked questions join it as the answers arrive. A follow-up question on a question you already asked goes on top of the queue, like a stack: ask every pending follow-up, newest first, before any waiting frontier question. Fill each batch from the top of the queue.

Rules for every question:

Rules 1 to 4 and 6 describe the question tool. In the chat fallback, use the chat format above instead. Rules 1 and 5 apply in both modes; in chat, state the best practice or the pitfall inside the question body. When this skill runs from `/flow:grill`, "Phase 1" and "Phase 3" below are the phases of that skill: the concept map and the saved research. In any other session, ground the questions in the concepts you have mapped and in your own reasoning.

1. Ground the question in your Phase 1 concepts and Phase 3 research. If the developer skipped a domain (or all research), ground those questions in the Phase 1 concepts and your own reasoning instead. State the best practice or the pitfall that makes the question matter, inside the option descriptions.
2. Give each question 2 to 4 options. Put your **recommended option first** and add "(Recommended)" to the end of its label. Explain the trade-off of each option in its description, and reference the research (for example: "NN/g warns this pattern causes error blindness").
3. Never pre-select or pre-check any option, including in multi-select questions. Let the developer choose.
4. Set `multiSelect: true` only when the choices are genuinely not mutually exclusive.
5. Keep asking decisions, not facts. If a question turns out to need a fact, stop before asking that question. Look up the codebase to find the fact, and find similar examples to what you are trying to do. Then ask the question. Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch a sub-agent with a fresh context window to find it; don't ask the user for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report; ask the rest of the frontier now. The _decisions_ are the user's: put each to them and wait.
6. Keep each `header` short (the tool caps it near 12 characters).

**Research document.** When the session has a research document (the caller names it, for example `docs/specs/spec-NN-<use-case>/research-output.md`), it holds one row per research finding. Each row has a recommendation and an empty Decision column. Keep this file current for the whole session:

- Update it as soon as a decision is final. Do not wait for the end of the round or the session. Update the Decision cell of every finding that the decision settles.
- Write exactly one value per cell: `Adopted` (the recommendation is taken), `Dropped` (it is not taken), or `Adopted — <comment>` (it is taken with changes, and the comment states them).
- If a decision changes later, update the cell again. The file always holds the latest decision.
- A long session can hit a context compaction, and you lose the decisions made so far. This file is the record that survives. After a compaction, read it before you ask the next round.
- Write through `flow:docsmith-doc-author` (Task tool, `subagent_type: flow:docsmith-doc-author`). Name the finding IDs and the exact Decision text. Tell it to change only those cells.
- A document that records declined research has no findings. Leave it as is.

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed.

## Converge

1. Summarise the shared understanding: the decisions made, the best practices adopted, the pitfalls now avoided, and the open risks that remain. The best practices and pitfalls come from the research document, when the session has one.
2. Do not act on the plan, decision, or feature until the developer confirms this summary.
3. When they confirm and the session has a research document, offer only `/flow:spec`, in the same conversation, to turn it into a governed spec — no fresh session, the value is the context you just built. The folder that holds the research document is the spec folder, and `/flow:spec` writes the spec into it.
