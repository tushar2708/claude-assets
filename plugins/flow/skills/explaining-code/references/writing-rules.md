# Writing rules

Two rules govern every sentence. A sentence that breaks either is not finished. They are mechanical: you can check each sentence against them without judgment.

Read this in Phase 3 (it defines what a verified claim is) and apply it in Phases 5–7.

---

## Rule 1 — The content contract

Every sentence that states how the system works must name four things:

| Part | Question it answers | Example |
|------|--------------------|---------|
| **Actor** | Who performs the action? | the code / the LLM / the graph library / the store / the compiler |
| **Data structure** | On what, exactly? | a list, one slot of an array, a row, an edge attribute |
| **Concrete value or operation** | What value or step, in numbers or exact operation? | `× 0.05`, "the top 5 by score", "a dot product" |
| **Source** | Where is this in the code? | `file.py:123` |

If you cannot fill all four, you do not understand the step yet — go read the code.

### Give a verb only to an actor that can perform it

This is the most common attribution error. Components are not people and do not share each other's abilities:

- A **model / LLM** *generates text*. It does not "keep", "filter", "store", "remember", "decide", or "rank" — those are done by the code around it, using the text the model produced.
- A **data structure** (array, list, graph) *holds* values and is *read* or *written* by code. It does not "know", "choose", or "want".
- A **function / the code** *computes, filters, sorts, selects, writes*.

**Wrong:** "The model keeps the relevant items." (A model cannot keep anything.)
**Right:** "The model generates a list of items it judges relevant; the code then matches each one back to the originals and selects those."

When in doubt, ask: *could this thing literally do this verb?* If not, find the actor that does.

---

## Rule 2 — Continuity (given → new)

Each sentence must begin from something the reader already holds (the **given**) and add exactly one new fact (the **new**). The reader builds understanding like a chain; a sentence that starts from an unknown noun breaks the chain.

Concrete checks:

1. **The first noun of a sentence must already be known** — defined earlier, or carried over from the previous sentence. If it is new, the *previous* sentence must be the one that introduces it.
2. **The output of one step is the subject of the next.** Describe a pipeline as a handoff: the thing step N produces is the thing step N+1 starts from.
3. **One new idea per sentence.** If a sentence introduces two unfamiliar nouns, split it, and define the first before using the second.

**Broken flow:**
> The code scores every fact. The candidates are sent to the model. The code fuzzy-matches each reply to a candidate.

(The reader meets "candidates" with no link to "facts", and "reply" with no link to anything.)

**Repaired:**
> The code scores every fact. It takes the five highest-scoring facts — call these the **candidates** — and sends them to the model. The model returns a reply listing the facts it judges relevant; the code then matches each returned fact back to one of the five candidates.

Now every noun entered the chain through a prior sentence.

---

## Rule 3 — The term-switch bridge

This enforces "one concept, one word" at the sentence level. You will often meet two words for one concept: your canonical term, and the code's variable name (e.g. your term is *account*, the code calls the field `user_bal`). Switching silently between them is the single biggest source of confusion.

- **In prose, write only the canonical term** (the one in the Term Ledger).
- **The first time a second word appears, link it in the same sentence**: "the five best matches — the *candidates* —" or "`user_bal` (the code's name for the account balance)".
- A code identifier may appear bare **only inside a `<code>`/`<pre>` block**. In a sentence, it still needs the bridge on first use.
- After the bridge, use only the canonical term again.

**Wrong:** "…added to `user_bal`. The account amount is then averaged. The customer's figure is normalized." (four words — `user_bal`, account, amount, customer's figure — for one concept, never linked.)
**Right:** "…added to the account balance (the code field is `user_bal`). That balance is then averaged, then normalized."

---

## What counts as a verified claim (Phase 3)

A claim is verified only when you have **opened the exact lines that implement it** in this repository and recorded `claim → file:line` in the Verification Log. These do **not** count:

- a function or variable name that sounds like the behavior;
- a comment or docstring (comments drift; read the code the comment describes);
- your memory of how a similar library works;
- a plan/design doc (it states intent, not what shipped).

If a claim cannot be verified from the source, either leave it out or mark it explicitly as an open question for the user — never present it as fact.

---

## Altitude: abstract, then exact

Open each section with **one** true, plain-language sentence that an outsider can follow — the accurate abstract. Then drop immediately to the exact objects, values, and lines. The abstract orients; the exactness informs. Do not stay abstract (that is vibes), and do not open cold with raw internals (that loses the reader). One sentence of altitude, then land.
