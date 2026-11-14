# TypeScript reference for domain-design

Follow this file for every TypeScript module you write or change under this skill. The skill's steps say what to build. This file says which TypeScript construct to use for each concept. Do not invent a different form. If a form here cannot work in the project, write the reason in `design.md` and ask the user.

The code below uses the meeting-room domain. Copy the shape, not the domain.

**Compiler check.** Run the compiler in its strict mode over every layer. Types are erased at run time, so several rules below are enforced only by the compiler. Where a rule must also hold at run time, this file says so.

## 1. Construct table

| Concept | Required form in TypeScript | Forbidden |
|---|---|---|
| Value object | A class with a **private constructor**, `readonly` fields, a static `create(...)` that validates and throws a rule error, an `equals` method. | An object literal type. A class with a public constructor. A mutable field. |
| Validated ID | A **branded type** plus one `parse` function that is the only place that casts: `type RoomId = string & { readonly __brand: "RoomId" }`. | `type RoomId = string`. A bare `string` or `number` for an ID. |
| Money and quantities | A value object `Money` holding integer minor units and a currency. | `number` with decimals for money. |
| Enumeration | A string-literal union with a `const` array: `const STATUSES = ["confirmed", "cancelled"] as const; type Status = typeof STATUSES[number]`. Switches end with a `never` check. See the matrix file. | Raw `string` for a status. `enum` with default numeric values. |
| Entity member of an aggregate | A class in the aggregate's module, not exported from the module. `readonly id`. `equals` over the ID. | An exported member class that other modules can build. |
| Aggregate root | A class with **`#` private fields** (hard private at run time), a private constructor, a static factory, and methods named after business actions. | `private` alone for state. Public fields. Setters. An operation that runs a query or saves. |
| Rebuilding from storage | `state()` returns a plain readonly `State` object. `static restore(state)` runs the value-object constructors and raises no events. | Setting fields from a repository. |
| Domain event | A `readonly` object type with a `type` discriminant. Built only inside the aggregate. Frozen with `Object.freeze` when built. | A mutable event. An event built in a use case or an adapter. |
| Domain service | An exported pure function. | A class with collaborators. |
| Domain error | A `RuleViolation extends Error` hierarchy with a `kind` field: one subclass per rule. Port errors `NotFound` and `Conflict` live in `ports/`. | Throwing a bare `Error` or a string. A driver error crossing a port. |
| Interface (port) | An `interface` in `ports/`. Methods that can block return `Promise`. Types in the signature come from `model/` only. | An interface that names a vendor. An interface with more than about five methods. A name with an `I` prefix. |
| Use case | A class whose constructor takes every collaborator as a `private readonly` parameter typed as a port. One method `run(input)`. | A constructor that creates a collaborator. A function that imports an adapter. |
| Injection | Constructor parameters only. | `export const repo = new SqlRepo()`. A module-level `let` that holds a collaborator. A default parameter that builds an adapter. A container lookup in the model or a use case. |
| Composition root | One module, such as `compose.ts`. It creates adapters and use cases. With a dependency-injection container, its configuration module is the composition root, and the model, use cases, and ports carry no container decorators or imports. | Adapter construction anywhere else except tests. |
| Adapter conformance | `class SqlRoomDayRepository implements RoomDayRepository`. | A structural match with no `implements`, because a later change can break it silently. |
| Fake | A class in the tests. It stores the aggregate's `State`, not the object, and calls `restore` in `get`. | A scripted mock whose answers are set per test. |
| Contract test | A function `roomDayRepositoryContract(make)` that registers the tests. It is called once with the fake and once with the real adapter. | Testing the fake and the adapter with different cases. |

## 2. Templates

### Branded ID

```ts
declare const brand: unique symbol;
export type RoomId = string & { readonly [brand]: "RoomId" };
export type OrgId = string & { readonly [brand]: "OrgId" };

export const parseRoomId = (raw: string): RoomId => {
  if (raw.trim() === "") throw new InvalidId("RoomId");
  return raw as RoomId;                       // the ONLY cast
};
```

### Value object

```ts
export class TimeRange {
  private constructor(readonly start: number, readonly end: number) {}   // epoch milliseconds: Date is mutable

  static create(start: number, end: number): TimeRange {
    if (end <= start) throw new RangeNotPositive();                      // R2
    if (end - start > 4 * 3_600_000) throw new RangeTooLong();           // R2
    if (utcDay(start) !== utcDay(end)) throw new RangeCrossesDay();      // R2
    return new TimeRange(start, end);
  }
  date(): string { return utcDay(this.start); }
  overlaps(o: TimeRange): boolean { return this.start < o.end && o.start < this.end; }
  equals(o: TimeRange): boolean { return this.start === o.start && this.end === o.end; }
}
```

### Aggregate, state, and restore

```ts
export class RoomDay {
  readonly #bookings: Booking[] = [];          // # is private at run time
  readonly #events: DomainEvent[] = [];
  private constructor(readonly roomId: RoomId, readonly date: string) {}

  static empty(roomId: RoomId, date: string): RoomDay { return new RoomDay(roomId, date); }

  confirm(id: BookingId, who: AttendeeId, range: TimeRange, count: AttendeeCount,
          roomCapacity: AttendeeCount, price: Money, now: number): void {
    if (range.date() !== this.date) throw new WrongDate();
    if (count.exceeds(roomCapacity)) throw new OverCapacity();                       // R3
    const confirmed = this.#bookings.filter((b) => b.isConfirmed);
    if (confirmed.some((b) => b.range.overlaps(range))) throw new Overlap();         // R1
    if (confirmed.length >= MAX_CONFIRMED_PER_DAY) throw new DayFull();              // R5
    this.#bookings.push(Booking.confirmed(id, who, range, price));
    this.#events.push(Object.freeze({ type: "BookingConfirmed", id, roomId: this.roomId, who, range, price, at: now }));
  }

  pullEvents(): readonly DomainEvent[] { const e = [...this.#events]; this.#events.length = 0; return e; }
  state(): RoomDayState { /* plain readonly data */ }
  static restore(s: RoomDayState): RoomDay { /* runs the value-object constructors; raises no events */ }
}
```

### Ports

```ts
export interface RoomDayRepository {
  get(roomId: RoomId, date: string): Promise<RoomDay>;   // an empty RoomDay if none exists
  save(day: RoomDay): Promise<void>;                     // also stores day.pullEvents() in the outbox, in the same transaction
}
export interface Clock { now(): number }
export interface IdGenerator { newBookingId(): BookingId }
```

### Use case

```ts
export class ConfirmBooking {
  constructor(
    private readonly roomDays: RoomDayRepository,
    private readonly rooms: RoomRepository,
    private readonly clock: Clock,
    private readonly ids: IdGenerator,
  ) {}

  async run(input: ConfirmBookingInput): Promise<ConfirmBookingResult> {
    const range = TimeRange.create(input.start, input.end);
    const room = await this.rooms.get(input.roomId);
    const day = await this.roomDays.get(input.roomId, range.date());
    const price = priceFor(room.rate, range);                    // pure function: created directly
    day.confirm(this.ids.newBookingId(), input.attendeeId, range, input.count, room.capacity, price, this.clock.now());
    await this.roomDays.save(day);
    return /* result */;
  }
}
```

### Adapter, composition root, fake, contract test

```ts
export class SqlRoomDayRepository implements RoomDayRepository { /* adapters/outbound */ }

// compose.ts: the ONLY place that creates adapters
export const compose = (config: Config) => {
  const db = connect(config.dbUrl);
  const confirm = new ConfirmBooking(new SqlRoomDayRepository(db), new SqlRoomRepository(db), systemClock, new UuidGenerator());
  return new HttpServer([new PostBookingHandler(confirm)]);
};

class InMemoryRoomDayRepository implements RoomDayRepository {       // tests
  readonly #states = new Map<string, RoomDayState>();                 // stores State, never the object
  async get(id: RoomId, date: string) {
    const s = this.#states.get(`${id}|${date}`);
    return s ? RoomDay.restore(s) : RoomDay.empty(id, date);
  }
  async save(day: RoomDay) { this.#states.set(`${day.roomId}|${day.date}`, day.state()); }
}

export const roomDayRepositoryContract = (make: () => Promise<RoomDayRepository>) => {
  // save then get returns equal state; a missing day is empty; a stale save throws Conflict
};
```

### Table-driven rule test

```ts
const cases: ReadonlyArray<{ name: string; start: number; end: number; error?: new () => Error }> = [
  { name: "valid one hour", start: at(9, 0), end: at(10, 0) },
  { name: "zero length", start: at(9, 0), end: at(9, 0), error: RangeNotPositive },
  { name: "five hours", start: at(8, 0), end: at(13, 0), error: RangeTooLong },
];
describe("R2 time range", () => {
  it.each(cases)("$name", ({ start, end, error }) => {      // or the runner's table feature, or a plain loop
    if (error) expect(() => TimeRange.create(start, end)).toThrow(error);
    else expect(() => TimeRange.create(start, end)).not.toThrow();
  });
});
```

Name tests `R<n>: <name>` for rules and `S<n>: <name>` for scenarios.

### Identifiers and enumerations

```ts
export type AppId = string & { readonly [brand]: "AppId" };    // each brand has its own label, so AppId and OrgId differ
export type OrgId = string & { readonly [brand]: "OrgId" };    // brand: see "Branded ID" above

export const STATUSES = ["confirmed", "cancelled"] as const;   // wire values are the strings themselves
export type Status = (typeof STATUSES)[number];
export const parseStatus = (raw: string): Status => {
  if (!(STATUSES as readonly string[]).includes(raw)) throw new InvalidStatus(raw);
  return raw as Status;                                         // the only cast for Status
};
const assertNever = (x: never): never => { throw new Error(`unhandled: ${String(x)}`); };
// every switch over Status ends with: default: return assertNever(status);

// Two parameters of the same type: one input object, so the names carry the meaning.
export interface TransferInput { readonly from: AccountId; readonly to: AccountId; readonly amount: Money }
```

Rules:

- One brand per kind of identifier, per context. The compiler rejects an `OrgId` where an `AppId` is expected. A plain `type AppId = string` does not, so never write it.
- Raw strings become identifiers and statuses at the edges (handlers, consumers, adapters), through the `parse...` functions. Inside the model, use cases, and ports, pass the typed value.
- Do not use `enum`. Use the string-literal union above, so the wire value is the value.
- A function or method with two or more parameters of the same type takes an input object.
- Before you rely on a brand or a union in a persistence-library mapping or a JSON payload, run one round trip in the project at Step 10: write, read, compare.

## 3. Traps

- **Structural typing treats equal shapes as equal.** `type AppId = string` and `type OrgId = string` are the same type, so passing one for the other compiles. Only a brand, or a class with a private member, makes two types incompatible.
- **A brand exists only at compile time.** It is erased at run time, so the `parse` function must validate. Values that come from outside (a request body, a database row) enter the model only through `parse`.
- **`private` is soft.** The TypeScript handbook says it is enforced only during type checking, and bracket access can still read it. Use `#` fields for aggregate state, which stay private after compilation.
- **`readonly` is compile-time only.** It blocks assignment outside the constructor, but nothing stops a cast. Use `Object.freeze` for events.
- **`Date` is mutable.** Hold time as epoch milliseconds in the model, and convert at the edges.
- **`#` fields are not serialized.** `JSON.stringify` on an aggregate gives nothing useful, which is intended. Persist through `state()`.
- **Async leaks into ports.** Repositories return `Promise`. The model stays synchronous. Never make a model method `async`.

## 4. Checklist searches

Use these as starting patterns. Run them through the project's own scripts where it has them, and adapt the paths.

| Check | Search or command |
|---|---|
| C1 | In `model/`, `usecases/`, and `ports/`, search the import lines for `adapters/` and for any database, transport, or framework package. The project's import-restriction rule should enforce it. |
| C2 | For each adapter in the seam table, search for `new <Adapter>(` outside `compose.ts` and the tests. |
| C3 | Search for `export const \w+ = new `, module-level `let`, and default parameters that call `new`. Search the model, use cases, and ports for container decorators. |
| C4 | Search the model and use cases for `Date.now(`, `new Date()` with no argument, `Math.random(`, `crypto.randomUUID(`, `process.env`. |
| C9 | `#` fields make this a run-time error. Under the ORM exception, search for assignments to the aggregate's fields outside its module. |
| C11 | Search all identifiers in the context for each `_Avoid_` word, case-insensitively. |
| C12 | In `model/`, `usecases/`, and `ports/`, search for parameters and fields named `*Id`, `amount`, `price`, `currency`, `status` typed `string` or `number`. `State` types and the brand's own `parse` function are exempt. |
| C13 | Search for non-`readonly` fields in value objects and events. It must return nothing. |
| C14 | Search for each event's `type: "<EventName>"` outside the aggregate's module. It must return nothing. |
| C17 | Search the use-case tests for a mocking facility applied to a port. |
| C19 | Every kind of identifier has its own brand, and every closed set is a string-literal union. Search the model, use cases, and ports for `type \w+ = string` and for `string` used as an identifier or status. It must return nothing for these types. |
| C20 | List the functions and methods in the model, use cases, and ports that take two or more parameters of the same identifier or value-object type. Each takes an input object. |

## 5. Enforcement

- Turn on the compiler's strict mode for every layer.
- Add the project's import-restriction rule so C1 fails the build. Reuse the tool the project already has, or ask the user before adding one.
- Keep `implements` on every adapter.

## 6. Under the ORM exception

The aggregate may be the library's entity class:

- Decorators and public fields may be required. E4 is then enforced by `readonly` where the library allows it, by search (C9), and by the import rule.
- Keep lifecycle hooks mechanical (E1).
- `state()` and `restore` are not needed, because the library fills the object.
- Operations stay methods on the class. They never call the library.
