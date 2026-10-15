# Interoperability without ambient authority

Brainstem Zaps exposes a stable named-effect adapter ABI. A program can compose
ordinary computation and approved effect results through LisPy `let*`,
functions, lists and dictionaries. An external system becomes native to
Brainstem when the recipient supplies an approved, versioned adapter contract
and the fixed Brainstem Zap executor exposes that contract.

The packet requests an exact adapter name, version and operation. The device
keeps the implementation, content pin, credential bindings, argument schema,
allowed destinations, storage scopes and budgets outside the traded program.
No pack downloads or installs a handler.

| Existing system | Safe integration lane |
| --- | --- |
| ComfyUI | Pinned native graphs/model and verified image-completion receipts |
| MCP | Named tools through a recipient-configured MCP transport and closed argument schemas |
| Plugins | Recipient-installed callbacks; program names are not import paths |
| Skills | Reviewed frozen programs; Markdown is data, not privileged instructions |
| Existing Python agents | One trusted host compatibility façade; Python is not shipped to secure devices |
| n8n-style workflows | Explicit node/operation mappings; arbitrary code, commands and credentials are not imported automatically |
| Future AI standards | A new approved adapter version, without changing the portable core or auto-granting access |

This is an extension mechanism, not a claim that every tool or every n8n node
already has an implementation. Unsupported versions or operations refuse.
Adding an adapter does not widen existing Zap permissions.

The standard effect form is:

```lisp
(effect "mcp.search" "1" "query"
  (make-dict "query" (get kwargs "query")))
```

This call fails before the handler if the exact request, recipient grant,
device policy, adapter pin, argument contract, path/egress rules or budget is
missing. A cryptographically authenticated publisher does not override any of
these checks.

The capability kernel is inside the VM. A local effect callback needs no
network service; a workflow using a GPU on another computer naturally depends
on that GPU provider, not on a mandatory language authorization server.
