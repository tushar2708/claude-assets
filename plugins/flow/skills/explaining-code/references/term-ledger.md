# The Term Ledger

The Term Ledger is the vocabulary source of truth for one document. You build it in Phase 2 and keep adding to it in Phase 3. Its purpose is to make term-jumping impossible: every concept has exactly one word you will write, decided once, up front.

Keep the ledger in your scratch space (not in the output). It is a working artifact, though a short version of it often becomes a "Vocabulary" box in the final document.

## One row per concept

A **concept** is a thing the system has or does — not a word. Two words for the same thing share one row. Columns:

| Column | What goes in it |
|--------|-----------------|
| **Concept** | A short description of the thing (e.g. "a subject/object string extracted from text"). |
| **Canonical term** | The single word you will write in prose everywhere. Pick the clearest one. |
| **Definition** | One line a newcomer can understand. |
| **Aliases / code names** | Every other word for it, especially the code's variable/type names. These may appear only in code blocks or with a bridge clause. |
| **Kind** | What it *is* structurally: graph node / edge / array / row / function / enum value / id string / vector / … Be specific; "node" vs "edge" vs "the string stored in a table" are different answers. |
| **Source** | The `file:line` where it is defined or constructed. |
| **Relationships** | What it contains, what it becomes, what it is part of. |

## Worked example of a filled ledger (generic)

For a document explaining a rate limiter, the ledger might contain:

| Concept | Canonical term | Definition | Aliases / code names | Kind | Source | Relationships |
|---|---|---|---|---|---|---|
| A caller identified for limiting | **client** | the entity whose requests are counted | `key`, `principal` | string id | `limiter.go:20` | owns one bucket |
| The per-client counter store | **bucket** | holds a client's current token count + last refill time | `entry`, `state` | struct in a map | `limiter.go:34` | one per client |
| The allowance unit | **token** | one unit of permitted work; a request spends one | — | integer field | `limiter.go:38` | stored in a bucket |
| The refill amount per second | **rate** | tokens added to a bucket each second | `rps`, `r` | float config | `config.go:11` | drives bucket refill |

With this fixed, the prose always says *client*, *bucket*, *token*, *rate* — never `key`, `entry`, `rps` outside a code block, and never a new synonym.

## Rules the ledger enforces

1. **A concept has a row before it appears in prose.** If you reach for a word with no row, stop and add the row (with its source) first. This is what prevents "and then the *candidate*…" when "candidate" was never defined.
2. **The canonical term is the only word in prose.** Aliases live in code blocks or ride a bridge clause (see `writing-rules.md`, Rule 3).
3. **Kinds are precise.** If your document ever implies that two different kinds are the same (a record that is "also a node", a value that is "also a function"), the ledger forces you to state the real relationship instead.
4. **Relationships are explicit.** Record "A becomes B", "A contains B", "A is NOT a B". These lines become the sentences that link concepts for the reader — and catch your own false assumptions (e.g. assuming a thing is a graph node when it is actually an edge).

## When to surface the ledger in the output

For any non-trivial document, put a compact **Vocabulary** box near the top (a table: term · what it is · same word as · kind) plus one or two sentences and a small diagram showing how the concepts connect. A reader who meets the terms once, pinned and related, can then follow every later section without re-deriving what each word means.
