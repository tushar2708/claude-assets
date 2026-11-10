---
name: grill
description: A research-backed, relentless interview to sharpen a feature. Map its concepts, research best practices and pitfalls, then reach a shared understanding with the developer.
disable-model-invocation: true
---

## Unsupported hosts

If the active host is neither Claude Code nor Codex, tell the user this skill has no validated integration there and suggest opening a support ticket at https://github.com/tushar2708/claude-assets/issues/new.


## Strict SOP

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

Ask the developer whether to research this feature on the web and which domains. In Claude Code use `AskUserQuestion`; in Codex use `request_user_input`. This gate is mandatory.

The tool caps a question at 4 options, and you have 4 research domains, so a single question cannot also hold a "skip" option. Ask in two steps:

**Step 1 — the on/off gate (single-select).** Ask one question: "Research this feature on the web before I grill you?"

- "Yes — let me choose the research domains (Recommended)"
- "No — skip research and go straight to the questions"

If the developer chooses "No", skip the research in Phase 3, run "Save the research" in its declined form, then go to Phase 4.

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

1. Research only the domains the developer selected in Phase 2. Skip every domain they did not select. If they chose "No" at the gate, skip rules 2 to 5 and run only "Save the research".
2. Run searches in parallel across the selected domains where the concepts are independent. Fetch a source page when the search snippet is not enough.
3. For each selected domain, write a compact brief: 3 to 6 bullets of best practices, and 3 to 6 bullets of common pitfalls, each with the source. Cite the source domain next to every claim, and keep the page URL. Give every finding a one-line recommendation: what this feature should do with it.
4. Keep only findings that are relevant to this feature. Discard generic advice that does not change a decision.
5. This research is the fuel for Phase 4. Every question you ask should trace back to a best practice to adopt or a pitfall to avoid.

### Save the research

Phase 4 does not start until `research-output.md` is saved and validated. This section runs whether the developer chose "Yes" or "No" at the gate. Run these steps once: after the briefs are written, or straight after the gate on "No".

1. **Precondition.** Look for `.docsmith/config.json` walking up from the current directory. If it is absent, STOP: tell the user to run `/flow:init` and wait. Write no doc or folder before docsmith is scaffolded.
2. **Create the spec folder** `docs/specs/spec-NN-<use-case>/`. NN is the next-of-largest existing numeric prefix among the `spec-<NN>-*` folders in `docs/specs/`, zero-padded to the width of the existing prefixes (2 digits when none exist). Find the largest with `ls docs/specs/ | sed -n 's/^spec-\([0-9][0-9]*\)-.*/\1/p' | sort -n | tail -1`. `<use-case>` is a kebab-case slug of the feature from Phase 1. `/flow:spec` later writes the spec into this same folder.
3. **Write the file.** By default, use the `flow:docsmith-doc-author` agent, once, with category `research`. If that agent is not available in the harness, or the user prefers another way, write the file yourself from the `research` template. Either way, `research-output.md` goes in that folder with `type: research` frontmatter, and it must validate to green. Give the writer the folder, and:
   - **Researched ("Yes")**: the briefs from rule 3 and every URL you consulted. Tell it to record every finding as one table row with its type, source link and recommendation, and to leave the Decision cell empty.
   - **Declined ("No")**: tell it to write the declined variant of the template. The file states that the developer declined research for this spec at the Phase 2 gate. It has no domain sections.
4. **Verify.** After the file is written, run `/humanizer` on `research-output.md` (file mode, prose only). From the repo root, run `uv run .docsmith/engine/docsmith.py validate` unscoped (no `--paths`). It must print `FAILURES: 0`. Relay every WARN line to the user. If there are failures and you used `flow:docsmith-doc-author`, re-dispatch it with the exact findings; do not fix them yourself. If you wrote the file yourself, fix the findings and run `validate` again.
5. Only then start Phase 4.

## Phase 4 — Interrogate the developer

Call the Skill tool with `grilling`. It runs the interview, so ask no question yourself in this phase. If its text is no longer in your context (for example after a compaction), call it again. Give it what this session built: the concepts from Phase 1, the research briefs from Phase 3, and the path of `research-output.md`.

## Phase 5 — Converge

The `grilling` skill runs this phase too: the summary, the developer's confirmation, and the offer of `/flow:spec`. Add nothing of your own.
