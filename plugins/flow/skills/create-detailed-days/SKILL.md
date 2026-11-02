---
name: create-detailed-days
description: Turn a range of an existing N-day plan into a self-contained day-by-day implementation guide with verified learning resources. Use only when explicitly invoked.
disable-model-invocation: true
---

# Create Detailed Days

## Host-specific questions

- **Claude Code:** use `AskUserQuestion` when it is available.
- **Codex:** use `request_user_input` when it is available.
- **Any other host:** ask the same questions in concise plain text.

Collect the starting day, batch size, source N-day plan, latest previous detailed-days guide (if any), and requested study-focus areas. Read prior guides before continuing a series.

Write `docs/plan/<plan-name>/detailed-days-<start>-<end>.md`. Process exactly one day at a time: research, write that day, record its completion using the host task tracker if available (otherwise a checklist in the output document), then continue.

For each day include:

1. An action-oriented task title.
2. A 3–5 sentence purpose and connection to prior work.
3. Prerequisites with 2–3 verified resources per topic, prioritizing official documentation and including relevant papers, tutorials, videos, examples, comparable projects, and alternatives.
4. Five to eight ordered, verifiable subtasks with paths where useful.
5. Minimal complete interface, structure, signature, or usage examples—never full implementations.
6. One concise verification statement.

Research current sources before citing them. Preserve continuity, formatting, and cross-references with prior guides. Finish with a sprint summary and the next-batch teaser.
