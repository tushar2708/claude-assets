---
name: explaining-code
description: Produce accurate, consistent, easy-to-read HTML documentation that explains a codebase — one feature, one subsystem, or a whole repository — by reading the real source and tracing every claim to a file:line. Use this whenever the user asks to "explain how X works", "document this repo/feature", "walk me through the codebase", "create a diagram of this flow", "how does this module/pipeline/endpoint work", or wants a visual, structured explanation of code they can keep and share. Prefer this skill over an off-the-cuff prose answer whenever the explanation would benefit from structure, diagrams, or a document the user keeps — even if they do not say the word "documentation".
disable-model-invocation: false
---

# Explaining Code

Build a documentation site (or a single page) that explains a codebase so a newcomer can follow it. The output is HTML with hand-drawn diagrams. Every sentence is traced to the real source; nothing is guessed.

This skill works in **seven phases, in order**. Each phase has one job and one exit condition. You do not start a phase's work until you have created its task; you do not leave a phase until its exit condition holds. Phase 7 runs a set of gates **one at a time** — a document that fails any gate is not finished.

## Why this discipline exists

A reader cannot see the code; they can only see your sentences. If a sentence names a thing you never defined, switches to a new word for an old concept, or states a fact you never verified, the reader is lost and your document is worse than nothing — it is confidently wrong. The phases below exist to make those three failures impossible, not unlikely. Follow them even when a shortcut is tempting; the shortcut is exactly how the errors get in.

## Anti-laziness contract (read before you start)

Your goal is a document that is **accurate** and **easy to understand**, not a document that was cheap to produce. That means:

- **Read the actual code for every claim.** Never describe behavior from a function's name, a comment, or your prior knowledge of similar systems. Open the lines. If you have not read it in *this* repository, you do not know it.
- **Trace, do not skim.** When a function calls another, follow the call. "Candidate", "node", "weight", "handler" — each is a concrete type in this repo; find its definition before you use the word.
- **Define before use.** Every term gets a definition the first time it appears, and a source line.
- **One concept, one word.** Pick one word per concept and keep it. When you must introduce a second word (often because the code's variable name differs), link the two in the same sentence.
- **Do the whole-document read.** Before you show anything, read the finished document end to end as a stranger would, and run every gate. Do not outsource proofreading to the user.

If you catch yourself writing a sentence you cannot back with a file:line, stop and go read the code.

## The task tree (mandatory — create tasks as you go)

This skill is driven by a task list. **Before you begin a phase, create its top-level task** (`Phase 1: …`, `Phase 2: …`, through `Phase 7: …`). When a phase has internal steps, **create numbered sub-tasks as you enter it** (`2.1`, `2.2`, `2.3`, …) and complete them one by one before moving on. Use whatever task tool the host provides (e.g. `TaskCreate`/`TaskUpdate`). The point is that you — and the user watching — always see exactly which phase and sub-step is active, and nothing is silently skipped.

Example shape for one run:

```
1  Scope & setup
2  Build the Term Ledger
   2.1  List every concept the document will mention
   2.2  Assign one canonical term per concept
   2.3  Record aliases, "is it a node?", and the defining file:line
3  Verify the code
   3.1  Read the entry point(s) top to bottom
   3.2  Trace each call into its callee
   3.3  Fill the Verification Log (claim → file:line)
4  Structure & skeleton
5  Fill content
6  Whole-document consistency pass
7  Run the gates
   7.1  Verification gate   7.2  Vagueness gate   7.3  Personification gate
   7.4  Term-consistency gate   7.5  Undefined-term gate   7.6  Continuity gate   7.7  Attribution gate
```

Create sub-tasks for Phases 4, 5, and 6 too — one per section of the document, so each section is tracked through writing and the consistency pass.

---

## Phase 1 — Scope & setup

**Goal:** know exactly what you are explaining and set up the two artifacts the later phases depend on.

1. Pin the scope with the user if unclear: a single feature/function, one subsystem, or the whole repository. Whole-repo → a multi-page site; one feature → a single page. Both use the same shell.
2. Choose **one running example** drawn from the repo's own data (a real request, a real test input, a real record). You will thread this one example through every section so the reader follows concrete values, not abstractions.
3. Create two working artifacts you will fill as you go (keep them in your scratch space, not in the output):
   - a **Term Ledger** (the vocabulary source of truth) — see `references/term-ledger.md`.
   - a **Verification Log** — a flat list of `claim → file:line`.
4. Decide the output location. Default: a `docs/<topic>/` folder in the repo (multi-page) or one `<topic>.html` (single feature). Copy the shared shell from `assets/` (see Phase 4).

**Exit condition:** scope, running example, output location fixed; both artifacts created (empty is fine).

## Phase 2 — Build the Term Ledger

**Goal:** fix the vocabulary *before* writing, so you never switch words mid-document.

Read `references/term-ledger.md` and build the ledger. One row per **concept** (not per word): the single canonical term you will write in prose, a one-line definition, the code's aliases for it, whether it is a graph node / data record / etc., and the `file:line` where it is defined. Record relationships between concepts explicitly (what contains what, what becomes what).

You will keep adding rows during Phase 3 as you discover concepts in the code — that is expected. The rule is only that **a concept has a ledger row before it appears in prose**.

**Exit condition:** every concept the document will name has a canonical term, a definition, and a source; aliases and relationships recorded.

## Phase 3 — Verify the code

**Goal:** turn "I think it works like this" into "it works like this, line N".

Read `references/writing-rules.md` first (it defines what counts as a verified claim). Then:

1. Read the entry point(s) top to bottom — the public function(s) that start the feature or the repo's main flows.
2. Follow every call into its callee. Resolve each data object to its real type and add it to the Term Ledger.
3. For **every** fact you intend to write, open the exact lines and add a `claim → file:line` row to the Verification Log. A claim with no log row does not get written.
4. If the user asks a pointed mechanism question ("is this an LLM or a classifier?", "is this cached?"), answer only after reading the wiring, never from expectation.

**Exit condition:** every planned claim has a Verification Log line; every data object has a resolved type in the ledger.

## Phase 4 — Structure & skeleton

**Goal:** get the shape right before filling it, so you never discover mid-write that a term is used before it is defined.

1. List the sections. Order them so each section uses only terms defined in an earlier section or the ledger. A good default order: orientation/basics → the concrete objects the system keeps → each object's exact shape → the flow(s) step by step → the algorithms/maths → any claims the project makes about itself.
2. Copy the shared shell from `assets/` (`style.css`, the page template, the index template). Never invent a new look — consistency across pages and across runs comes from reusing this shell.
3. Write the **skeleton only**: every section heading plus a one-line statement of intent, no content. For the whole-repo site, also write the landing page with navigation cards to each section and (if the flow is non-trivial) one end-to-end pipeline diagram placeholder.
4. Read the skeleton top to bottom and confirm the order reads right.

**Exit condition:** all section headings exist with intents; the shell is in place; order verified.

## Phase 5 — Fill content

**Goal:** write each section so it is concrete, verified, and flows.

Fill one section at a time (track each as a sub-task). Within a section go **abstract (accurate) → concrete objects → exact data → code**: open with one true plain-language paragraph, then drop immediately to exact data.

Every sentence must satisfy both rules from `references/writing-rules.md`:

- **Content contract:** name the *actor* that acts, the *data structure* it acts on, the *concrete value or operation*, and the *source line*. Give a verb only to an actor that can perform it.
- **Continuity (given → new):** begin each sentence from something already introduced and add exactly one new fact; the output of one step is the subject of the next; never introduce a noun that the previous sentence did not set up.

Use the shared diagram grammar in `references/diagram-grammar.md`: hand-authored inline SVG (not a diagram library), fixed colors/shapes per node kind, every stage box clickable to its section, and **real values shown, never placeholders alone**. Thread the running example through text and diagrams.

**Exit condition:** every section filled; every factual sentence maps to a Verification Log line; the running example appears throughout.

## Phase 6 — Whole-document consistency pass

**Goal:** catch the errors that only appear when the document is read as a whole — the ones that a section-by-section write cannot see. **This is the phase most often skipped, and skipping it is how term-jumping and broken flow survive.**

Read the **entire finished document** top to bottom, as a reader with no prior context. Then, for each term and each section (track each section as a sub-task):

1. Confirm every term is **defined before it is used** — its first appearance in the document is its definition, not a use.
2. Confirm only the **canonical** term appears in prose; every alias either sits in a code block or carries a bridge clause linking it to the canonical term.
3. Confirm the **continuity** holds across sentence and section boundaries: the first noun of each sentence is already known to the reader; the subject of each step is the output of the previous one.
4. Fix every break here, as a set — not one line when the user points at it.

**Exit condition:** one coherent lexicon end to end; no term used before definition; no silent word-switch; flow unbroken.

## Phase 7 — Run the gates, one at a time

**Goal:** a mechanical final check. Read `references/gates.md` for the exact commands. Run each gate as its own sub-task; a gate that fails sends you back to fix, then you re-run it. Do not present until all pass.

1. **Verification gate** — every factual sentence maps to a Verification Log line.
2. **Vagueness gate** — the vague-word grep returns nothing.
3. **Personification gate** — no component is given a verb it cannot perform.
4. **Term-consistency gate** — every alias in prose sits beside a bridge clause or inside `<code>`.
5. **Undefined-term gate** — every ledger term's first occurrence is its definition.
6. **Continuity gate** — spot-read: every sentence picks up from the previous one.
7. **Attribution gate** — each action is credited to the actor that performs it (the code vs an LLM vs the graph library vs the store).

**Exit condition:** all seven gates pass. Only now do you show the user the file path and a one-line summary.

---

## Output shape

- **Whole repository** → a small static site: `index.html` (orientation + nav + one end-to-end diagram) and one page per subsystem, all linking the shared `style.css`.
- **One feature** → a single page with the same shell: title bar, abstract, the objects it touches, one pipeline diagram, the exact steps with the running example, one comparison, and a source table.

Keep the structure, sentence style, diagram grammar, and look-and-feel identical across every document you produce, so a reader who has seen one of your pages can read any other without relearning.

## Reference files

- `references/writing-rules.md` — the content contract, the continuity (given→new) rule, and the term-switch bridge rule, with examples. Read in Phase 3; apply in Phase 5–7.
- `references/term-ledger.md` — the Term Ledger template and how to build it. Read in Phase 2.
- `references/gates.md` — the seven gates with exact grep commands and pass/fail criteria. Read in Phase 7.
- `references/diagram-grammar.md` — the inline-SVG diagram grammar (colors, shapes, clickable stages, real values). Read in Phase 4–5.

## Assets (the shared shell — copy, do not reinvent)

- `assets/style.css` — the one stylesheet every page links.
- `assets/page-template.html` — a single feature page / one section page.
- `assets/index-template.html` — the landing page with navigation for a multi-page site.
