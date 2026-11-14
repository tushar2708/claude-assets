# Python reference for domain-design

Follow this file for every Python module you write or change under this skill. The skill's steps say what to build. This file says which Python construct to use for each concept. Do not invent a different form. If a form here cannot work in the project, write the reason in `design.md` and ask the user.

The code below uses the meeting-room domain. Copy the shape, not the domain.

**Version check.** Read the project's Python version first. `dataclasses` needs 3.7. `Protocol` needs 3.8. `slots=True` on a dataclass needs 3.10. Leave `slots=True` out on older versions.

**Type checker.** In Python the interface check is done by the project's type checker, not by the runtime. Use the checker the project already runs, in its strictest configured mode, over the model, use cases, ports, and the composition root.

## 1. Construct table

| Concept | Required form in Python | Forbidden |
|---|---|---|
| Value object | `@dataclass(frozen=True, slots=True)` with a `__post_init__` that validates and raises a rule error. Behaviour as methods. | A dataclass without `frozen=True`. A dict. A tuple. A class with setters. |
| Validated ID | A frozen dataclass around the primitive: `@dataclass(frozen=True) class RoomId: value: str`, validated in `__post_init__`. | A bare `str` or `int` for an ID. `NewType` as the only protection, because it does nothing at run time. |
| Money and quantities | A value object `Money(minor_units: int, currency: Currency)`. | `float` for money. A bare `Decimal` passed around. |
| Entity member of an aggregate | A plain class in the aggregate's module. Names start with `_`. `__eq__` and `__hash__` over the ID only. | A dataclass with public mutable fields. |
| Aggregate root | A plain class (not a dataclass). State is in `_`-prefixed attributes. Read access through `@property`. Operations are methods named after business actions. | Public attributes that outside code assigns. Setters. An operation that runs a query or saves. |
| Rebuilding from storage | `state()` returns a frozen `State` dataclass. `@classmethod restore(cls, state)` runs the value-object constructors and raises no events. | Setting `_` attributes from a repository. |
| Domain event | A frozen dataclass. Collections are `tuple`, not `list`. Built only inside the aggregate. | A mutable event. An event built in a use case or an adapter. |
| Domain service | A module-level function with typed parameters and a typed result. | A class with collaborators. |
| Domain error | A hierarchy: `class RuleViolation(Exception)`, one subclass per rule. Port errors `NotFound` and `Conflict` live in the `ports` module. | Raising `Exception`, `ValueError`, or `AssertionError` for a rule. A driver exception crossing a port. |
| Enumeration | `enum.Enum` with explicit string values. See the matrix file. | Raw strings or integers for a status. |
| Interface (port) | A `typing.Protocol` class in the `ports` module. Types in the signature come from `model` only. | An abstract base class inside the model. A name that holds a vendor word. A protocol with more than about five methods. |
| Use case | A class whose `__init__` takes every collaborator, typed as a `Protocol`, and stores it in a `_` attribute. One method `run(input)`. | A default argument that builds an adapter. An `__init__` that creates a collaborator. |
| Injection | `__init__` parameters only. | Module-level instances of collaborators. A function default such as `clock=SystemClock()`. A container or registry looked up from inside the model or a use case. |
| Composition root | One function, such as `build_app(config)` in `app.py`. It creates adapters and use cases. | Adapter construction anywhere else except tests. With a dependency-injection container, its configuration module is the composition root, and the model, use cases, and ports carry no container decorators or imports. |
| Fake | A class in the tests. It stores the aggregate's `State`, not the object, and calls `restore` in `get`. | A scripted mock whose answers are set per test. |
| Contract test | A fixture parametrized over the fake and the real adapter. Every contract test function runs against both. | Testing the fake and the adapter with different cases. |

## 2. Templates

### Value object

```python
@dataclass(frozen=True, slots=True)
class TimeRange:
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.start.tzinfo is None or self.end.tzinfo is None:
            raise RangeNotAware()
        if self.end <= self.start:
            raise RangeNotPositive()                       # R2
        if self.end - self.start > timedelta(hours=4):
            raise RangeTooLong()                           # R2
        if self.start.date() != self.end.date():
            raise RangeCrossesDay()                        # R2

    def date(self) -> date: return self.start.date()
    def overlaps(self, other: "TimeRange") -> bool: return self.start < other.end and other.start < self.end
```

### Aggregate, state, and restore

```python
class RoomDay:
    def __init__(self, room_id: RoomId, on_date: date) -> None:
        self._room_id = room_id
        self._date = on_date
        self._bookings: list[_Booking] = []
        self._events: list[DomainEvent] = []

    @classmethod
    def empty(cls, room_id: RoomId, on_date: date) -> "RoomDay": return cls(room_id, on_date)

    def confirm(self, booking_id: BookingId, attendee_id: AttendeeId, rng: TimeRange,
                count: AttendeeCount, room_capacity: AttendeeCount, price: Money, now: datetime) -> None:
        if rng.date() != self._date: raise WrongDate()
        if count.exceeds(room_capacity): raise OverCapacity()                      # R3
        confirmed = [b for b in self._bookings if b.is_confirmed]
        if any(b.range.overlaps(rng) for b in confirmed): raise Overlap()          # R1
        if len(confirmed) >= MAX_CONFIRMED_PER_DAY: raise DayFull()                # R5
        self._bookings.append(_Booking.confirmed(booking_id, attendee_id, rng, price))
        self._events.append(BookingConfirmed(booking_id, self._room_id, attendee_id, rng, price, now))

    def pull_events(self) -> tuple[DomainEvent, ...]:
        events, self._events = tuple(self._events), []
        return events

    def state(self) -> "RoomDayState": ...
    @classmethod
    def restore(cls, state: "RoomDayState") -> "RoomDay": ...    # runs the value-object constructors; raises no events

@dataclass(frozen=True)
class RoomDayState:        # primitives allowed here only
    room_id: str
    date: str
    bookings: tuple["BookingState", ...]
```

### Ports

```python
class RoomDayRepository(Protocol):
    def get(self, room_id: RoomId, on_date: date) -> RoomDay: ...     # an empty RoomDay if none exists
    def save(self, day: RoomDay) -> None: ...                         # also stores day.pull_events() in the outbox, in the same transaction

class Clock(Protocol):
    def now(self) -> datetime: ...

class IdGenerator(Protocol):
    def new_booking_id(self) -> BookingId: ...
```

### Use case

```python
class ConfirmBooking:
    def __init__(self, room_days: RoomDayRepository, rooms: RoomRepository,
                 clock: Clock, ids: IdGenerator) -> None:         # no defaults that build an adapter
        self._room_days = room_days
        self._rooms = rooms
        self._clock = clock
        self._ids = ids

    def run(self, inp: ConfirmBookingInput) -> ConfirmBookingResult:
        rng = TimeRange(inp.start, inp.end)
        room = self._rooms.get(inp.room_id)
        day = self._room_days.get(inp.room_id, rng.date())
        price = price_for(room.rate, rng)                          # pure function: created directly
        day.confirm(self._ids.new_booking_id(), inp.attendee_id, rng, inp.count, room.capacity, price, self._clock.now())
        self._room_days.save(day)
        return ...
```

### Adapter, composition root, fake, contract test

```python
class SqlRoomDayRepository:                                       # adapters/outbound: no base class needed
    def get(self, room_id: RoomId, on_date: date) -> RoomDay: ...
    def save(self, day: RoomDay) -> None: ...

def build_app(config: Config) -> App:                             # the ONLY place that creates adapters
    db = connect(config.db_url)
    confirm = ConfirmBooking(SqlRoomDayRepository(db), SqlRoomRepository(db), SystemClock(), UuidGenerator())
    return App(handlers=[PostBookingHandler(confirm)])

class InMemoryRoomDayRepository:                                  # tests
    def __init__(self) -> None: self._states: dict[tuple[RoomId, date], RoomDayState] = {}
    def get(self, room_id, on_date):
        state = self._states.get((room_id, on_date))
        return RoomDay.empty(room_id, on_date) if state is None else RoomDay.restore(state)
    def save(self, day): self._states[(day.room_id, day.date)] = day.state()

@pytest.fixture(params=["fake", "real"])                          # or the project's equivalent
def repo(request) -> RoomDayRepository: ...
# every contract test takes `repo`: save then get returns equal state; a missing day is empty; a stale save raises Conflict
```

Because `Protocol` is structural, nothing in the adapter says it implements the port. The proof is the type checker, plus the fixture above, which runs the adapter through the same tests as the fake.

### Table-driven rule test

```python
@pytest.mark.parametrize(                                         # or the project's equivalent
    "name,start,end,expected",
    [
        ("valid one hour", at(9, 0), at(10, 0), None),
        ("zero length", at(9, 0), at(9, 0), RangeNotPositive),
        ("five hours", at(8, 0), at(13, 0), RangeTooLong),
    ],
)
def test_r2_time_range(name, start, end, expected):
    if expected is None:
        TimeRange(start, end)
    else:
        with pytest.raises(expected):
            TimeRange(start, end)
```

Name tests `test_r<n>_<name>` for rules and `test_s<n>_<name>` for scenarios.

### Identifiers and enumerations

```python
@dataclass(frozen=True, slots=True)
class AppId:                                           # AppId and OrgId are different classes
    value: str
    def __post_init__(self) -> None:
        if not self.value.strip(): raise InvalidId("AppId")

@dataclass(frozen=True, slots=True)
class OrgId:
    value: str                                         # same shape

class Status(Enum):
    CONFIRMED = "confirmed"                            # wire values are explicit strings
    CANCELLED = "cancelled"
# Status("bogus") raises ValueError: use Status(raw) at the edges to parse

# Two parameters of the same type: keyword-only, so the names carry the meaning.
def transfer(*, source: AccountId, target: AccountId, amount: Money) -> None: ...
```

Rules:

- One class per kind of identifier, per context. The project's type checker rejects an `OrgId` where an `AppId` is expected. If the project does not run a type checker, the distinction is only a convention: tell the user at Step 0 and ask whether to add one.
- Raw strings become identifiers and statuses at the edges (handlers, consumers, adapters). Inside the model, use cases, and ports, pass the typed value.
- Persist `status.value`, never the member name or its position.
- A function or method with two or more parameters of the same type puts `*` before them, so callers must name them. The Python docs recommend this when "names have meaning".
- Before you rely on a frozen dataclass or an enum in a persistence-library mapping or a JSON payload, run one round trip in the project at Step 10: write, read, compare.

## 3. Traps

- **`NewType` is a type-checker feature only.** The Python docs say that at run time calling a `NewType` returns its argument unchanged. It validates nothing and keeps nothing apart at run time. Use it only to add a second layer on top of a validated class.
- **`frozen=True` freezes attributes, not their contents.** A `list` field stays mutable. Use `tuple` and `frozenset`. `dataclasses.replace` calls the constructor again, so `__post_init__` validation runs again.
- **Naive and aware datetimes cannot be compared.** Comparing them raises `TypeError`. Require timezone-aware values in every value object that holds a time.
- **A default argument is evaluated once**, when the function is defined. A default that builds an adapter is both hidden creation and one shared instance.
- **Module-level code runs on import.** An adapter created at module level is created before the composition root runs and cannot be replaced by a test.
- **Privacy is a naming convention.** A `_` prefix stops nothing. Enforce it by search (C9) and by the type checker where it supports it.
- **`Protocol` is checked statically.** A missing method fails only under the type checker or in the contract test.

## 4. Checklist searches

Use these as starting patterns. Run them through the project's own scripts where it has them, and adapt the paths.

| Check | Search or command |
|---|---|
| C1 | In `model`, `usecases`, and `ports`, search the import lines for the adapters package and for any database, transport, or framework package. The project's import-rule tool should enforce it. |
| C2 | For each adapter in the seam table, search for its constructor call outside the composition root and the tests. |
| C3 | Search for module-level assignments of collaborator instances. Search `def __init__` and `def` signatures for defaults that call a constructor (`=\s*\w+\(`). |
| C4 | Search the model and use cases for `datetime.now(`, `datetime.utcnow(`, `date.today(`, `time.time(`, `uuid.uuid4(`, `random.`, `os.environ`, `os.getenv(`. |
| C9 | Search for assignments to `_`-prefixed attributes of an aggregate outside its class. Under the ORM exception, search for assignments to its columns outside its module. |
| C11 | Search all identifiers in the context for each `_Avoid_` word, case-insensitively. |
| C12 | In `model`, `usecases`, and `ports`, search for parameters and fields named `*_id`, `amount`, `price`, `currency`, `status` annotated `str`, `int`, or `float`. `State` dataclasses and the value object's own definition are exempt. |
| C13 | Search for `@dataclass` lines in `model` without `frozen=True`. It must return nothing for value objects and events. |
| C14 | Search for each event class name followed by `(` outside the aggregate's module. It must return nothing. |
| C17 | Search the use-case tests for a mocking facility applied to a port. |
| C19 | Every kind of identifier is its own class, and every closed set is an `Enum`. Search the model, use cases, and ports for `str` or `int` used as an identifier or status. It must return nothing. The type checker passes over these layers. |
| C20 | List the functions and methods in the model, use cases, and ports that take two or more parameters of the same identifier or value-object type. Each puts `*` before them. |

## 5. Enforcement

- Run the type checker in its strictest configured mode over every layer, including the composition root.
- Add the project's import rule so C1 fails the build. Reuse the tool the project already has, or ask the user before adding one.
- Keep one contract-test fixture per port.

## 6. Under the ORM exception

The aggregate may be the library's model class:

- Column declarations stay as the library requires. Public attributes then exist. E4 is enforced by search (C9) and by the import rule, because the language does not help.
- Keep the library's lifecycle hooks mechanical (E1).
- `state()` and `restore` are not needed, because the library fills the object.
- Operations stay methods on the class. They never call the library's session.
