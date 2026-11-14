# Layout format

The layout is the one file that holds the shape of a multi-sprint effort. The `brainstorm` skill writes it. Later `grill` and `spec` sessions keep it current. Its structure is the docsmith `brainstorm` template. This file holds the rules that the template cannot show: sprint states, how questions are handled, how a changed decision is recorded, and where the files live.

Read this whole file before you write or change a layout.

## Where the files live

```
docs/specs/
└── brainstorm-03-<slug>/
    ├── brainstorm-03-<slug>.md                      the layout
    ├── research-output.md                           the research for the whole effort
    ├── research-sprint-2.md                         extra research for one sprint, added later (optional)
    ├── spec-03-01-<slug>/spec-03-01-<slug>.md       a sprint spec
    └── spec-03-02-<slug>/spec-03-02-<slug>.md       another sprint spec, added later
```

- **`NN`** is the brainstorm's number. Take the largest numeric prefix among the folders in `docs/specs/` named `spec-<NN>-*` or `brainstorm-<NN>-*`, add one, and zero-pad to the width of the existing prefixes (2 digits when none exist). Standalone specs and brainstorms share this one sequence, so no two folders get the same `NN`.
- **`MM`** is the number of the spec inside its brainstorm, counted from `01`. Take the largest `MM` among that brainstorm's spec folders and add one. Never reuse an `MM`. A sprint added later takes the next `MM`, so you can add sprints to a brainstorm at any time, and two brainstorms never collide.
- A spec that covers sprints 2 and 3 takes one `MM`. Both sprint rows link to it.
- A layout that comes from a promoted grilling session reuses the `NN` of the session's spec folder. The folder `spec-NN-<slug>` is renamed to `brainstorm-NN-<slug>`, and its research file stays in it. See `promote.md`.

## Sprints

A sprint is one chunk of the effort that a person can finish and check. It has a type:

| Type | What the sprint produces | Example goal |
|---|---|---|
| research | Answers to questions that block later sprints. No product code | Find out which of two libraries meets the load limit |
| POC | A throwaway build that tests one idea | Show that the sync approach works for 10,000 records |
| implementation | Product code, tests, and docs | Build the import service |

Rules:

- Create 3 or 4 sprints. Put them in dependency order. Put a research or POC sprint first when later sprints depend on a fact nobody has yet. That clears the unknowns early.
- A sprint number never changes and is never reused. A sprint added later gets the next number, even if it must run earlier. The `Depends on` column carries the order.
- A spec may cover several sprints. A sprint is never split across several specs. If a sprint is too big for one spec, add a new sprint and move the questions to it.

### Sprint states

| State | Meaning | Enters when | Leaves when |
|---|---|---|---|
| `proposed` | Named, with nothing decided | The layout is written, and none of its questions is `Resolved` | It becomes `grilling` |
| `grilling` | Some decisions made, others not | A question of this sprint is resolved, including a sprint written with `Resolved` rows by a promotion, or a session starts working on it | It becomes `finalized` |
| `finalized` | Fully decided | It has zero open questions, and every spec that covers it is `ready` | A resolved decision of the sprint changes (see "Revisions"). It becomes `grilling` again |

A sprint is `finalized` only when both are true: it has zero open questions, and at least one spec covers it with every covering spec at status `ready`. The session that makes the last covering spec `ready` sets the sprint to `finalized`. The spec's own status tracks implementation. The layout never records it.

## Open questions

The Open questions table is the one list of what is not yet decided. It is the fog of war: everything in scope that is not sharp enough to build.

- **IDs** run `Q-1`, `Q-2`, and so on. An ID is never reused.
- **Each question belongs to one sprint.** If you are not sure which sprint, ask the user.
- **A question answered in a session about another sprint** stays on its own row. Record its decision there, then update that sprint's state.
- **A new question found while working** is added as a new row at once, with the next ID and its sprint. Never carry a question only in conversation.
- **Resolving a question:** set `Status` to `Resolved` and write the decision in one sentence, at once, not at the end of the session.
- **A question that turns out not to matter** is `Resolved` with the decision `Dropped: <reason>`.
- **Detail lives in one place.** Once a sprint has a spec, the spec holds the detail of each decision. The layout row keeps one sentence and a link to the spec.
- The layout is complete when it has no `Open` rows and every sprint is `finalized`.

## Revisions

A decision that is already `Resolved` can change while a later sprint is being decided. Do all of these in the same session:

1. Edit the older spec directly, so that it states the new decision. Do not leave the old text in it.
2. Write the new decision into the spec of the sprint you are working on.
3. Update the `Decision` cell of the question to the new decision.
4. Add a row to Revisions: the date, what changed, the old decision, the new decision, and the files you changed.
5. Read the `If it changes` line of every dependency edge that leaves the changed sprint. Re-check the later sprints named there. Add a new `Open` question for every part that no longer holds.
6. If the edit leaves the older spec with open items, set that spec back to `draft` and its sprint back to `grilling`.

## The layout's own status

The layout is `draft` while any sprint is not `finalized` or any question is `Open`. The session that finalizes the last sprint, with zero `Open` rows, sets the layout to `stable`.

## Who changes what

| Skill | Creates or changes |
|---|---|
| `brainstorm` | The layout and the research file, once, at the start |
| `grill` | Question rows, sprint states, Revisions, and the decisions in older specs. It also marks a spec `ready`, with the developer's yes, when the last open item of that spec is resolved, and then finalizes the sprints that spec completes |
| `spec` | The sprint specs, the `Spec` column, and `finalized` when it makes the last covering spec `ready` |
