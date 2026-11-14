# Go reference for domain-design

Follow this file for every Go package you write or change under this skill. The skill's steps say what to build. This file says which Go construct to use for each concept. Do not invent a different form. If a form here cannot work in the project, write the reason in `design.md` and ask the user.

The code below uses the meeting-room domain. Copy the shape, not the domain.

## 1. Construct table

| Concept | Required form in Go | Forbidden |
|---|---|---|
| Value object | A struct with **unexported** fields. A constructor `NewX(...) (X, error)` that validates. **Value receivers** only. Accessor methods named after the field (`Start()`), no `Get` prefix. An `Equal` method. | Exported fields. Pointer receivers. A constructor that cannot fail when a rule exists. |
| Validated ID | A defined type (`type RoomID string`) with `ParseRoomID(string) (RoomID, error)`. | Bare `string` or `int` for an ID in the model, use cases, or ports. |
| Money and quantities | A value object (`Money`) holding integer minor units and a currency. | `float32` or `float64` for money. |
| Enumeration | A defined type (`type Status string`) with exported constants of that type and `ParseStatus(string) (Status, error)` that rejects unknown values. Switches list every constant. See the matrix file. | A bare `string` or `int` for a status. Converting raw input with `Status(raw)` outside `ParseStatus`. |
| Entity member of an aggregate | An unexported struct in the aggregate's package. Equality by ID. | A member type that other packages can build or change. |
| Aggregate root | An exported struct with **unexported** fields, in its **own package**. Members live in the same package, because Go hides fields per package. Operations are pointer-receiver methods named after business actions. | Exported mutable fields. Setters. An operation that runs a query or saves. |
| Rebuilding from storage | `State()` returns a plain `State` struct. `Restore(State) (*X, error)` runs the value-object constructors. It raises no events. | Making fields exported so a repository can fill them. |
| Domain event | An exported struct with exported fields, in package `model`. Passed by value. Built only inside the aggregate. Slices and maps are copied when the event is built. | Pointers to events. An event built in a use case or an adapter. |
| Domain service | A package-level function that takes values and returns values. | A struct with collaborators. |
| Domain error | A package-level sentinel (`var ErrOverlap = errors.New("overlap")`) or a typed error. Callers test with `errors.Is` and `errors.As`. Wrap with `%w`. | Comparing error text. Returning a driver error from a port. |
| Interface (port) | A small `interface` in the `ports` package of the context. Methods take `context.Context` first when they can block. Types in the signature come from `model` only. | An interface named after a vendor. An interface with more than about five methods. A name with an `I` prefix. |
| Use case | A struct whose fields are interfaces, a constructor `NewX(deps...) *X`, and one method `Run(ctx, input) (result, error)`. | A struct that builds its own collaborators. A package-level function that uses a package-level variable. |
| Injection | Constructor parameters only. | Package-level `var` of a collaborator type. `init()` that wires anything. Default values that build an adapter. |
| Adapter | A struct in `adapters/outbound/...` with a line `var _ ports.X = (*Adapter)(nil)` that proves it satisfies the interface at build time. | An adapter file imported by `model` or `usecases`. |
| Composition root | One `main` package, such as `cmd/<app>/main.go`. It creates adapters and use cases and hands them to handlers. | Adapter construction anywhere else except tests. |
| Fake | A struct in the test support package. It stores the aggregate's `State`, not the pointer, and calls `Restore` in `Get`. | A scripted mock whose answers are set per test. |
| Contract test | `RunXContract(t, newRepo func(*testing.T) ports.X)` in a `porttest` package. Called once with the fake and once with the real adapter. | Testing the fake and the adapter with different cases. |

## 2. Templates

### Value object

```go
package model

type TimeRange struct{ start, end time.Time } // unexported: only this package can build one

var (
	ErrRangeNotPositive = errors.New("range must have positive length") // R2
	ErrRangeTooLong     = errors.New("range too long")                  // R2
	ErrRangeCrossesDay  = errors.New("range must stay within one day")  // R2
)

func NewTimeRange(start, end time.Time) (TimeRange, error) {
	if !end.After(start) {
		return TimeRange{}, ErrRangeNotPositive
	}
	if end.Sub(start) > 4*time.Hour {
		return TimeRange{}, ErrRangeTooLong
	}
	sy, sm, sd := start.Date()
	ey, em, ed := end.Date()
	if sy != ey || sm != em || sd != ed {
		return TimeRange{}, ErrRangeCrossesDay
	}
	return TimeRange{start, end}, nil
}

func (r TimeRange) Start() time.Time { return r.start }
func (r TimeRange) End() time.Time   { return r.end }
func (r TimeRange) IsZero() bool     { return r.start.IsZero() && r.end.IsZero() }
func (r TimeRange) Overlaps(o TimeRange) bool {
	return r.start.Before(o.end) && o.start.Before(r.end)
}
func (r TimeRange) Equal(o TimeRange) bool { // never use == on time values: see the traps
	return r.start.Equal(o.start) && r.end.Equal(o.end)
}
```

### Aggregate, state, and restore

```go
package roomday // one aggregate per package

type RoomDay struct {
	roomID   model.RoomID
	date     model.Date
	bookings []booking // booking is unexported
	events   []model.Event
}

type booking struct {
	id     model.BookingID
	who    model.AttendeeID
	rng    model.TimeRange
	status status
	price  model.Money
}

func Empty(roomID model.RoomID, date model.Date) *RoomDay { return &RoomDay{roomID: roomID, date: date} }

func (d *RoomDay) Confirm(id model.BookingID, who model.AttendeeID, rng model.TimeRange,
	count, roomCapacity model.AttendeeCount, price model.Money, now time.Time) error {
	if rng.Date() != d.date {
		return ErrWrongDate
	}
	if count.Exceeds(roomCapacity) { // R3
		return ErrOverCapacity
	}
	confirmed := 0
	for _, b := range d.bookings {
		if b.status != statusConfirmed {
			continue
		}
		confirmed++
		if b.rng.Overlaps(rng) { // R1
			return ErrOverlap
		}
	}
	if confirmed >= maxConfirmedPerDay { // R5
		return ErrDayFull
	}
	d.bookings = append(d.bookings, booking{id, who, rng, statusConfirmed, price})
	d.events = append(d.events, model.BookingConfirmed{BookingID: id, RoomID: d.roomID, AttendeeID: who, Range: rng, Price: price, At: now})
	return nil
}

func (d *RoomDay) PullEvents() []model.Event { e := d.events; d.events = nil; return e }

// State is plain data for repositories. Primitives are allowed here only.
type State struct {
	RoomID   string
	Date     string
	Bookings []BookingState
}

func (d *RoomDay) State() State
func Restore(s State) (*RoomDay, error) // runs the value-object constructors; raises no events
```

### Ports

```go
package ports

type RoomDayRepository interface {
	Get(ctx context.Context, roomID model.RoomID, date model.Date) (*roomday.RoomDay, error) // an empty RoomDay if none exists
	Save(ctx context.Context, d *roomday.RoomDay) error                                      // also stores d.PullEvents() in the outbox, in the same transaction
}

type Clock interface{ Now() time.Time }
type IDGenerator interface{ NewBookingID() model.BookingID }
```

### Use case

```go
package usecases

type ConfirmBooking struct {
	roomDays ports.RoomDayRepository
	rooms    ports.RoomRepository
	clock    ports.Clock
	ids      ports.IDGenerator
}

func NewConfirmBooking(rd ports.RoomDayRepository, rs ports.RoomRepository, c ports.Clock, ids ports.IDGenerator) *ConfirmBooking {
	return &ConfirmBooking{roomDays: rd, rooms: rs, clock: c, ids: ids}
}

func (u *ConfirmBooking) Run(ctx context.Context, in ConfirmBookingInput) (ConfirmBookingResult, error) {
	if in.Range.IsZero() { // a zero value skips the constructor: reject it at the entry
		return ConfirmBookingResult{}, ErrInvalidInput
	}
	// load room and day, price := model.PriceFor(room.Rate(), in.Range), day.Confirm(u.ids.NewBookingID(), ..., u.clock.Now()), u.roomDays.Save
}
```

### Adapter and composition root

```go
package sqlstore // adapters/outbound/sqlstore
var _ ports.RoomDayRepository = (*RoomDayRepository)(nil)

package main // cmd/app/main.go: the only place that creates adapters
func main() {
	db := mustConnect(cfg.DBURL)
	confirm := usecases.NewConfirmBooking(sqlstore.NewRoomDayRepository(db), sqlstore.NewRoomRepository(db), clock.System{}, ids.UUID{})
	serve(http.NewPostBookingHandler(confirm))
}
```

### Fake and contract test

```go
type InMemoryRoomDayRepository struct{ states map[string]roomday.State } // stores State, never the pointer
func (r *InMemoryRoomDayRepository) Get(ctx context.Context, id model.RoomID, d model.Date) (*roomday.RoomDay, error) {
	s, ok := r.states[key(id, d)]
	if !ok {
		return roomday.Empty(id, d), nil
	}
	return roomday.Restore(s)
}

// porttest/roomday_repository.go
func RunRoomDayRepositoryContract(t *testing.T, newRepo func(*testing.T) ports.RoomDayRepository) { /* save then get returns equal state; get of a missing day returns an empty day; save of a stale day returns ports.ErrConflict */ }
```

### Table-driven rule test

```go
func TestR2_TimeRange(t *testing.T) {
	at := func(h, m int) time.Time { return time.Date(2026, 3, 1, h, m, 0, 0, time.UTC) }
	tests := []struct {
		name       string
		start, end time.Time
		wantErr    error
	}{
		{"valid one hour", at(9, 0), at(10, 0), nil},
		{"zero length", at(9, 0), at(9, 0), model.ErrRangeNotPositive},
		{"five hours", at(8, 0), at(13, 0), model.ErrRangeTooLong},
		{"crosses midnight", at(23, 0), time.Date(2026, 3, 2, 1, 0, 0, 0, time.UTC), model.ErrRangeCrossesDay},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			_, err := model.NewTimeRange(tc.start, tc.end)
			if !errors.Is(err, tc.wantErr) {
				t.Fatalf("got %v, want %v", err, tc.wantErr)
			}
		})
	}
}
```

Name tests `TestR<n>_<Name>` for rules and `TestS<n>_<Name>` for scenarios.

### Identifiers and enumerations

```go
type AppID string // a DEFINED type: AppID and OrgID are different types. Never write `type AppID = string` (an alias is the same type)
type OrgID string

func ParseAppID(raw string) (AppID, error) { // the ONLY place that converts a string to an AppID
	if raw == "" {
		return "", ErrInvalidAppID
	}
	return AppID(raw), nil
}

type Status string

const (
	StatusConfirmed Status = "confirmed" // wire values are explicit strings, never iota
	StatusCancelled Status = "cancelled"
)

func ParseStatus(raw string) (Status, error) {
	switch s := Status(raw); s {
	case StatusConfirmed, StatusCancelled:
		return s, nil
	}
	return "", ErrInvalidStatus
}

// Two parameters of the same type: one input struct with named fields, so a swap cannot compile silently.
type TransferInput struct{ From, To AccountID; Amount Money }
```

Rules:

- One defined type per kind of identifier, per context. The spec says two named types are not assignable to each other, so passing an `OrgID` where an `AppID` is expected fails to compile.
- Never declare an identifier as an alias. The spec says an alias and its target denote identical types, so it gives no protection.
- Raw strings become identifiers and statuses at the edges (handlers, consumers, adapters), through the `Parse...` functions. Inside the model, use cases, and ports, pass the typed value.
- Never persist `iota` integers. Persist the explicit string.
- A function with two or more parameters of the same type takes an input struct with named fields.
- Before you rely on a defined string type in a persistence-library struct or in a JSON payload, run one round trip in the project at Step 10: write, read, compare.

## 3. Traps

- **The zero value always exists.** Anyone can write `TimeRange{}` and skip the constructor. Give every value object an `IsZero()`. Every use case rejects zero values of its inputs at the entry. Add a test per use case that passes the zero value.
- **Do not compare times with `==`.** The `time` package says `==` compares the instant, the location, and the monotonic clock reading, and tells you to prefer `Equal`. Use `Equal` inside value objects, and never compare a struct that holds a `time.Time` with `==`.
- **Visibility is per package.** Root and members share a package. A repository in another package cannot fill unexported fields, which is why `State` and `Restore` are required.
- **`internal/`.** Code under a directory named `internal` can be imported only by code in the tree rooted at the parent of `internal`. Put the context's `model`, `usecases`, `ports`, and `adapters` under it, so other contexts cannot import them. This is how the one-way rule between contexts is enforced by the compiler.
- **Slices and maps are shared on copy.** A value object that holds one copies it in the constructor and in the accessor.
- **Reflection-based libraries need exported fields.** The reflection package cannot set an unexported field. See section 6.

## 4. Checklist searches

Use these as starting patterns. Run them through the project's own build and lint scripts where it has them, and adapt the paths.

| Check | Search or command |
|---|---|
| C1 | In `model/`, `usecases/`, and `ports/`, search the import lines for the adapters path and for any database, transport, or vendor package. |
| C2 | For each adapter in the seam table, search for its `New...(` call outside `cmd/` and outside `_test.go` files. |
| C3 | Search the same folders for a top-level `var` of an interface or adapter type, and for `func init()`. |
| C4 | Search the model and use cases for `time.Now(`, `rand.`, `uuid.`, `os.Getenv(`, `os.LookupEnv(`. |
| C9 | Unexported fields make this a compile error. Under the ORM exception, search for `\.Field =` outside the aggregate's package. |
| C11 | Search all identifiers in the context for each `_Avoid_` word, case-insensitively. |
| C12 | In `model/`, `usecases/`, and `ports/`, search for fields and parameters named `*ID`, `Amount`, `Price`, `Currency`, `Status` typed `string`, `int`, `int64`, `float64`. `State` structs and the value object's own definition are exempt. |
| C13 | Search for `func \(\w+ \*<ValueObject>\)`. It must return nothing. |
| C14 | Search for each event type followed by `{` outside the aggregate's package. It must return nothing. |
| C18 | Each use case has a test that passes the zero value of each value-object input and expects an error. |
| C19 | Every kind of identifier and every closed set has its own defined type. Search for `type \w+ = ` in the model, use cases, and ports. It must return nothing for these types. |
| C20 | List the functions and methods in the model, use cases, and ports that take two or more parameters of the same identifier or value-object type. Each takes an input struct with named fields. |

## 5. Enforcement

- Place packages under `internal/`.
- Add the project's import-restriction lint rule so that C1 fails the build. Reuse the linter the project already runs.
- Keep the `var _ ports.X = (*Adapter)(nil)` line in every adapter.

## 6. Under the ORM exception

A library that fills structs by reflection needs exported fields, and often reads tags. Then the aggregate is the library's struct:

- Keep the fields exported. Add the library's tags. Put a comment on the type: "Change state only through methods."
- E4 is enforced by search (C9) and by the lint rule, because the compiler no longer helps.
- `State` and `Restore` are not needed, because the library fills the struct.
- Operations stay pointer-receiver methods. They never call the library.
