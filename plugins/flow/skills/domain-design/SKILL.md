---
name: domain-design
description: Design a new feature or refactor existing code into a domain-driven structure, in any language. Use when the user asks to design, model, structure or refactor a feature, or when new code needs business rules, storage, or outside services. Also used by the grill skill to keep the glossary current during an interview.
disable-model-invocation: false
---

## Unsupported hosts

If the active host is neither Claude Code nor Codex, tell the user this skill has no validated integration there and suggest opening a support ticket at https://github.com/tushar2708/claude-assets/issues/new.

# Domain Design

**Mandatory first action.** Read `references/concepts.md` in full before you do anything else. It defines every term this skill uses, each with an example from one running domain: a meeting-room booking system. Do not continue until you have read it. Do not guess what a term means. When a term is unclear, re-read its row. Re-read the "Test questions" table in that file before Step 4 and Step 5.

**Mandatory second action.** Read `references/project-conventions.md` in full, then learn the project as it says: its instruction files, its lint and type-check configuration, and 2 to 3 existing examples of how things are done in the codebase. Do this before you design anything. Step 0 records the result.

**Mandatory third action.** Choose the language reference files in Step 0, then read each one in full before you write any code. They say which construct of the language to use for each concept. This skill has no other source for that.

## How to use this skill

- Run the **Procedure** in order. Do not start a step until the gate of the previous step passes.
- Write the result of each step into `design.md` in the feature's folder. If the project validates its documentation files, follow its rules for `design.md`.
- Ask the user questions by calling the Skill tool with `grilling`.
- The pseudo-code in this file is a guide. Write the real code in the language of the code you are working on, using the constructs in that language's reference file (Step 0). Use the project's style for everything the reference file does not set.
- Do not invent your own construct for a concept when the reference file has one. If the reference file's form cannot work, write the reason in `design.md` and ask the user.
- The project's existing conventions win on every detail this skill does not set. Where they conflict with this skill, do not pick a side. Ask the user, in the form given in `references/project-conventions.md`.
- The examples use the meeting-room domain. Copy the shape of the reasoning, not the domain.

## The seven laws

These apply to all new code.

1. **Dependencies point inward.** The model imports nothing from use cases, adapters, or other contexts. Use cases import the model and interfaces. Adapters import the model and interfaces.
2. **Collaborators are injected, never created.** See "Collaborators and seams".
3. **Rules live in the model.** Not in handlers, use cases, or adapters.
4. **The model never reads the clock, random numbers, or IDs.** They arrive as parameters.
5. **Aggregates refer to other aggregates by ID only.**
6. **One aggregate is saved per transaction.** Effects on other aggregates travel as events.
7. **Interfaces use business words and core types only.** No SQL, no vendor or library types, no technology words.

## Collaborators and seams

This section is required in the plan and in the code.

**Rule.** Code in the model, in use cases, and in adapters never creates a collaborator. Each collaborator is received through the constructor, typed as an interface. Only the composition root creates adapters.

**Test for "is this a collaborator?"** Ask two questions. Would a test want to replace it? Does it touch the outside world or vary between runs? If either answer is yes, it is a collaborator. You may create these directly: value objects, parts of your own aggregate, events, plain data, errors, and pure functions.

**Forbidden:**

- constructing an adapter or client inside a use case, the model, or an adapter. Only the composition root may do it;
- global or static instances of collaborators, service locators, and registries;
- default parameters that build a real adapter;
- importing an adapter module from the model or from use cases;
- calling the clock, random numbers, UUIDs, or the environment inside the model or a use case;
- container annotations, decorators, or container imports on the model, on use cases, or on interfaces. If the project uses a dependency-injection container, its configuration module is the composition root. It is the only place that declares what is created.

```
# BAD: the use case builds its own collaborators
class ConfirmBooking:
    run(input):
        repo = SqlRoomDayRepository(connect(DB_URL))   # created here
        now  = system_time()                           # hidden collaborator

# GOOD: received through the constructor, typed as interfaces
class ConfirmBooking:
    constructor(roomDays: RoomDayRepository, rooms: RoomRepository,
                clock: Clock, ids: IdGenerator)
```

```
# composition root: the ONLY place that creates adapters
main():
    db      = connect(config.dbUrl)
    confirm = ConfirmBooking(SqlRoomDayRepository(db), SqlRoomRepository(db),
                             SystemClock(), UuidGenerator())
    server  = HttpServer([PostBookingHandler(confirm)])
```

**Plan-time requirement.** The plan must contain a **seam table** (Step 11). Do not write code for a use case until every row of its seam table has an interface, a production adapter, and a test fake.

## Exception for ORMs and data-mapping libraries

The model may be the library's own persistence class: annotations, a base class, generated fields, imports from the library. This avoids a duplicate class and avoids drift. Seven rules keep it safe.

- **E1.** Business rules live in constructors and methods. Never put them in the library's lifecycle hooks, signals, or triggers. Hooks may do only mechanical work, such as audit timestamps.
- **E2.** Library relations (foreign keys, joins, lazy loading) exist only between members of one aggregate. Between aggregates, store the ID.
- **E3.** Model methods never run queries and never save. Lazy loading inside a model method is hidden input and output, so it is forbidden.
- **E4.** Code outside the aggregate's module does not assign its fields. It calls operations. Enforce this with read-only fields or private setters where the language allows. Otherwise add a lint or search rule.
- **E5.** If the library cannot put behaviour on its class (the class is generated, or plain data), write the aggregate as a normal class. The repository converts between the two. Add a round-trip test: fill every field, convert both ways, compare.
- **E6.** One owner of the database schema. Not two.
- **E7.** The library's connection or session is a collaborator. Only repositories use it.

## Procedure

Each step has **Do**, **Output**, **Gate**, and an **Example**.

### Step 0. Choose the mode, learn the project, and choose the language files

- **Do:**
  1. Choose the mode. New feature: run Steps 1 to 15. Existing code: run "Refactor mode". Called by `grill`, or asked to build the glossary during an interview: run "Session mode" only, and skip the rest of this step.
  2. Learn the project. Follow `references/project-conventions.md`:
     - find and read the instruction files (`AGENTS.md`, `CLAUDE.md`, rules files, and the others listed there), from the repository root down to every folder you will change;
     - find the lint, type-check, and style configuration, and the commands that run it;
     - find 2 to 3 existing examples of how the codebase already does each thing this feature needs, and the interfaces, domains, and seams you can reuse.
  3. Find every language the work touches. Look at the build files and at the files you will change or add. Use the language of the code being written, not the language of the whole repository.
  4. Read the matching reference file in full, one per language:

     | Language | File |
     |---|---|
     | Go | `references/lang-go.md` |
     | Java | `references/lang-java.md` |
     | Python | `references/lang-python.md` |
     | TypeScript | `references/lang-typescript.md` |

  5. Read `references/lang-matrix.md` when the work spans two or more languages, or when you port a design from one language to another.
  6. If a language has no reference file, stop and ask the user. Do not borrow another language's file.
  7. For Python, check whether the project runs a type checker. If it does not, tell the user that the distinction between identifier types then rests on convention, and ask whether to add one.
- **Output:** in `design.md`:
  - a "Project conventions" section: the instruction files you read, the checks and commands you found, and the table of existing examples from `references/project-conventions.md`;
  - one line per language: the language, the reference file, and the part of the work it covers.
- **Gate:** the gate in `references/project-conventions.md` passes. Every language the work touches has a reference file that you have read. Follow the language files in Steps 6, 7, 9, 10, 11, 13, 14, and 15. Follow the project's conventions everywhere this skill is silent.
- **Example:** a feature has a Go service and a TypeScript web client. Read the instruction files from the root down to the service folder and the client folder. Find the golangci-lint configuration, `tsconfig.json`, and the ESLint configuration. Find two existing use cases in the service. Read `lang-go.md` for the service, `lang-typescript.md` for the client, and `lang-matrix.md` for the event contract between them.

### Step 1. Scenarios

- **Do:** interview the user. Write 5 to 15 scenarios, each "given … when … then …". Include at least three failures or edge cases.
- **Output:** the scenario list, each with an ID (S1, S2, …). Name the actor of each scenario: the person or outside system that starts it.
- **Gate:** at least three scenarios end in a rejection.
- **Example:**
  - S1: given room A is free 9-10, when Sam confirms 9-10, then the booking is confirmed and `BookingConfirmed` is raised.
  - S2: given A is booked 9-10, when Kim books 9:30-10:30, then it is rejected as an overlap.
  - S3: a 5-hour request is rejected as too long.
  - S4: cancelling 30 minutes before the start is rejected.
  - S5: 9 attendees in a room for 8 is rejected.
  - S6: after a cancellation, the slot is free again and `BookingCancelled` is raised.
  - S7 (room search): find rooms with capacity of at least N and a projector in building B.
  - S8 (room search): sort the found rooms by price.

### Step 2. Glossary and context

- **Do:** read `references/glossary-format.md` first. Add each new noun to the glossary, in that format. Name the context. List the words borrowed from other contexts, and what this feature needs from each: an ID only, or named fields. An ID borrowed from another context becomes this context's own type, with its own name, and is converted at the boundary.
- **Output:** glossary entries, the context name, the context's `_Type_` (core, supporting, or generic), and a "needs from others" list. With two or more contexts, also record the list as `Relationships` blocks in `GLOSSARY-MAP.md`, with the contract, translation, delivery, and pattern of each. Add a row to "Words that differ across contexts" for every word that has two meanings or two names. Every actor named in the scenarios gets a glossary entry with `_Kind_: actor`.
- **Gate:** every noun in the scenarios is in the glossary or is an ordinary word. No borrowed word has two meanings across the boundary. The context has a `_Type_`. If the type is `supporting` or `generic`, apply the lighter procedure in `references/glossary-format.md` and tell the user which steps you skip.
- **Example:** context *Booking*. It publishes `BookingConfirmed(bookingId, roomId, attendeeId, range, price)`. *Billing* listens and creates an invoice. *Billing* never reads *Booking*'s tables.

### Step 3. Rules

- **Do:** turn every "must", "never", "at most", and "only if" into a numbered rule. Give each rule one valid and one invalid example.
- **Output:** the rule list (R1, R2, …).
- **Gate:** each rule can be tested with plain inputs and no database.
- **Example:**
  - R1: confirmed bookings of one room never overlap.
  - R2: a booking has positive length, is at most 4 hours, and stays within one day.
  - R3: attendees do not exceed the room's capacity.
  - R4: cancel only at least 1 hour before the start.
  - R5: at most 8 confirmed bookings per room per day.
  - R6: a cancelled booking cannot be cancelled again.

### Step 4. Classify the nouns

- **Do:** apply the "Test questions" from `references/concepts.md` to each noun.
- **Do (also):** give each kind of identifier its own type, and give each closed set (a status, a kind) an enumeration. `AppId` and `OrgId` are two types, not two names for a string. Use the construct that the language file gives for "Validated ID" and "Enumeration". Raw values become typed values at the edges (handlers, consumers, adapters), and the inside passes the typed value.
- **Output:** a classification table, the `_Kind_` line of each glossary entry, and the `_States_` line of each entity that has a lifecycle. Each state becomes a member of an enumeration.
- **Gate:** every noun has exactly one class: entity, value object, domain service, or event. Every identifier and every closed set has its own type.
- **Example:**

| Noun | Class |
|---|---|
| Room | entity |
| Booking | entity |
| `TimeRange` | value object |
| `Money` | value object |
| `AttendeeCount` | value object |
| `priceFor` | domain service |
| `BookingConfirmed` | event |

### Step 5. Group the rules into aggregates

- **Do:** for each rule, list the objects it reads or changes. Rules that touch the same objects form one aggregate. Choose the root. If a rule needs a fact owned by another aggregate, the use case reads it and passes it in as a value.
- **Size check:** if an aggregate would hold more than a few dozen members, narrow it. For example, use one date instead of a whole year.
- **Output:** an aggregate table, and the `_Contains_` and `_Refers to by ID_` lines of each aggregate root's glossary entry.
- **Gate:** every rule belongs to exactly one aggregate. No aggregate holds another as an object, only its ID. Every term in a `_Refers to by ID_` line is an aggregate root with its own entry.
- **Example:**

| Rule | Objects it touches | Where it goes |
|---|---|---|
| R1, R5 | all bookings of one room on one date | `RoomDay` |
| R4, R6 | one booking | `RoomDay` (member `Booking`) |
| R2 | the new time range | `TimeRange` (value object) |
| R3 | the new booking plus the room's capacity | `RoomDay`. The use case reads the room and passes `roomCapacity` in as a value |

Result: aggregate `RoomDay` (it holds `roomId`, not a `Room`) and aggregate `Room` (capacity, equipment).

### Step 6. Write the value objects

- **Do:** for each value object, write its fields, creation rules, operations, and equality. It has no setters. Write the code in the form the language file gives for "Value object" and "Validated ID".
- **Output:** a spec, then code, then one test per creation rule.
- **Gate:** an invalid instance cannot be constructed.
- **Example:**

```
value TimeRange
    fields: start: Instant, end: Instant
    create(start, end):
        if end <= start                    -> error "range must have positive length"   # R2
        if end - start > 4 hours           -> error "range too long"                    # R2
        if date(start) != date(end)        -> error "range must stay within one day"    # R2
    date()  -> Date:  the date of start
    overlaps(other) -> bool:  start < other.end and other.start < end
    equality: by start and end
```

### Step 7. Write the aggregates

- **Do:** for each aggregate, write an **operation table**: name, inputs, preconditions with rule IDs, state change, event raised, errors. Then write the code. `now` and new IDs are inputs. The model never reads them. Write the code in the forms the language file gives for "Aggregate root", "Rebuilding from storage", "Domain event", and "Domain error".
- **Output:** the operation table, the code, and one test per rule named after the rule.
- **Gate:** every rule appears in exactly one operation's preconditions and has a test.
- **Example:**

```
aggregate RoomDay
    identity: (roomId, date)
    fields:   roomId, date, bookings: list of Booking
    member Booking: id, attendeeId, range: TimeRange, attendeeCount, status, price

    operation confirm(bookingId, attendeeId, range, attendeeCount, roomCapacity, price, now)
        requires: range.date() == this date                       -> WrongDate
                  attendeeCount <= roomCapacity                   -> OverCapacity      # R3
                  no confirmed booking overlaps range             -> Overlap           # R1
                  fewer than 8 confirmed bookings                 -> DayFull           # R5
        changes:  add Booking(status = confirmed)
        raises:   BookingConfirmed(bookingId, roomId, attendeeId, range, price, at = now)

    operation cancel(bookingId, now)
        requires: booking exists                                  -> NotFound
                  booking.status == confirmed                     -> AlreadyCancelled  # R6
                  booking.range.start - now >= 1 hour             -> TooLateToCancel   # R4
        changes:  booking.status = cancelled
        raises:   BookingCancelled(bookingId, roomId, at = now)
```

```
test R1_overlap_is_rejected:
    day = RoomDay.empty(roomA, 2026-03-01)
    day.confirm(id1, sam, 9-10, 2, 8, price, now)
    expect day.confirm(id2, kim, 9:30-10:30, 2, 8, price, now) fails with Overlap
```

### Step 8. Write the events

- **Do:** write one immutable data type per event, named in the past tense. Include the aggregate's ID, the time, and the minimum other data a listener needs.
- **Output:** the event types, and the `_Raised when_` and `_Carries_` lines of each event's glossary entry.
- **Gate:** each event is raised by exactly one operation, and has both glossary lines.

### Step 9. Write the interfaces

- **Do:** for each driven need of each use case, first search the codebase for an existing interface that does the job (Step 0 lists them). Reuse it. Write a new one only when none fits, and write the reason in `design.md`. Then, for each need without an interface, write one:
  - a repository per aggregate root: `get`, `save`, and queries named in glossary words;
  - an index for search, if a scenario needs one;
  - a gateway per third-party service;
  - small interfaces for the clock and for ID generation.

  Write each in the form the language file gives for "Interface (port)", "Clock", and "ID generator".
- **Rules:**
  - Parameters and results are core types only.
  - No SQL, no vendor type, no technology word.
  - Errors are core errors (not found, conflict), not driver errors.
  - Keep interfaces small.
- **Output:** the interface files.
- **Gate:** a search of the interface files for technology and vendor words returns nothing.
- **Example:**

```
interface RoomDayRepository  get(roomId, date) -> RoomDay      # an empty RoomDay if none exists
                             save(roomDay)                      # also stores the events the model raised, in the outbox, in the same transaction
interface RoomRepository     get(roomId) -> Room
interface Clock              now() -> Instant
interface IdGenerator        newBookingId() -> BookingId
```

An outbox worker (an inbound adapter) later hands the stored events to listeners through an `EventBus` interface.

### Step 10. Decide the persistence mapping

- **Do:** for each aggregate, answer one question: can the persistence class carry methods? If yes, it is the aggregate: apply E1 to E7. If no, write a normal class and a mapper in the repository (E5). The language file's section "Under the ORM exception" says how E4 is enforced in that language.
- **Output:** one written answer per aggregate.
- **Gate:** every aggregate has an answer. No library relation crosses an aggregate boundary.

### Step 11. Write the use cases and the seam table

- **Do:** write one use case per user intent. Each one follows these steps:
  1. Build value objects from the input.
  2. Load the aggregate through its repository.
  3. Call the aggregate's operation.
  4. Save. The repository records the events the model raised.
  5. Return a result.

  A use case decides nothing the model can decide. Write the code in the forms the language file gives for "Use case", "Injection", "Adapter", and "Composition root".
- **Output:** the use-case code, a **seam table**, and the `_Actor_` line of each use case's glossary entry.
- **Gate:** every row of the seam table has an interface, a production adapter, and a test fake. The constructor lists every collaborator. Nothing is created inside.
- **Example:**

```
class ConfirmBooking
    constructor(roomDays, rooms, clock, ids)                # all injected
    run(input):
        range = TimeRange.create(input.start, input.end)
        room  = rooms.get(input.roomId)
        day   = roomDays.get(input.roomId, range.date())
        price = priceFor(room.rate, range)                  # pure function: created directly
        day.confirm(ids.newBookingId(), input.attendeeId, range,
                    input.attendeeCount, room.capacity, price, clock.now())
        roomDays.save(day)
        return BookingConfirmedResult(...)
```

| Use case | Collaborator | Interface | Production adapter | Test fake |
|---|---|---|---|---|
| ConfirmBooking | loads and saves `RoomDay` | `RoomDayRepository` | `SqlRoomDayRepository` | `InMemoryRoomDayRepository` |
| ConfirmBooking | reads room capacity and rate | `RoomRepository` | `SqlRoomRepository` | `InMemoryRoomRepository` |
| ConfirmBooking | current time | `Clock` | `SystemClock` | `FixedClock` |
| ConfirmBooking | new booking ID | `IdGenerator` | `UuidGenerator` | `SequenceIdGenerator` |

### Step 12. Place the fields

Do this step only when a feature uses a search index or more than one store.

- **Do:** write a placement table. Follow these rules.
  1. Every field lives in the system of record.
  2. A field enters an index only if a scenario filters, sorts, or scores by it. Write the scenario ID in the reason column.
  3. The index stores an **entry**: a small separate type, built from the model by one function `toEntry(model)`. There is no function back to the model.
  4. A search returns **hits** (ID and score).
  5. The use case then loads the full records by ID from the system of record, keeping the hit order. This is how the final response gets its extra fields.
  6. Writes: save to the system of record first. The outbox row is written in the same transaction. A worker then updates the index, and retries on failure. An index failure never undoes the record. The index can always be rebuilt from the record.
  7. Deletes work the same way. A hit whose record no longer exists is skipped.
  8. Add an index only when a scenario needs it.
- **Output:** the placement table, the entry type, and `toEntry`.
- **Gate:** the entry type's fields equal the table's index columns exactly. A test asserts this.
- **Example:** scenarios S7 and S8.

| Field | Record | Index | Reason |
|---|---|---|---|
| id | ✔ | ✔ | join key |
| capacity | ✔ | ✔ | filter (S7) |
| equipment | ✔ | ✔ | filter (S7) |
| building | ✔ | ✔ | filter (S7) |
| hourlyRate | ✔ | ✔ | sort (S8) |
| name, photos, description | ✔ | – | returned only |

### Step 13. Write the tests

- **Do:** write tests at four levels.
  1. Model tests with no fakes: one per rule.
  2. Use-case tests with the in-memory fakes from the seam table: one per scenario.
  3. A contract test for each interface. Run it against both the fake and the real adapter.
  4. The placement test from Step 12.

  Write the rule tests as tables of cases, in the form the language file shows. Write the fakes as the language file's "Fake" row says: they store the aggregate's state and rebuild it on every load. Write the contract test as its "Contract test" row says.
- **Output:** the tests.
- **Gate:** every scenario ID and every rule ID appears in the name of a test.

### Step 14. Lay out the code

- **Do:** use this layout, or the nearest equivalent that keeps the dependency rules. If the project already has a layout, keep its folder names and structure. Keep the dependency rules. Where the two cannot both hold, ask the user.
- **Output:** the files in place.
- **Gate:** the dependency rules from "The seven laws" hold for the layout.

```
<context>/
  GLOSSARY.md   only when the project has two or more contexts (see below)
  model/        value objects, aggregates, events, domain services
  usecases/     one per use case
  ports/        interfaces the core needs
  adapters/
    inbound/    handlers, command-line commands, consumers, schedulers   (they call use cases)
    outbound/   database, search index, third-party clients, clock, ID generator   (they implement ports)
startup file outside every context = the composition root
```

Handlers receive the use case through an interface, so handler tests can use a stub.

Glossary placement: with one context, `GLOSSARY.md` sits at the repo root. With two or more contexts, each context folder has its own `GLOSSARY.md`, and the repo root has `GLOSSARY-MAP.md`. The details are in `references/glossary-format.md`.

### Step 15. Enforce, then run the checklist

- **Do:** run every check below. For each language the work touches, use the search patterns in section 4 of that language's reference file. Each result needs evidence: a file and line, a search result, or a test name. "Unknown" is an allowed answer. Add lint or import rules, as section 5 of the language file says, so that C1, C2, C3, and C9 fail the build. Add them to the project's existing lint tool, found in Step 0. Run every lint, type-check, and test command that Step 0 found, through the project's own scripts. They must all pass without changing the project's configuration to make them pass.
- **Output:** the checklist, with evidence, in `design.md`.
- **Gate:** every item passes, or has a written reason and a follow-up.

| # | Check | How |
|---|---|---|
| C1 | The model and the use cases import no adapter, driver, or framework. | Search the imports. The import rule fails the build. |
| C2 | No collaborator is constructed outside the composition root and the tests. | Search for constructor calls of each adapter in the seam table. |
| C3 | No global or static collaborator instances, and no container annotations in the model, use cases, or interfaces. | Search for module-level or static instances, and for annotations. |
| C4 | No clock, random, ID, or environment call inside the model or the use cases. | Search for the calls listed in the language file. |
| C5 | Every rule and scenario has a test named after it. | List the tests. |
| C6 | Every interface has a fake and a contract test that runs against both the fake and the real adapter. | Check the seam table and the contract test. |
| C7 | No library relation crosses an aggregate. | List the relations. |
| C8 | The entry type matches the placement table. | The Step 12 test. |
| C9 | Nothing outside the aggregate assigns its fields. | The compiler, or a search for assignments, as the language file says. |
| C10 | Interfaces contain no technology words. | Search the interface files. |
| C11 | No `_Avoid_` word of the context appears in an identifier. | Search the context's code for each avoid-word. |
| C12 | No bare primitive for an ID, an amount, a currency, or a status in the model, the use cases, or the interfaces. | Search with the patterns in the language file. State types and the value object's own definition are exempt. |
| C13 | Value objects and events cannot be changed after creation. | The check in the language file. |
| C14 | Events are built only inside their aggregate. | Search for event construction elsewhere. |
| C15 | Interface files import only core types. | Search the imports of the interface files. |
| C16 | Adapters translate driver errors. No driver error type appears in an interface, and a contract test shows a duplicate becomes a core `Conflict`. | Search the interface files, and run the contract test. |
| C17 | Fakes are in-memory implementations. A mocking tool may only check recorded events. | Search the use-case tests for mocks of interfaces. |
| C18 | Go only: a use case rejects the zero value of each value-object input. | One test per use case. |
| C19 | Every kind of identifier has its own type, and every closed set is an enumeration. No two kinds share a type, and no alias stands in for a distinct type. | The check in the language file. |
| C20 | A function with two or more parameters of the same type takes named fields. | List such functions, as the language file says. |

## Refactor mode

Use this when the code already exists.

0. Run Step 0: find the languages and read their reference files.
1. Pick one flow.
2. Write tests that capture its current behaviour at the outermost entry point.
3. Move the flow into a use case without changing its behaviour.
4. Run Steps 1 to 5 on what the code does today. Move one rule at a time into the model, each with its unit test.
5. For each outside call in the use case, add an interface. Move the call into an adapter. Add the seam-table row and a fake.
6. Delete the old path. Add the lint rule that keeps the gain.

## Session mode (used by `grill`)

Use this mode when `grill` calls this skill, or when the user asks you to build or sharpen the glossary during an interview. Run it together with the `grilling` skill. `grilling` runs the interview. This mode adds the domain duties below to it.

In this mode:

- Do not run Steps 0 to 15. Do not write code. Do not read the language files or `references/project-conventions.md`.
- Read `references/concepts.md` and `references/glossary-format.md` in full.
- Put every question to the user through `grilling`: explain in the chat first, then use the question tool, with your recommended answer first.

**Before the first question.**

1. Find the glossary files as the section "Which structure applies" in `references/glossary-format.md` says. Read every one. A `GLOSSARY-MAP.md` lists them.
2. If none exists, do not create one yet. Create it when the first term is resolved (duty 5).
3. Keep the terms in your context. After a compaction, read the glossary files again before you ask the next question.

**The six duties and the ADR offer.** Each duty has a trigger. When the trigger happens, do the duty at once, in the same round. Do not save it for the end.

1. **Challenge against the glossary.**
   - Trigger: the user uses a word from an `_Avoid_` list, or uses a glossary word with a meaning other than its definition, or uses two words for one glossary term.
   - Do: say it in the chat at once. Quote the glossary definition and the way the user used the word. Ask which is right.
   - If the glossary is right, use its word from then on. If the user's meaning is right, treat it as a rename (duty 5).
   - Example: "Your glossary defines *Cancellation* as 'a confirmed booking that the attendee ends before it starts'. You just described a cancellation by the room owner. Which meaning is right?"
2. **Sharpen fuzzy language.**
   - Trigger: a word is vague, or has more than one meaning in this product, or one thing gets two names in the conversation.
   - Do: list each meaning you find in the code and in the conversation. Propose one canonical term for each. Ask which the user means.
   - Example: "You said *account*. The code has `Customer` (who pays) and `User` (who signs in). Which one do you mean? If both, I propose two terms, *Customer* and *User*."
3. **Discuss concrete scenarios.**
   - Trigger: the user describes a rule, or a relationship between two concepts.
   - Do: write a scenario of the form "given … when … then …" that probes an edge: a boundary, an empty case, a duplicate, a concurrent request, a request that is too late, an action done twice. Ask what must happen. Write at least one scenario per relationship, and at least one that ends in a rejection.
   - Keep the settled scenarios. List them at Converge. Step 1 of the Procedure starts from them.
   - Example: "Given room A is booked 9:00 to 10:00, when Kim books 9:30 to 10:30, what must happen: reject it, or shorten it to 10:00 to 10:30?"
4. **Cross-reference with the code.**
   - Trigger: the user states how something works today.
   - Do: check the code. Finding it is your job: use a sub-agent, as the `grilling` skill says for facts. If the code disagrees, quote the `file:line` and ask which is right.
   - Example: "You said a booking can be partly cancelled. `internal/booking/cancel.go:41` cancels the whole booking. Which is right?"
5. **Update the glossary inline.**
   - Trigger: a term is resolved: new, renamed, merged, or split.
   - Do: edit the glossary file at once, in the format of `references/glossary-format.md`. One entry per term, with a definition of one or two sentences and an `_Avoid_` list. Leave `_Kind_` out of an entry whose kind is not decided yet. Step 4 of the Procedure adds it. Write the fields from the "Term fields" section of the format file (`_Actor_`, `_States_`, `_Contains_`, `_Refers to by ID_`, `_Raised when_`, `_Carries_`) only when the user's answers settle them. Otherwise leave them off. With a rename, follow the rename rule in the format file.
   - Put the term in the right context. If a second context appears, follow "Going from one context to two" in the format file. If the user is not sure which context, ask.
   - The glossary holds words and their meanings only. Never write implementation details, decisions, or scenarios into it.
   - Tell the user, in one line in the chat, which file you changed and which term.
   - Example: the user settles that a *Booking* is "a confirmed claim on one room for one time range". Add that entry, with `_Avoid_: reservation, slot`, to the Booking context's `GLOSSARY.md`. Create the file if it does not exist.
6. **Offer ADRs sparingly.**
   - Trigger: the user makes a decision.
   - Do: read the section of `../write-adr/SKILL.md` that says when to discuss an ADR. If the decision meets at least one of its criteria, ask the user, through the question tool, whether to record it as an ADR. If it meets none, say nothing.
   - If the user says yes, do not write it. The `write-adr` skill runs only when the user invokes it. Note the topic. At Converge, tell the user to run `/flow:write-adr` for each noted topic.
   - Example: "Contexts will talk only through events, never through direct calls. This is a pattern that every future feature must follow, so it meets the criteria in `write-adr`. Record it as an ADR?"

**At Converge.** Add these to the summary that `grilling` gives, before the user confirms:

- the glossary files you created or changed, with the terms added, renamed, or removed;
- the scenarios that were settled;
- the contradictions between the user's description and the code, and how each was resolved;
- the ADR topics the user wants to record, with the command to run;
- the words that are still open, with the reason.
