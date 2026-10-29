# The seven gates

Phase 7 runs these gates **one at a time**, each as its own sub-task. A gate that fails sends you back to fix the document, after which you re-run that gate. You present nothing until all seven pass. The gates are mechanical on purpose: they catch the failures that judgment alone misses once a document is long.

Set `DOCS` to the folder (or file) you are checking, e.g. `DOCS=docs/<topic>`.

## Gate 7.1 — Verification

Every factual sentence maps to a `claim → file:line` row in your Verification Log.

- Walk the document section by section. For each sentence that states how the system behaves, point to its Verification Log row.
- A sentence with no row is either unverified (go read the code and verify, or cut it) or it is genuinely non-factual (an analogy, clearly tagged).

**Pass:** no factual sentence lacks a source.

## Gate 7.2 — Vagueness

No filler adjectives or hand-waving stand in for a concrete value.

```bash
grep -rniE "\b(lightly|roughly|basically|simply|somewhat|a bit|sort of|kind of|genuinely|essentially|effectively|powerful|magic|seamless|robust|good|nice|clean|where to start|and so on|under the hood)\b" "$DOCS" \
  | grep -viE "navcard|aria-label|<title>"
```

**Pass:** returns nothing. Each hit is either replaced with the concrete value/operation it was standing in for, or (rarely) is genuinely the right word in context and you can justify it.

## Gate 7.3 — Personification

No component is given a verb it cannot perform (see `writing-rules.md`, Rule 1).

```bash
grep -rniE "(model|llm|graph|vector|store|array|list|index|walk|pagerank|embedding|cache|queue|table) (knows|decides|chooses|wants|remembers|keeps|thinks|understands|realizes|sees|picks|likes|prefers|learns|filters|stores|ranks|selects)" "$DOCS" \
  | grep -viE "the code|the function"
```

**Pass:** returns nothing, or each hit truly has that actor performing that verb. Reassign the verb to the code (or to the model's "generates") where it is wrong.

## Gate 7.4 — Term consistency

Every alias in prose sits beside a bridge clause or inside a `<code>` block.

- For each ledger concept that has aliases, grep each alias across the document.
- For every hit, confirm it is inside `<code>`/`<pre>`, or the same sentence links it to the canonical term.

```bash
# example for one alias; repeat per alias from the ledger
grep -rniE "\bALIAS\b" "$DOCS"
```

**Pass:** no alias appears in bare prose without a bridge.

## Gate 7.5 — Undefined term

Every ledger term's **first** occurrence in the document is its definition, not a use.

- For each canonical term, find its first occurrence (reading order across pages) and confirm that sentence defines it.

```bash
# find the first file/section a term appears in
grep -rni "\bTERM\b" "$DOCS" | head
```

**Pass:** no term is used before it is defined.

## Gate 7.6 — Continuity

Spot-read the document: every sentence picks up from the previous one (see `writing-rules.md`, Rule 2).

- Pick each section's first three sentences and each pipeline/step list. For each sentence, name the word or idea in the previous sentence it starts from.
- A sentence whose first noun was never introduced fails; rewrite it so a prior sentence introduces that noun.

**Pass:** no sentence starts from an unknown noun; each step's subject is the previous step's output.

## Gate 7.7 — Attribution

Each action is credited to the actor that performs it.

- Re-read every sentence containing a model/LLM, a data structure, and the code. Confirm the verb belongs to the named actor: the model *generates*, the code *selects/filters/sorts/writes*, the structure *holds/is read*.

**Pass:** no action is credited to a component that cannot perform it.

---

## After all seven pass

Open the document in a browser once to confirm diagrams render and links work, then tell the user the file path and a one-line summary of what the document covers. Do not ask the user to proofread for the problems these gates check — that is your job, done here.
