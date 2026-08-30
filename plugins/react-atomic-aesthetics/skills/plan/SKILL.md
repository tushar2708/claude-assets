---
name: plan
description: |
  Plan a clean, aesthetically intentional React UI/UX before implementation. Use when:
  (1) Starting a new UI feature, page, or component in a React/Tailwind/shadcn project
  (2) Redesigning existing UI
  (3) Any non-mechanical UI change (anything beyond renames, reference updates, or copy-only edits)
  Drives the react-atomic-aesthetics:architect agent to map journeys, analyze existing patterns for consistency,
  and produce an implementation plan that complies with this plugin's canonical RULES.md.
---

# Plan UI

This skill plans a React UI/UX change against the plugin's canonical rules before any code is written.

## Step 0 — Read the rules

Read ${CLAUDE_PLUGIN_ROOT}/RULES.md. All planning decisions must comply with it. Reference rules by number (A1–A20, B1–B5, Part C).

## Step 1 — Enter Plan Mode

This planning step runs inside Claude Code Plan Mode. If not already in Plan Mode, enter it before planning. Do NOT use this skill for bug fixes or for purely mechanical edits (renames, reference updates, copy-only changes).

## Step 2 — Invoke the architect

Delegate to the react-atomic-aesthetics:architect agent. Provide it: the feature goal, the target UI project path, and any known constraints. The architect will:
1. Read RULES.md.
2. Analyze the existing codebase patterns (component structure, design tokens/theme, spacing rhythm, existing atoms/molecules/organisms) and state which it will match for consistency.
3. Map the user journey including all four async states (empty, loading, error, success — RULES A16) and accessibility (A18–A19).
4. Define the atomic component hierarchy (RULES B1) and the aesthetic direction: the single deliberate accent discovered from existing tokens (A1–A2), 2–3 type sizes (A5), whitespace-first grouping (A6), depth/signature (A10–A11), and layout-level differentiation (A12).
5. Produce a prioritized, parallelizable implementation plan with exact files, props interfaces, styling approach (Tailwind + semantic tokens, RULES A3/B3), lucide-react icons and their aria-labels (A18), and per-component acceptance criteria.

## Step 3 — Skip condition

Skip re-invoking the architect if it was invoked recently for similar work in this session and its findings (existing patterns, tokens, plan) are already in context. Reuse those findings instead of re-analyzing.

## Step 4 — Hand off

The plan is executed by react-atomic-aesthetics:implementer agents (see the review skill for post-build review). Do not implement inside this skill.
