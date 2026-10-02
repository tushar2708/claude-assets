---
name: grill
description: A research-backed, relentless interview to sharpen a feature. First map its business, product, UX, and technical concepts; research industry best practices and pitfalls for each; then interrogate the developer with the AskUserQuestion tool until you reach a shared understanding.
disable-model-invocation: true
---

Run a grilling session that is grounded in research, not just intuition. Move through five phases in order. Do not skip a phase. Do not start writing or implementing anything until the developer confirms a shared understanding at the end.

The unit of work is the **feature** the developer wants to build or the decision they want to make. Everything below serves one goal: expose every hidden assumption before a line of code is written.

## Phase 1 — Map the concepts

Identify the concepts the feature touches, split across four domains. Name the concepts explicitly; do not stay vague.

| Domain | What to extract |
|--------|-----------------|
| **Business** | The goal, the value, the cost, the risk, the metric that proves success, the stakeholders. |
| **Product** | The user problem, the target user, the scope, the alternatives, the priority, the success criteria. |
| **UX** | The user journey, the entry points, the states (empty, loading, error, success), the friction, the accessibility needs. |
| **Technical / architecture** | The data model, the API contract, the integration points, the failure modes, the scale limits, the security surface. |

Rules for this phase:

1. Find facts yourself. Never ask the developer for a fact you can look up. When a concept needs a fact from this repo (a schema, an existing endpoint, a convention), dispatch a sub-agent to read the codebase and report. Explore in parallel where you can.
2. Write a short, labelled list of the concepts you found, grouped by the four domains. This list drives the research gate in Phase 2 and the research in Phase 3.
3. If the feature is not about software, keep the four domains but adapt them (for a business decision, "technical" becomes "operational", and so on). This skill works on any idea, not only code.

## Phase 2 — Ask whether to research, and which domains (mandatory gate)

Always ask the developer, with the **AskUserQuestion tool**, whether to research this feature on the web — and which domains. This gate is mandatory. Never skip it. Never assume the answer. The developer may want no research for a small feature, or only some domains for a focused one.

The tool caps a question at 4 options, and you have 4 research domains, so a single question cannot also hold a "skip" option. Ask in two steps:

**Step 1 — the on/off gate (single-select).** Ask one question: "Research this feature on the web before I grill you?"

- "Yes — let me choose the research domains (Recommended)"
- "No — skip research and go straight to the questions"

If the developer chooses "No", skip Phase 3 entirely and go to Phase 4.

**Step 2 — the domain picker (multi-select), only if Step 1 was "Yes".** Ask one question with `multiSelect: true`: "Which research do you want?" Offer exactly these four options, **none pre-selected**:

- **Product research**
- **Architecture research**
- **UX research**
- **Business-domain research**

The developer selects any subset; selecting all four means full coverage. Phase 3 then researches only the selected domains. Map each choice to the domain table in Phase 3: "Architecture research" uses the **Technical / architecture** row.

## Phase 3 — Research best practices and pitfalls

For the key concepts from Phase 1, search the web for two things per domain: the **industry best practices** and the **common pitfalls**. Use the web search tool. Prefer the well-known sources below; pass them as `allowed_domains` so the results stay authoritative. Add other reputable, first-party, or official-documentation sources when a concept needs them.

| Domain | Preferred sources |
|--------|-------------------|
| **Business** | hbr.org, mckinsey.com, a16z.com, stratechery.com |
| **Product** | lennysnewsletter.com, svpg.com, reforge.com, mindtheproduct.com |
| **UX** | nngroup.com, baymard.com, lawsofux.com, smashingmagazine.com |
| **Technical / architecture** | martinfowler.com, owasp.org, thoughtworks.com, infoq.com, plus the official docs of any specific technology in play |

Rules for this phase:

1. Research only the domains the developer selected in Phase 2. Skip every domain they did not select. If they chose "No" at the gate, skip this phase entirely.
2. Run searches in parallel across the selected domains where the concepts are independent. Fetch a source page when the search snippet is not enough.
3. For each selected domain, write a compact brief: 3 to 6 bullets of best practices, and 3 to 6 bullets of common pitfalls, each with the source. Cite the source domain next to every claim.
4. Keep only findings that are relevant to this feature. Discard generic advice that does not change a decision.
5. This research is the fuel for Phase 4. Every question you ask should trace back to a best practice to adopt or a pitfall to avoid.

## Phase 4 — Interrogate with the AskUserQuestion tool

Now grill the developer. Ask questions with the **AskUserQuestion tool** — never as plain inline text. The tool renders a structured picker, so the developer answers fast.

Map the feature as a **design tree**: every decision branches into the decisions that hang off it. Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled — the questions you can ask now without guessing at answers you have not heard yet.

Each round:

1. Compute the frontier. A question whose answer depends on another still-open question belongs to a later round, not this one.
2. Call the AskUserQuestion tool with up to 4 frontier questions (the tool's limit per call). If the frontier holds more than 4 questions, ask the top 4 by impact this round, and ask the rest in the next round.
3. Wait for the answers. Each answer reshapes the tree: settled decisions push the frontier outward and unblock later questions. Recompute the frontier and start the next round.

Rules for every question:

1. Ground the question in your Phase 1 concepts and Phase 3 research. If the developer skipped a domain (or all research), ground those questions in the Phase 1 concepts and your own reasoning instead. State the best practice or the pitfall that makes the question matter, inside the option descriptions.
2. Give each question 2 to 4 options. Put your **recommended option first** and add "(Recommended)" to the end of its label. Explain the trade-off of each option in its description, and reference the research (for example: "NN/g warns this pattern causes error blindness").
3. Never pre-select or pre-check any option, including in multi-select questions. Let the developer choose.
4. Set `multiSelect: true` only when the choices are genuinely not mutually exclusive.
5. Keep asking decisions, not facts. If a question turns out to be a fact, stop, look it up with a sub-agent, and drop the question.
6. Keep each `header` short (the tool caps it near 12 characters).

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed.

## Phase 5 — Converge

1. Summarise the shared understanding: the decisions made, the best practices adopted, the pitfalls now avoided, and the open risks that remain.
2. Do not act on the feature until the developer confirms this summary.
3. When they confirm, offer to hand the same conversation to `/to-spec` to turn it into a published spec — no fresh session, the value is the context you just built.
