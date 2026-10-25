# Wave Model

The one definition of the flow model. Read by `/flow:spec`, `/flow:plan-it`, `/flow:make-tasks`, and `/flow:execute`.

## Hierarchy

spec → sub-features → waves → stages → tasks

| Level | Meaning |
|---|---|
| Sub-feature | One complete increment of behavior. The spec defines the sub-features. |
| Wave | Exactly one sub-feature, with its full TDD cycle. |
| Stage | An ordered step inside a wave. |
| Task | One logical change inside one stage. |

```
Plan
├─ Tag: one short tag for the whole plan, used in every task title
├─ Sources: session | spec <path> | both
├─ Skill compliance ledger: skill | MUST rule | satisfied in (wave/stage/task) | N/A reason
└─ Wave W<n> = sub-feature SF-<id>   (serial; W<n+1> starts after W<n>'s verify task)
   ├─ Shared contracts (types, interfaces, conventions, test tables)
   ├─ Extra gate commands (optional)
   ├─ Stage S1 contracts | S2 tests | S3 implementation   (non-TDD: S1 only)
   │  └─ sub-stage S<m>a, S<m>b only when a task imports a new symbol from a task in the same stage
   │     └─ Task T<k>
   └─ Verify task
```

## Spec Sub-feature Fields

| Field | Content |
|---|---|
| ID | `SF-<n>` |
| Name | Short name |
| Behavior | What the sub-feature does |
| User stories covered | User story numbers |
| Depends on | Earlier SF only |
| Done-when | Checkable acceptance criteria |

1. The list is ordered.
2. No file paths.

## Wave Rules

1. One wave = one sub-feature: `W<n>` = `SF-<id>`.
2. A plan can split a spec sub-feature into `SF-<n>a`/`SF-<n>b`.
3. Never merge sub-features. Never reorder sub-features.
4. Waves are always serial.
5. Each wave ends compiling, tests green, pre-commit passing.
6. Plan every wave for that end state, also when verification is skipped.

## Stage Rules

| Wave type | Stages |
|---|---|
| TDD | S1 contracts (types, interfaces, stubs, mocks) → S2 tests (table-driven, must fail) → S3 implementation (tests must pass) |
| Non-TDD | S1 only |

1. A stage splits into sub-stages `S<m>a`, `S<m>b` only when a task imports a new symbol from another task in the same stage.
2. Tasks in a stage run in parallel.
3. Stages run in order.

## Ownership Rule

1. A file belongs to at most one task in a stage.
2. The same file can appear in a later stage or wave.

## Task Definition

1. One logical change in one stage.
2. Any number of files.
3. Any number of edits per file.
4. No file cap.

## Task Fields

All fields are required.

| Field | Content |
|---|---|
| Title | `[<tag>] W<n>.S<m>.T<k> <name>` |
| Wave | `W<n>` = `SF-<id>` |
| Stage | `S1`, `S2`, `S3`, or a sub-stage |
| Files | Every file the task owns in this stage |
| Changes | Every edit, per file, with full detail |
| Shared contracts | In the plan: the wave section names its contract sections by exact heading. In the tracker: `/flow:make-tasks` writes them once per wave to `<plan path without .md>.tasks/W<n>-contracts.md`, and each task names that file and the plan sections it cites |
| Test cases | Table-driven cases (S2 tasks, and S3 tasks that make them pass) |
| Self-check | One compile/build command for the touched package. No test suite. Runs without asking. |
| Agent | An agent name from the agent table, or `main-thread` |
| Done-when | Checkable acceptance criteria |
| Blocked by | All tasks of the previous stage or sub-stage. First stage: the previous wave's verify task. W1 first stage: none. |

## Verify Task

One per wave. Title `[<tag>] W<n>.verify`. Blocked by all tasks of the wave's last stage.

| Field | Content |
|---|---|
| Wave | `W<n>` = `SF-<id>` |
| Extra gate commands | Commands the plan lists for the wave, for example the project's coverage target |
| Procedure | The steps below |

Procedure:

1. Read the verify choice from the tracker. If a choice exists, apply it. Do not ask.
2. If no choice exists, ask the user with AskUserQuestion. Options: "Run for this wave", "Run for every wave", "Skip for every wave".
3. On "Run for every wave": write "run — user choice at W<n>" into every remaining verify task.
4. On "Skip for every wave": mark every remaining verify task completed with "skipped — user choice at W<n>". Stop here.
5. Run `pre-commit run --files <every file the wave changed>`.
6. Run the wave's extra gate commands.
7. Check each task's changes against its plan entry and the wave's done-when list.
8. Fix every failure. Run steps 5–7 again until all pass.

Rule: If the user said run, run. If the user said skip, skip. No exceptions.

## Post-wave Tasks

Owner reminders, doc tasks, and feedback.

1. Blocked by the last verify task.
2. Block nothing.
3. Feedback is last.

## Agent Table

| Primary file type of the task | Agent |
|---|---|
| `.go` | golang-code-implementer |
| `.py` | python-code-implementer |
| `.ts` backend (no JSX) | typescript-code-implementer |
| `.tsx`, `.jsx`, React `.ts` | react-atomic-aesthetics:implementer |
| docs governed by docsmith | flow:docsmith-doc-author |
| any other type, or the agent is not available in the session | main-thread |

1. Never use general-purpose.

## Commit Rule

1. Never commit. Never offer or suggest a commit. Commit only when the user asks.

## Compliance Ledger

| skill | MUST rule | satisfied in (wave/stage/task) | N/A reason |
|---|---|---|---|
