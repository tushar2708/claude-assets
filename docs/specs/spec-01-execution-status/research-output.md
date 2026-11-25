---
type: research
title: "Execution Status Skill Research"
status: draft
tags:
  - research
  - execution-status
generated:
  by: flow:docsmith-doc-author
  at: 2026-11-25T05:44:00Z
---

# Execution Status Skill Research

| Section | What it covers |
|---------|----------------|
| [Scope](#scope) | The feature researched, the domains covered, and how decisions are recorded |
| [Business](#business) | Business findings, sources, recommendations and decisions |
| [Product](#product) | Product findings, sources, recommendations and decisions |
| [UX](#ux) | UX findings, sources, recommendations and decisions |
| [Technical / Architecture](#technical--architecture) | Technical findings, sources, recommendations and decisions |
| [References](#references) | Every source consulted and the findings it backs |

## Scope

The feature is a new skill called `execution_status` for the flow plugin. When the `execute` skill is mid-run and the developer asks for the status, the agent today gives a low-effort update that only lists task numbers. The skill should define the communication style of a status update. The update shows which waves are implemented, what the overall task set has achieved, what remains, short notes on detours, and an overall status. It should also get the agent past its narrow view of the current task. Researched: Business, Product, UX, Technical / architecture.

The Decision column starts empty. The interview fills it as each decision is final: `Adopted`, `Dropped`, or `Adopted — <comment>`.

## Business

| ID | Type | Finding | Source | Recommendation | Decision |
|----|------|---------|--------|----------------|----------|
| BUS-1 | Pitfall | "Many employees have a tendency to put a positive spin on anything they report to senior management", and truthful reporting is held back when "the organizational climate is not receptive to bad news" | [hbr.org](https://store.hbr.org/product/the-pitfalls-of-project-status-reporting/SMR483) | Make problems and detours first-class. Never default to "on track" | Adopted — detours are logged and the headline word comes from a rule, so "on track" is never the default |
| BUS-2 | Pitfall | Subjective green/amber/red ratings hide trouble. Quantified criteria work better (seen in search results only; the page did not load) | [mckinsey.com](https://www.mckinsey.com/capabilities/operations/our-insights/increasing-transparency-in-megaproject-execution) | Derive the verdict from tracker counts by a stated rule | Adopted — a status word derived by a stated rule, plus counts |
| BUS-3 | Pitfall | Reports list outputs and activity, while a project can be "done" and still miss its goal (seen in search results only) | [hbr.org](https://hbr.org/2023/11/project-managers-focus-on-outcomes-not-deliverables) | Say what each finished wave achieved, not which tasks closed | Adopted — each wave line states the recorded outcome |
| BUS-4 | Pitfall | Programs capture too many metrics and use few of them (seen in search results only; the page did not load) | [mckinsey.com](https://www.mckinsey.com/capabilities/transformation/our-insights/keeping-transformations-on-target) | Keep the numbers to a few meaningful counts | Adopted — counts of waves built, verified and closed |

## Product

| ID | Type | Finding | Source | Recommendation | Decision |
|----|------|---------|--------|----------------|----------|
| PRD-1 | Best practice | A good status report puts progress, next steps and risks in one place, so the reader needs no outside reference (seen in search results only) | [reforge.com](https://www.reforge.com/artifacts/progress-pulse-program-status-reporting-at-mindtickle) | Put done, remaining and detours in one message | Adopted — done, remaining and detours in one reply |
| PRD-2 | Best practice | Teams use a fixed set of sections each time: learned, achieved, challenges, next steps (seen in search results only) | [lennysnewsletter.com](https://www.lennysnewsletter.com/p/community-wisdom-prioritizing-your) | Use one fixed section order, so the developer knows where to look | Adopted — fixed order: goal, headline, waves, what is left, detours, follow-ups |
| PRD-3 | Best practice | Detail follows the audience: a short summary for stakeholders, finer checkpoints for the team (seen in search results only) | [lennysnewsletter.com](https://www.lennysnewsletter.com/p/community-wisdom-prioritizing-your) | Default to a short summary, with detail on request | Adopted — summary by default, detail on request |
| PRD-4 | Pitfall | Now/Next/Later is a roadmap framework, not a status format, and practitioners report disliking it (seen in search results only) | [lennysnewsletter.com](https://www.lennysnewsletter.com/p/community-wisdom-prioritizing-your) | Use done / in progress / not started, which match the fixed plan | Adopted — wave states, not a Now/Next/Later layout |

## UX

| ID | Type | Finding | Source | Recommendation | Decision |
|----|------|---------|--------|----------------|----------|
| UX-1 | Best practice | Inverted pyramid: the most important information comes first, and "the first sentence of every paragraph should be the most important" | [nngroup.com](https://www.nngroup.com/articles/inverted-pyramid/) | Open with a one-line verdict and the overall progress | Adopted — the headline comes first |
| UX-2 | Best practice | Progressive disclosure: show only a few of the most important options first, disclose "everything that users frequently need up front", and make the path to more obvious | [nngroup.com](https://www.nngroup.com/articles/progressive-disclosure/) | Summary first, per-wave detail on request | Adopted — summary first, per-wave detail on request |
| UX-3 | Pitfall | Too many items on the first view dilute focus, and designs beyond two levels often hurt usability because users get lost | [nngroup.com](https://www.nngroup.com/articles/progressive-disclosure/) | Use two levels only | Adopted — two levels only |
| UX-4 | Best practice | For AI answers, the inverted pyramid is not enough. A better model is a truncated pyramid: the essential answer first, then relevant follow-up prompts so users can pull detail on demand | [nngroup.com](https://www.nngroup.com/articles/less-chat-more-answer/) | End with named follow-ups, such as asking for the detail of one wave | Adopted — the reply ends with named follow-ups |

## Technical / Architecture

| ID | Type | Finding | Source | Recommendation | Decision |
|----|------|---------|--------|----------------|----------|
| TEC-1 | Best practice | A progress file plus git history let an agent "quickly understand the state of work when starting with a fresh context window" | [anthropic.com](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | Read the tracker and the plan fresh at every status request | Adopted — the run log is the progress file; the status skill reads it and the tracker at every request |
| TEC-2 | Best practice | A full feature list with pass/fail marks keeps the whole scope visible and stops an agent declaring the job done too early | [anthropic.com](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | Report against the plan's full wave and sub-feature list | Adopted — one line per wave of the full plan, including waves not started |
| TEC-3 | Pitfall | Agents mark features complete without end-to-end testing | [anthropic.com](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | Show for each wave whether its verify task ran or was skipped | Adopted — three levels reported separately: built, verified, closed |
| TEC-4 | Best practice | Structured note-taking: notes "persisted to memory outside of the context window" let an agent track progress across complex tasks and many tool calls | [anthropic.com](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | Compute the status from the external tracker, not from memory | Adopted — execute writes one short wave line and any detour lines into a plain run log file in the plan's folder; the status skill reads it |
| TEC-5 | Pitfall | The plan's influence on later agent actions drops sharply after the first action, and the authors conclude that context policies "should preserve broader task state, not plans alone". The result is measured on one benchmark, and the authors state confounds | [arxiv.org](https://arxiv.org/abs/2606.22953) | Re-read both the plan and the tracker. Do not rely on the plan sitting in context | Adopted — the tracker is read fresh at every request; the plan and the code are read only where the agent does not already hold them in this conversation |
| TEC-6 | Pitfall | "Overly aggressive compaction can result in the loss of subtle but critical context" | [anthropic.com](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | Detours known only from the conversation can vanish. Record them in the tracker | Adopted — detours are recorded in the run log file as execute runs |

## References

- [Progress Pulse - Program Status Reporting at Mindtickle](https://www.reforge.com/artifacts/progress-pulse-program-status-reporting-at-mindtickle) — findings: PRD-1
- [Community Wisdom: Prioritizing your roadmap (Lenny's Newsletter)](https://www.lennysnewsletter.com/p/community-wisdom-prioritizing-your) — findings: PRD-2, PRD-3, PRD-4
- [The Pitfalls of Project Status Reporting (HBR)](https://store.hbr.org/product/the-pitfalls-of-project-status-reporting/SMR483) — findings: BUS-1
- [How to manage capital projects more efficiently (McKinsey)](https://www.mckinsey.com/capabilities/operations/our-insights/increasing-transparency-in-megaproject-execution) — findings: BUS-2
- [Project Managers, Focus on Outcomes — Not Deliverables (HBR)](https://hbr.org/2023/11/project-managers-focus-on-outcomes-not-deliverables) — findings: BUS-3
- [Keeping transformations on target (McKinsey)](https://www.mckinsey.com/capabilities/transformation/our-insights/keeping-transformations-on-target) — findings: BUS-4
- [Inverted Pyramid: Writing for Comprehension (NN/G)](https://www.nngroup.com/articles/inverted-pyramid/) — findings: UX-1
- [Progressive Disclosure (NN/G)](https://www.nngroup.com/articles/progressive-disclosure/) — findings: UX-2, UX-3
- [Less Chat, More Answer (NN/G)](https://www.nngroup.com/articles/less-chat-more-answer/) — findings: UX-4
- [Effective harnesses for long-running agents (Anthropic)](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) — findings: TEC-1, TEC-2, TEC-3
- [Effective context engineering for AI agents (Anthropic)](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — findings: TEC-4, TEC-6
- [Plans Fade Fast: Why Context Management Is Load-Bearing for LLM Agents (arXiv)](https://arxiv.org/abs/2606.22953) — findings: TEC-5
