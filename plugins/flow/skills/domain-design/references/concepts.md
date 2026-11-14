# Concepts used by the domain-design skill

Read this whole file before you do anything else in the skill. Every word the skill uses is defined here, with an example.

## The running example

All examples use one domain: a **meeting-room booking system**.

- People book rooms for time ranges.
- Rooms have a capacity and equipment.
- Bookings cost money.
- A separate finance area makes invoices.

Do not copy the example domain into the user's feature. Copy the shape of the reasoning.

## How to read the table

- **Plain meaning** says what the word means in everyday language.
- **Example** shows it in the running domain.
- **How to spot it in code** tells you what to look for or write, in any language.

## The words

| Word | Plain meaning | Example | How to spot it in code |
|---|---|---|---|
| **Model** | The code that holds the business rules. | `TimeRange`, `RoomDay`, `Booking` | Types with validating constructors and methods named after business actions |
| **Glossary** | A list of words. Each word has one meaning and a list of words to avoid. | "Booking: a confirmed claim on one room for one time range. Avoid: reservation, slot." | A `GLOSSARY.md` file (see `references/glossary-format.md`) |
| **Context** | A region of the product where every word has exactly one meaning. | In *Booking*, "Attendee" is the person using the room. In *Billing*, "Payer" is the one who pays. It is the same person with two words, so these are two contexts. | A top-level folder per context |
| **Context type** | How much care a context deserves: **core** (what makes the product valuable), **supporting** (needed, not special), or **generic** (a solved problem). | *Booking* is core. *Billing* is supporting. *Notification* is generic. | A `_Type_` line in the context's glossary |
| **Value object** | A small, unchangeable thing defined by its values. It has no ID. It checks itself when created. Two equal ones are interchangeable. | `TimeRange(start, end)`: end after start, at most 4 hours. `Money(amount, currency)`. | A constructor that validates; no setters; compared by content |
| **Entity** | A thing with an identity that stays the same while its details change. | Booking #123 stays booking #123 when its time changes. | Has an ID; has methods that change its state |
| **Rule** (also called invariant) | A sentence that must always be true. | "Two confirmed bookings of one room never overlap." | A check inside a model method, plus one test named after the rule |
| **Aggregate** | A group of entities and value objects that must stay consistent together. It has one entry object, the **root**. Outsiders use only the root. The group is loaded and saved as one unit. | `RoomDay` is one room's bookings for one date. The root is `RoomDay`. The member is `Booking`. | One repository per aggregate; one transaction per save |
| **Domain event** | An unchangeable record that something happened. Named in the past tense. | `BookingConfirmed(bookingId, roomId, at)` | A plain data type, created by a model method |
| **Domain service** | A pure calculation that belongs to no single entity. It has no outside access. | `priceFor(rate, timeRange) -> Money` | A function that takes values and returns a value |
| **Use case** | One thing the application can be asked to do. It loads the aggregate, calls the model, and saves. Events raised by the model are stored with the save. | `ConfirmBooking` | One class or function per user intent |
| **Collaborator** | Anything a piece of code needs that touches the outside world or changes between runs: a database, a network, a file, the clock, random numbers, an ID generator, configuration, another use case. | The clock that stamps `BookingConfirmed` | Any call like `now()`, `random()`, `uuid()`, or `connect(...)` |
| **Interface** (also called **port**) | A contract: a list of operations with types. It is written in business words. The code that needs it owns it. | `RoomDayRepository { get(roomId, date); save(roomDay) }` and `Clock { now() }` | An interface, protocol, trait, or abstract class, depending on the language |
| **Repository** | An interface for loading and saving one aggregate. | `RoomDayRepository` | `get(...)` and `save(...)` in business words |
| **Gateway** | An interface to a third-party service. | `PaymentGateway { charge(money, payer) }` | An interface named after the business need, not the vendor |
| **Adapter** | Code that implements an interface using a real technology. | `SqlRoomDayRepository`, `SystemClock` | A class that talks to a database, network, or the operating system |
| **Actor** | A person or an outside system that asks the application to do something. | Sam, an attendee, who asks to confirm a booking. A nightly job that expires unpaid bookings. | A user role, a client of an API, a scheduler. Each starts a use case |
| **Driving side** | Code that calls us. It is the entry point. Code here is an **inbound adapter**. | An HTTP handler for `POST /bookings`, a queue consumer, a scheduled job | Handlers, command-line commands, consumers. They call use cases |
| **Driven side** | What we call. These are interfaces implemented by **outbound adapters**. | `RoomDayRepository`, `Clock`, `EmailSender` | Interfaces under `ports/`, implemented under `adapters/outbound/` |
| **Seam** | A place where behaviour can be swapped without editing the code at that place. In practice, it is any collaborator received through an interface parameter. | `ConfirmBooking` receives a `Clock`. Production passes `SystemClock`. A test passes `FixedClock`. | Constructor parameters typed as interfaces |
| **Composition root** | The one place, in startup code, where adapters are created and handed to use cases. | `main()` | A single startup file |
| **System of record** | The store that holds every field of an entity. It is the truth. | The main database | One repository per aggregate |
| **Index** and **entry** | An index is a derived store that holds only the fields used to filter or score a search. An entry is the small record kept there. It can be rebuilt from the system of record. | A search index holding `capacity`, `equipment`, `building`, and `descriptionVector` | A separate small type, built from the model by one function |
| **Hit** | A search result: an ID and a score, nothing else. | `Hit(roomId, 0.83)` | A tiny type returned by an index |
| **Outbox** | A row written in the same transaction as a change. It says "deliver this event". A worker delivers it later. | Row `BookingConfirmed, pending` | A table plus a worker |

## Glossary format

The format of glossary files, and where they live, is in `references/glossary-format.md`. Read it at Step 2 of the skill.

## Test questions

Use these when a step asks you to classify something.

| Question | If yes |
|---|---|
| If two have identical fields, are they still different things? | Entity |
| Would you "replace" it rather than "edit" it? | Value object |
| Is it a pure calculation that no entity owns? | Domain service |
| Is it something that happened that the business cares about? | Domain event |
| Would a test want to replace it, or does it touch the outside world or vary between runs? | Collaborator |
| Must these things be consistent with each other at the same instant? | Same aggregate |
| May these two things disagree for a few seconds without business harm? | Separate aggregates, linked by an event |
