---
name: explain-feature
description: Explain a repository feature in concise runtime order, covering contracts, state, control flow, and failures. Use only when explicitly invoked.
disable-model-invocation: true
---

# Explain a Feature

Use exactly these headings, in order: `A) Scope`, `B) Entry Point`, `C) Chronological Flow`, `D) Data Contract`, `E) State & Side Effects`, `F) Control Logic`, `G) Failure Modes`, `H) Quick Mental Model`, and optional `I) Deep Dive`.

- Prefer runtime order over an architectural dump.
- State `Unknown` rather than guessing.
- Use bullets, plain language, and relevant `path:line` references.
- Limit sections to 120 words, the initial reply to 500 words and eight files.
- For a `simple` request use only A, B, C, and H. For `detailed`, expand D through G with examples. For a follow-up, address only its requested step with what it does, why it exists, key code, and a common bug.
