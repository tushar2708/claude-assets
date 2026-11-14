# Language matrix for domain-design

One row per concept, one column per language. Use it to compare, or to port a design from one language to another. The details, templates, traps, and search patterns are in the per-language files. The matrix does not replace them. Before you write code in a language, read that language's file in full.

| Language | File |
|---|---|
| Go | `references/lang-go.md` |
| Java | `references/lang-java.md` |
| Python | `references/lang-python.md` |
| TypeScript | `references/lang-typescript.md` |

## Constructs

| Concept | Go | Java | Python | TypeScript |
|---|---|---|---|---|
| Value object | Struct, unexported fields, `NewX` returns `(X, error)`, value receivers, `Equal` | `record` with a validating compact constructor | Frozen dataclass with `__post_init__` | Class, private constructor, `readonly` fields, static `create`, `equals` |
| Validated ID | Defined type plus `ParseX` | `record XId(String value)` | Frozen dataclass around the primitive | Branded type plus one `parse` |
| Enumeration | Defined string type, constants, `ParseX` | `enum` with explicit wire values and a `fromWire` | `enum.Enum` with string values | String-literal union from a `const` array |
| Same-kind parameters | Input struct with named fields | Input record | `*` before the parameters | Input object |
| Money | Value object of integer minor units | `record Money(long, Currency)` | Value object of integer minor units | Value object of integer minor units |
| Entity member | Unexported struct, same package as root | Package-private `final` class | `_`-prefixed class in the aggregate's module | Non-exported class in the aggregate's module |
| Aggregate root | Exported struct, unexported fields, own package, pointer receivers | `public final class`, private fields, own package | Plain class, `_` attributes, `@property` reads | Class with `#` fields, private constructor, static factory |
| Rebuild from storage | `State()` and `Restore(State)` | `state()` and `static restore(State)` | `state()` and `@classmethod restore` | `state()` and `static restore` |
| Domain event | Exported struct, passed by value | `record` implementing `DomainEvent` | Frozen dataclass, tuples | Frozen `readonly` object with a `type` field |
| Domain service | Package function | `final` class with `static` methods | Module function | Exported function |
| Domain error | Sentinel or typed error, `errors.Is` | `RuleViolation` hierarchy | `RuleViolation` hierarchy | `RuleViolation` hierarchy with `kind` |
| Interface (port) | `interface` in `ports` | `interface` in `ports` | `typing.Protocol` | `interface` in `ports/` |
| Use case | Struct plus `NewX`, `Run(ctx, in)` | `final` class, one constructor, `execute(in)` | Class, `__init__`, `run(in)` | Class, constructor parameter properties, `run(in)` |
| Clock | `Clock` interface | `java.time.Clock` | `Clock` protocol | `Clock` interface |
| Composition root | `cmd/<app>/main.go` | One class, or the container's configuration | `build_app()` | `compose.ts` |
| Fake | In-memory struct storing `State` | In-memory class storing `State` | In-memory class storing `State` | In-memory class storing `State` |
| Contract test | `RunXContract(t, newRepo)` | Abstract test class, two subclasses | Fixture with `params=["fake","real"]` | `xContract(make)` called twice |
| Table-driven test | Slice of cases, `t.Run` | Parameterized test with a source of cases | `parametrize` | Array of cases with `it.each` or a loop |
| Test names | `TestR2_...` | `R2_...` | `test_r2_...` | `R2: ...` |

## What stops a mistake, and when

"Compile" means the compiler stops it. "Run time" means the program fails when it runs. "Search" means only a checklist search or a test finds it.

| Mistake | Go | Java | Python | TypeScript |
|---|---|---|---|---|
| Passing an `OrgId` where an `AppId` is expected | Compile (defined types, never aliases) | Compile (record types) | Type checker only. Without one, nothing stops it | Compile, only with a brand. `type X = string` does not stop it |
| Swapping two parameters of the same type | Search. Use an input struct | Search. Use an input record | Search. Put `*` before them | Search. Use an input object |
| Assigning a bad status | Search. Constants of a defined type are not exhaustive. Use `ParseStatus` at the edges | Compile (`enum`) | Run time (`Enum(...)` raises) and type checker | Compile (union) |
| Building an invalid value object | Search, because `T{}` skips the constructor. Use `IsZero` | Run time (compact constructor). A public record must have a public canonical constructor, so anyone can call it | Run time | Compile (private constructor) |
| Changing a value object | Compile (unexported fields) | Compile (`private final`) | Run time (`FrozenInstanceError`) | Compile (`readonly`), run time with `Object.freeze` |
| Outside code changing an aggregate's fields | Compile (unexported) | Compile (private) | Search | Run time (`#` fields) |
| An adapter not satisfying a port | Compile (`var _ ports.X = ...`) | Compile (`implements`) | Type checker and contract test | Compile (`implements`) |
| Adapter built outside the composition root | Search | Search | Search | Search |
| Model reading the clock | Search | Search | Search | Search |
| Core importing an adapter | Compile with `internal/` plus an import rule | Compile with modules, or an architecture test | Import rule | Import rule |

## Version and tool notes

| Language | Note |
|---|---|
| Go | Visibility is per package. `internal/` limits imports to the tree rooted at its parent. Compare times with `Equal`, not `==`. |
| Java | Check that the project's version has records. `java.time.Clock` exists since 1.8. `BigDecimal.equals` compares scale. |
| Python | `dataclasses` need 3.7. `Protocol` needs 3.8. `slots=True` needs 3.10. `NewType` does nothing at run time. |
| TypeScript | Types are erased at run time. `private` is soft. `#` fields are private at run time. `Date` is mutable. |
