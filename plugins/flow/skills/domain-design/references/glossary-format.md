# Glossary format



Purpose: this format defines the words of each context, so that humans and agents always use one common vocabulary. It also paves the way for future domain design and extension. The `domain-design` skill writes these files in Step 2.


A glossary file has this structure and these rules.

## Structure

```md
# {Context Name}

_Type_: core | supporting | generic

{One or two sentence description of what this context is and why it exists.}

## Language

**Booking**:
A confirmed claim on one room for one time range.
_Kind_: entity, member of RoomDay
_States_: confirmed → cancelled
_Avoid_: Reservation, slot

**RoomDay**:
One room's bookings for one date.
_Kind_: aggregate root
_Contains_: Booking
_Refers to by ID_: Room

**Room**:
A meeting area that can be booked for a time range, with a capacity and equipment.
_Kind_: aggregate root
_Contains_: none
_Avoid_: Venue, space

**Attendee**:
A person who uses a booked room.
_Kind_: actor
_Avoid_: Guest, user

**TimeRange**:
A start and an end, where the end is after the start.
_Kind_: value object

**BookingConfirmed**:
Something the business cares about: a booking became confirmed.
_Kind_: event
_Raised when_: a booking becomes confirmed
_Carries_: booking, room, attendee, time range, price

**Confirm booking**:
The request to claim a room for a time range.
_Kind_: use case
_Actor_: Attendee
```

## Rules

- **Be opinionated.** When multiple words exist for the same concept, pick the best one and list the others under `_Avoid_`.
- **Keep definitions tight.** One or two sentences max. Define what it IS, not what it does.
- **Only include terms specific to this project's context.** General programming concepts (timeouts, error types, utility patterns) don't belong even if the project uses them extensively. Before adding a term, ask: is this a concept unique to this context, or a general programming concept? Only the former belongs.
- **Group terms under subheadings** when natural clusters emerge. If all terms belong to a single cohesive area, a flat list is fine.
- **Give every term a `_Kind_`.** Use one value from this list: `entity`, `value object`, `aggregate root`, `event`, `use case`, `domain service`, `actor`, `plain term`. An `actor` is a person or an outside system that asks the application to do something. A member of an aggregate says so: `entity, member of RoomDay`. The kind describes the model, not the code. Step 4 and Step 5 of the skill decide it. A term gets its `_Kind_` when Step 4 classifies it. In a grilling session (the skill's "Session mode"), an entry may leave `_Kind_` out until its kind is decided.
- **Events and use cases are terms.** Write each event and each use case as an entry, because they are part of the shared language. Events are named in the past tense. Use cases are named as a request.
- **Mark the context type.** The `_Type_` line says how much of the skill's procedure the context needs:
  - `core`: the part of the product that makes it valuable. Run every step.
  - `supporting`: needed, but not special. Run Steps 1 to 5, 7 and 9. Aggregates are optional.
  - `generic`: a solved problem, such as sending email or taking payments. Prefer an existing product or library. Otherwise write simple code, with no aggregates.
  - If you cannot decide, ask the user.
- **Words in `_Avoid_` never appear in code.** No type, function, variable, file, table, column, route, or event name may use an `_Avoid_` word of the same context. Checklist item C11 searches for them.
- **A rename is a model change.** When a term changes, in one change: move the old word into `_Avoid_`, update the definition, and rename every identifier that used the old word. Never leave the old word in the code and the new word in the glossary.

## Term fields

These fields go under the definition, in the order of the table. Each one belongs to one kind of term. Write a field only on the kinds listed for it. A field that does not apply to a term is left off the entry, except where the table says to write `none`.

| Field | Goes on | Written when | Form | Example | Leave out or write `none` when |
|---|---|---|---|---|---|
| `_Actor_` | `use case` | Step 11 of the Procedure, from the actors of the scenarios in Step 1. In Session mode, when the user settles who starts it | One or more terms of kind `actor`, separated by commas | `_Actor_: Attendee, Room manager` | No person or outside system starts it, for example a timer or an event. Write `none` and say in the definition what starts it |
| `_States_` | `entity` that has a lifecycle | Step 4 of the Procedure. In Session mode, when the user settles the states | State names in lower case. `→` means "may move to". Separate unrelated moves with `;` | `_States_: draft → confirmed → cancelled` or `_States_: open → closed; open → cancelled` | The entity has one state only. Leave the field off |
| `_Contains_` | `aggregate root` | Step 5 of the Procedure. In Session mode, when the user settles the boundary | The terms of the entities and value objects inside the aggregate, separated by commas | `_Contains_: Booking` | Never left off. Write `none` when the root has no members |
| `_Refers to by ID_` | `aggregate root` | Step 5 of the Procedure | The terms of other aggregate roots that this one holds only by ID, separated by commas | `_Refers to by ID_: Room` | The root refers to no other aggregate. Leave the field off |
| `_Raised when_` | `event` | Step 8 of the Procedure. In Session mode, when the user settles it | One phrase that names the business moment, in the words of the glossary | `_Raised when_: a booking becomes confirmed` | Never left off |
| `_Carries_` | `event` | Step 8 of the Procedure | The facts a listener needs, as glossary terms, separated by commas. Never types, never field names | `_Carries_: booking, room, attendee, time range, price` | Never left off. An event without both fields is not finished |

Rules for these fields:

- Every term named in `_Actor_`, `_Contains_`, or `_Refers to by ID_` has its own entry in the same glossary, with the matching kind. An `_Actor_` term has kind `actor`.
- Every state in `_States_` becomes a member of an enumeration in code (Step 4). Write the states in the glossary's words. Wire values are code and do not belong here.
- A `_Contains_` term has the kind `entity` or `value object`. A `_Refers to by ID_` term has the kind `aggregate root`. A term never appears in both fields of the same root.
- With two or more contexts, a fact listed under `Contract` in `GLOSSARY-MAP.md` must also appear in the event's `_Carries_` line.

## Where the glossary lives

**One context (most projects):** one `GLOSSARY.md` at the repo root.

**Two or more contexts:** one `GLOSSARY.md` inside each context's folder, and one `GLOSSARY-MAP.md` at the repo root. The map lists the contexts, where they live, and how they relate to each other:

```md
# Glossary Map

## Contexts

- [Booking](./booking/GLOSSARY.md) _(core)_: rooms, time ranges, and confirmed bookings
- [Billing](./billing/GLOSSARY.md) _(supporting)_: invoices and payments
- [Notification](./notification/GLOSSARY.md) _(generic)_: messages sent to attendees

## Words that differ across contexts

| Word | In Booking | In Billing | Decision |
|---|---|---|---|
| Attendee / Payer | the person who uses the room | the person who pays | two words, one per context |

## Relationships

Write one block per direction that carries information. Each block has four fields.

- **Booking → Billing**
  - Contract: event `BookingConfirmed(bookingId, attendeeId, price)`
  - Translation: Billing stores `attendeeId` as its `payerId`. A "booking" becomes an "invoice line".
  - Delivery: at least once. Billing must accept the same event twice.
  - Pattern: published language
- **Booking → Notification**
  - Contract: event `BookingCancelled(bookingId, attendeeId)`
  - Translation: Notification stores `attendeeId` as `recipientId`.
  - Delivery: at least once. Notification must not send the same message twice.
  - Pattern: published language
- **Billing → Booking**: none. Billing keeps its own copy of what it needs from `BookingConfirmed`.
```

Contexts do not share types. When one context needs a fact from another, the other context publishes an event or an ID. The first context keeps its own copy of what it needs. An ID that comes from another context becomes a type of the receiving context with its own name: Billing holds a `PayerId`, not Booking's `AttendeeId`. The `Translation` field records the conversion. Write each such need as one `Relationships` block.

The `Pattern` field uses one of these names:

- **published language**: the sender publishes a documented contract, and the receiver reads it. This is the default.
- **customer/supplier**: the receiver asks for changes and the sender plans them.
- **conformist**: the receiver accepts the sender's model as it is.
- **anticorruption layer**: the receiver translates the sender's model into its own at the border, so the sender's words never enter the receiver.
- **separate ways**: the two contexts do not connect.

Do not use a *shared kernel* (two contexts sharing a piece of model code) unless the user approves it. It breaks the rule that contexts do not share types.

**Words that differ across contexts.** When one real thing has two names, or one name has two meanings, add a row. A row is the first sign that you need two contexts. Add a row at Step 2 whenever the gate on borrowed words finds one.

**Going from one context to two:** when the second context appears, move the root `GLOSSARY.md` into the first context's folder, add the second context's `GLOSSARY.md`, and create `GLOSSARY-MAP.md`.

## Which structure applies

Step 2 of the skill decides:

- If `GLOSSARY-MAP.md` exists, read it to find the contexts.
- If only a root `GLOSSARY.md` exists, the project has one context.
- If neither exists, create a root `GLOSSARY.md` in Step 2, when you write the first term. In Session mode, create it when the first term is resolved.

When there are several contexts, decide which one the current feature belongs to. If it is unclear, ask the user.