# Java reference for domain-design

Follow this file for every Java class you write or change under this skill. The skill's steps say what to build. This file says which Java construct to use for each concept. Do not invent a different form. If a form here cannot work in the project, write the reason in `design.md` and ask the user.

The code below uses the meeting-room domain. Copy the shape, not the domain.

**Version check.** Records are used for value objects and events. Read the project's Java version first. If the project's version has no records, write the same thing as a `final` class: `private final` fields, a constructor that validates, accessors, and `equals`, `hashCode`, and `toString` over all fields. I have not verified the release in which records appeared, so check it in the project's build file.

## 1. Construct table

| Concept | Required form in Java | Forbidden |
|---|---|---|
| Value object | A `record`. A **compact constructor** that validates and rejects `null`. Behaviour as methods. | A class with setters. A record that holds a mutable list without copying it. A public constructor that skips validation. |
| Validated ID | A `record RoomId(String value)` whose compact constructor rejects blank values. | A bare `String` or `long` for an ID in the model, use cases, or ports. |
| Money and quantities | A `record Money(long minorUnits, Currency currency)`. | `double`, `float`, or a bare `BigDecimal` for money. |
| Enumeration | A Java `enum` with an explicit wire value per constant and a `fromWire(String)` that rejects unknown values. Switches list every constant. See the matrix file. | A `String` or `int` for a status. `Enum.valueOf` on raw input. |
| Entity member of an aggregate | A package-private `final class` in the aggregate's package. `private final` ID. `equals` and `hashCode` over the ID only. | A public member class. A record, because a record's equality covers all fields. |
| Aggregate root | A `public final class` with `private` fields. Members are package-private in the same package. Operations are public methods named after business actions. | Setters. Public fields. An operation that runs a query or saves. |
| Rebuilding from storage | `State state()` returns a `record State` of plain data. `static RoomDay restore(State s)` runs the value-object constructors and raises no events. | Public setters for the repository's use. |
| Domain event | A `record` implementing the `DomainEvent` interface. Lists are copied with `List.copyOf` in the compact constructor. Built only inside the aggregate. | A mutable event class. An event built in a use case or an adapter. |
| Domain service | A `final` class with a private constructor and `static` pure methods. | A service with fields that are collaborators. |
| Domain error | A `RuleViolation extends RuntimeException` hierarchy: one subclass per rule (`Overlap`, `DayFull`). Port errors `NotFound` and `Conflict` live in the `ports` package. | Throwing `RuntimeException` or `IllegalArgumentException` directly. Letting a driver exception cross a port. |
| Interface (port) | A small `interface` in the `ports` package. Types in the signature come from `model` only. | A name that holds a vendor word. An interface with more than about five methods. A name with an `I` prefix. |
| Clock | `java.time.Clock`, injected. Use cases call `clock.instant()`. The model receives `Instant now` as a parameter. | Any `now()` call without a `Clock` argument. |
| ID generator | An `IdGenerator` interface in `ports`. | `UUID.randomUUID()` inside the model or a use case. |
| Use case | A `public final class` with `private final` interface fields, **one** constructor that takes all of them, and one method `execute(Input)`. Input and output are records. | A constructor that creates a collaborator. Field injection. A `static` method that holds state. |
| Injection | Constructor parameters only. | `static` collaborator fields. `getInstance()`. Container lookups such as `getBean(`. Container annotations (for example `@Autowired`, `@Inject`, `@Component`, `@Service`) on the model, use cases, or ports. |
| Composition root | One class, such as `CompositionRoot` or the `main` class. With a dependency-injection container, the container's configuration classes are the composition root. They are the only place that creates adapters and use cases. | Adapter construction anywhere else except tests. |
| Fake | A class in the test source set. It stores the aggregate's `State`, not the object, and calls `restore` in `get`. | A scripted mock whose answers are set per test. |
| Contract test | An `abstract class RoomDayRepositoryContract` with `abstract RoomDayRepository create()`. Two subclasses: one for the fake, one for the real adapter. | Testing the fake and the adapter with different cases. |

## 2. Templates

### Value object

```java
public record TimeRange(Instant start, Instant end) {
    public TimeRange {                                     // compact constructor: runs on every creation
        Objects.requireNonNull(start);
        Objects.requireNonNull(end);
        if (!end.isAfter(start)) throw new RangeNotPositive();                      // R2
        if (Duration.between(start, end).compareTo(Duration.ofHours(4)) > 0)
            throw new RangeTooLong();                                               // R2
        if (!start.atZone(ZoneOffset.UTC).toLocalDate().equals(end.atZone(ZoneOffset.UTC).toLocalDate()))
            throw new RangeCrossesDay();                                            // R2: use the room's zone when the project has one
    }
    public LocalDate date() { return start.atZone(ZoneOffset.UTC).toLocalDate(); }
    public boolean overlaps(TimeRange o) { return start.isBefore(o.end) && o.start.isBefore(end); }
}
```

### Aggregate, state, and restore

```java
package booking.model.roomday;

public final class RoomDay {
    private final RoomId roomId;
    private final LocalDate date;
    private final List<Booking> bookings = new ArrayList<>();   // Booking is package-private
    private final List<DomainEvent> events = new ArrayList<>();

    public static RoomDay empty(RoomId roomId, LocalDate date) { return new RoomDay(roomId, date); }

    public void confirm(BookingId id, AttendeeId who, TimeRange range, AttendeeCount count,
                        AttendeeCount roomCapacity, Money price, Instant now) {
        if (!range.date().equals(date)) throw new WrongDate();
        if (count.exceeds(roomCapacity)) throw new OverCapacity();                     // R3
        long confirmed = 0;
        for (Booking b : bookings) {
            if (!b.isConfirmed()) continue;
            confirmed++;
            if (b.range().overlaps(range)) throw new Overlap();                        // R1
        }
        if (confirmed >= MAX_CONFIRMED_PER_DAY) throw new DayFull();                   // R5
        bookings.add(Booking.confirmed(id, who, range, price));
        events.add(new BookingConfirmed(id, roomId, who, range, price, now));
    }

    public List<DomainEvent> pullEvents() { var e = List.copyOf(events); events.clear(); return e; }

    public record State(String roomId, String date, List<BookingState> bookings) {}   // primitives allowed here only
    public State state() { /* ... */ }
    public static RoomDay restore(State s) { /* runs the value-object constructors; raises no events */ }
}
```

### Ports

```java
package booking.ports;

public interface RoomDayRepository {
    RoomDay get(RoomId roomId, LocalDate date);   // an empty RoomDay if none exists
    void save(RoomDay day);                        // also stores day.pullEvents() in the outbox, in the same transaction
}
public interface IdGenerator { BookingId newBookingId(); }
// the clock is java.time.Clock
```

### Use case

```java
public final class ConfirmBooking {
    private final RoomDayRepository roomDays;
    private final RoomRepository rooms;
    private final Clock clock;
    private final IdGenerator ids;

    public ConfirmBooking(RoomDayRepository roomDays, RoomRepository rooms, Clock clock, IdGenerator ids) {
        this.roomDays = roomDays; this.rooms = rooms; this.clock = clock; this.ids = ids;
    }

    public ConfirmBookingResult execute(ConfirmBookingInput in) {
        var range = new TimeRange(in.start(), in.end());
        var room = rooms.get(in.roomId());
        var day = roomDays.get(in.roomId(), range.date());
        var price = Pricing.priceFor(room.rate(), range);                  // pure function: created directly
        day.confirm(ids.newBookingId(), in.attendeeId(), range, in.count(), room.capacity(), price, clock.instant());
        roomDays.save(day);
        return /* result */;
    }
}
```

### Adapter, composition root, fake, contract test

```java
public final class SqlRoomDayRepository implements RoomDayRepository { /* adapters.outbound */ }   // the compiler checks "implements"

public final class CompositionRoot {                       // the ONLY place that creates adapters
    static ConfirmBooking confirmBooking(DataSource ds) {
        return new ConfirmBooking(new SqlRoomDayRepository(ds), new SqlRoomRepository(ds), Clock.systemUTC(), new UuidIdGenerator());
    }
}

final class InMemoryRoomDayRepository implements RoomDayRepository {     // test source set
    private final Map<Key, RoomDay.State> states = new HashMap<>();       // stores State, never the object
    public RoomDay get(RoomId id, LocalDate d) {
        var s = states.get(new Key(id, d));
        return s == null ? RoomDay.empty(id, d) : RoomDay.restore(s);
    }
    public void save(RoomDay day) { states.put(Key.of(day), day.state()); }
}

abstract class RoomDayRepositoryContract {
    abstract RoomDayRepository create();
    // save then get returns equal state; get of a missing day returns an empty day; a stale save throws Conflict
}
```

### Table-driven rule test

```java
@ParameterizedTest(name = "R2 {0}")                       // or the project's equivalent
@MethodSource("r2Cases")
void r2_timeRange(String name, Instant start, Instant end, Class<? extends RuleViolation> expected) {
    if (expected == null) { assertDoesNotThrow(() -> new TimeRange(start, end)); return; }
    assertThrows(expected, () -> new TimeRange(start, end));
}
static Stream<Arguments> r2Cases() {
    return Stream.of(
        Arguments.of("valid one hour", at(9, 0), at(10, 0), null),
        Arguments.of("zero length", at(9, 0), at(9, 0), RangeNotPositive.class),
        Arguments.of("five hours", at(8, 0), at(13, 0), RangeTooLong.class));
}
```

Name tests `R<n>_<name>` for rules and `S<n>_<name>` for scenarios.

### Identifiers and enumerations

```java
public record AppId(String value) {                    // AppId and OrgId are different types
    public AppId { Objects.requireNonNull(value); if (value.isBlank()) throw new InvalidId("AppId"); }
}
public record OrgId(String value) { /* same shape */ }

public enum Status {
    CONFIRMED("confirmed"), CANCELLED("cancelled");     // wire values are explicit strings
    private final String wire;
    Status(String wire) { this.wire = wire; }
    public String wire() { return wire; }
    public static Status fromWire(String raw) {
        for (Status s : values()) if (s.wire.equals(raw)) return s;
        throw new InvalidStatus(raw);
    }
}

// Two parameters of the same type: one input record, so the names carry the meaning.
public record TransferInput(AccountId from, AccountId to, Money amount) {}
```

Rules:

- One record per kind of identifier, per context. Passing an `OrgId` where an `AppId` is expected fails to compile.
- Raw strings become identifiers and statuses at the edges (handlers, consumers, adapters), through the constructor or `fromWire`. Inside the model, use cases, and ports, pass the typed value.
- Never persist `ordinal()`. Persist the explicit wire value.
- A method with two or more parameters of the same type takes an input record.
- Before you rely on a record or enum in a persistence-library mapping or a JSON payload, run one round trip in the project at Step 10: write, read, compare.

## 3. Traps

- **Records are shallow.** A `List` component is still a mutable reference. Copy it with `List.copyOf` in the compact constructor, and never return the internal list from an entity.
- **Record equality is by all components.** That is right for value objects and events. It is wrong for entities, which use plain classes with equality over the ID.
- **`BigDecimal.equals` compares scale.** `2.0` and `2.00` are not equal. Hold money as integer minor units.
- **`Instant.now()`, `LocalDate.now()`, and the like read the system clock.** `java.time.Clock` was added in Java 1.8 so that "alternate clocks [can] be plugged in". Use `clock.instant()` in use cases and pass `now` into the model.
- **Package-private is the encapsulation tool.** Root and members share a package. Put each aggregate in its own package so nothing else can reach the members.
- **Libraries that build objects by reflection** may require a non-final class and a non-public no-argument constructor. See section 6.

## 4. Checklist searches

Use these as starting patterns. Run them through the project's own build and lint scripts where it has them, and adapt the paths.

| Check | Search or command |
|---|---|
| C1 | In `model`, `usecases`, and `ports`, search the import lines for the adapters package and for any database, transport, or framework package. |
| C2 | For each adapter in the seam table, search for `new <Adapter>(` outside the composition root and the tests. |
| C3 | Search for `static` fields of collaborator type, `getInstance(`, and container lookups such as `getBean(`. Search the model, use cases, and ports for container annotations. |
| C4 | Search the model and use cases for `.now()` with empty parentheses, `System.currentTimeMillis(`, `UUID.randomUUID(`, `new Random(`, `Math.random(`, `System.getenv(`. |
| C9 | Search for `public void set` in aggregates. Under the ORM exception, search for calls to setters on aggregates outside their package. |
| C11 | Search all identifiers in the context for each `_Avoid_` word, case-insensitively. |
| C12 | In `model`, `usecases`, and `ports`, search for `String` and `long` parameters and fields named `*Id`, and for any `double`, `float`, or `BigDecimal` field. `State` records and the value object's own definition are exempt. |
| C13 | Every value object and event is a `record`, or a class whose fields are all `private final`. Search for non-final fields in them. |
| C14 | Search for `new <EventName>(` outside the aggregate's package. It must return nothing. |
| C17 | Search the use-case tests for a mocking library applied to a port. |
| C19 | Every kind of identifier is its own `record`, and every closed set is an `enum`. Search the model, use cases, and ports for `String` or `long` used as an identifier or status. It must return nothing. |
| C20 | List the methods in the model, use cases, and ports that take two or more parameters of the same identifier or value-object type. Each takes an input record. |

## 5. Enforcement

- Use package-private visibility for members. Where the project uses the module system, export only `ports` and `usecases`.
- Add an architecture test that fails when a class in `model`, `usecases`, or `ports` imports from `adapters`, so C1 fails the build. Reuse the tool the project already has, or ask the user before adding one.

## 6. Under the ORM exception

The aggregate may be the library's entity class:

- Annotations on fields are allowed. If the library needs a no-argument constructor, make it `protected` or package-private, and have it leave the object invalid until the library fills it.
- If the library needs a non-final class, the aggregate is not `final`. Say so in a comment.
- E4 is enforced by the absence of public setters, and by search (C9).
- `State` and `restore` are not needed, because the library fills the object.
