# Educational explanation contract

This reference prevents a codebase explanation from becoming an accurate but unhelpful index of functions, files, and types. Read it in Phase 1 before fixing scope, then apply it in Phases 4–7.

This contract adds **educational structure**. It does not replace:

- source verification and attribution in `writing-rules.md`;
- vocabulary discipline in `term-ledger.md`;
- diagram mechanics in `diagram-grammar.md`; or
- the existing mechanical gates in `gates.md`.

## The required outcome

A newcomer must be able to answer all of these after reading the document:

1. What real user or operator outcome is this system trying to achieve?
2. What workload, risk, or constraint made this architecture necessary?
3. For each layer, what problem does it solve that the preceding layer does not?
4. What happens to one concrete input from arrival through result or persistence?
5. What does success guarantee at each important boundary, and what can still fail afterward?
6. Which claims come from the checked-out code, which come from a named external source, and which values are illustrative?

If the document cannot answer these questions, it is a code inventory, not an explanation.

## Prewriting gate: the Explanation Brief

Before creating any output page, create this working artifact next to the Term Ledger and Verification Log. Do not write the document until every field has an answer.

```markdown
# Explanation Brief

## Reader and real-world context
- Reader: what they likely know and do not know.
- User/operator persona: who uses the system.
- Desired outcome: what that person is trying to accomplish.
- Workload or risk: frequency, size, latency, correctness, cost, or operational pressure that matters.

## One running example
- Exact input: a real repository/test input when available.
- Expected result: exact response, stored record, side effect, or failure.
- Illustrative adaptation: only when a real input needs safe product context; label it as illustrative.

## Evidence classes
- CODE: behavior verified in checked-out source, with `file:line`.
- EXTERNAL: published workload/product claim, with a direct named source/link.
- ILLUSTRATIVE: teaching persona, value, or scenario; never present it as observed production data.
- INFERENCE: conclusion drawn from evidence; label the reasoning.

## Layer map
| Layer / section | Reader question | Problem solved | Mechanism | Example state in → state out | Guarantee | Trade-off or failure boundary | Evidence |
|---|---|---|---|---|---|---|---|

## Diagram plan
- Diagram type and the decision or transformation it teaches.
- Actors, real values, and labels for every arrow.
- Which later section each clickable stage opens.
```

The Layer map is the design source for the document. A section without a reader question, problem, example transformation, guarantee, and boundary is not ready to draft.

## Page contract

Every substantive page or section must follow this order:

1. **Why this exists.** Start with the real problem in plain language before naming the mechanism.
2. **The running example at this boundary.** State exactly what value enters the layer and what value, decision, or state leaves it.
3. **How it works.** Introduce the mechanism only after the reader understands the problem it addresses. Apply the abstract → concrete objects → exact data → code progression from `writing-rules.md`.
4. **Guarantee and boundary.** State what this layer makes true and what it deliberately does not promise. Include meaningful failure behavior where relevant.
5. **Carry forward.** End by naming the output handed to the next layer and why the next layer is still needed.

For a document that does not have layers, substitute the equivalent user journey or lifecycle stages. Do not force a technical-layer metaphor onto an unrelated feature.

## First-principles rule

Never open with unexplained jargon or an identifier merely because the code uses it. Explain the underlying constraint first, then introduce the term as the name of the solution.

Bad:

> The service uses RESP2 and a consistent hash ring.

Better:

> TCP delivers one ordered byte stream rather than separate commands, so the server needs a framing rule before it can identify one request. Blobasaur uses RESP2, whose length prefixes mark exactly where each command argument ends.

Bad:

> The system creates SQLite shards.

Better:

> One SQLite database accepts one writer at a time. To let unrelated user updates proceed in parallel, the process places keys into several independent database files; those files are its local shards.

The first sentence may be an analogy only when it is tagged as an analogy and does not replace the exact mechanism.

## Running-example lineage

The same record, request, job, or operation must appear in every appropriate section. Each appearance must advance its state; do not repeat the same example only as decoration.

For example:

```text
client bytes
  → parsed command
  → routing decision
  → selected worker/shard
  → queued or committed operation
  → stored row / external side effect
  → read result or later maintenance state
```

When a branch changes the result, show a contrasting concrete example for each meaningful outcome: for example, local vs redirect, committed vs queued, cache hit vs storage read, or live vs expired.

## Diagram contract

In addition to `diagram-grammar.md`:

- A diagram must teach a transformation, decision, state transition, or collaboration—not list component names.
- Every arrow states what moves or what decision causes it: exact bytes, key, slot, record, operation, response, state, or error.
- Every box names both its kind and its role in the example.
- Use the running example's real values wherever they clarify the mechanism.
- Include both a successful path and a meaningful alternative/failure branch when the distinction is central to the design.
- The diagram caption or adjacent prose states the lesson the reader should take from it.

## Evidence-label rule

Keep these evidence classes visible whenever mixing code, published context, and teaching examples:

- Mark checked-source claims with a repository `file:line`.
- Link external product/workload figures to their authoritative published source.
- Label teaching personas and fabricated-but-realistic values as illustrative.
- Label conclusions that go beyond literal source behavior as inferences and state the evidence behind them.

## Educational acceptance test

Run this after the existing quality gates and before presenting the document:

1. Read each section's first paragraph. Does it state a human or operational problem before introducing implementation jargon?
2. Trace the running example end to end. Does every section show a new concrete state, decision, or output?
3. For each section, can you complete: “This layer exists because ___; it uses ___; therefore ___ is guaranteed; however ___ can still happen”?
4. Inspect each diagram. Can a reader identify the actors, values, decisions, and result without reading the source code?
5. Inspect every workload or production number. Is it labelled CODE, EXTERNAL, ILLUSTRATIVE, or INFERENCE appropriately?

**Pass:** all five answers are yes. A dry subsystem inventory fails even if every factual statement is correctly cited.
