# Brainstem Zaps language profile

## Source and agent shape

Programs are UTF-8 `.lispy` files. `;` starts a line comment. Parentheses form
calls and lists, `'x` is shorthand for `(quote x)`, strings use JSON-compatible
double-quoted escapes, `#t`/`#f` are booleans, and numeric literals use finite
binary64 values. Identifiers are ASCII LisPy names. Dotted pairs, vectors,
macros, and reader extensions are not part of this profile.

A frozen agent defines these top-level values:

```lisp
(define agent-name "Factorial")
(define agent-description "Computes a bounded factorial.")
(define agent-parameters
  (make-dict
    "type" "object"
    "properties" (make-dict
      "n" (make-dict "type" "integer" "minimum" 0 "maximum" 12))
    "required" (list "n")
    "additionalProperties" #f))

(define (factorial n)
  (if (<= n 1)
      1
      (* n (factorial (- n 1)))))

(define (agent-run context kwargs)
  (make-dict
    "answer" (factorial (get kwargs "n"))
    "request" (get context "request_id" #f)))
```

Only top-level `define` forms are accepted. A top-level value must be a literal,
quoted value, bounded `list`/`make-dict` constant, or lambda; top-level function
definitions are supported. `agent-name`, `agent-description`,
`agent-parameters`, and two-argument `agent-run` are required. `agent-parameters`
is the supported JSON Schema subset and is copied into the frozen metadata.
There are no executable top-level forms.

The complete ordered set of top-level definitions is stored as the frozen
`closure`. Verification reparses the source, reconstructs that closure, and
requires an exact structural match before evaluation.

## Supported forms and primitives

Special forms:

- `define`, including `(define (name args...) body...)`
- `lambda`, lexical closures, and recursion
- `if`, `cond` with a final `else`, `begin`
- `let`, `let*`, `set!`
- `quote` and `'`
- short-circuit `and` and `or`

Numbers and predicates:

- `+`, `-`, `*`, `/`, `=`, `<`, `<=`, `>`, `>=`, `eq?`, `equal?`, `not`
- `number?`, `string?`, `boolean?`, `symbol?`

Lists:

- `list`, `cons`, `car`, `cdr`, `append`, `length`
- `null?`, `pair?`, `list?`, `map`, `apply`

Strings and dictionaries:

- `string-append`, `string-length`, `string=?`
- `make-dict` takes alternating unique string keys and values
- `get` accepts a dictionary, key, and optional default
- `dict-set` returns a new dictionary; `dict-has?`, `dict-keys`

Effects use one named syscall ABI implemented by the VM's embedded,
in-process capability kernel; it does not contact a broker service:

```lisp
(effect "mcp.search" "1" "query"
  (make-dict "query" (get kwargs "query")))
```

The exact capability name, version, and operation must also occur in the
immutable pack request. The function has no ambient authority; absent
app-local recipient grant, device policy, approved contract, registered local
callback, schema/path/egress match, or remaining budget, it fails before the
callback is called. A callback may choose to contact a remote provider, but
that is an optional dependency of that one workflow, not of the VM.

## Deliberate exclusions

The VM does not implement `letrec`, dotted pairs, macros, continuations,
mutable list cells, `eval`, `load`, ports, I/O primitives, exception handlers,
module loading, host-object access, reflection, shell commands, filesystem
operations, direct network APIs, or arbitrary plugin loaders. Unbound names
such as `eval`, `exec`, `import`, `require`, `globalThis`, `constructor`,
`prototype`, and `__proto__` are not host references. They are inert quoted
symbols or fail as unbound calls.

This is a deliberate, documented subset of familiar LisPy/Scheme conventions,
not a claim that every Scheme reader extension or arbitrary host-language
operation is available. Owned LisPy/Brainstem components and licensed primitives
retain their provenance.

## Turing-completeness boundary

In the abstract language semantics, recursive lexical closures plus `if`,
`define`, and lists can encode unbounded counters and a universal register/Turing
machine. A computation can recurse until a halting condition; `set!` also
provides lexical mutable state. The practical runtime is **not** unbounded:
finite evaluation fuel, call depth, allocations, source/tokens, collection
sizes, finite binary64 numeric domain, output size, and wall time make every
individual run bounded. “Turing-complete” describes the unbounded abstract
semantics, not a promise that a device accepts or completes every computation.
