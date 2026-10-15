# Brainstem Zaps documentation

**A workflow is a portable program.** Brainstem Zaps is an agent-first,
capability-scoped LisPy language and frozen-workflow profile for the Brainstem
ecosystem. This public repository hosts documentation and harmless examples;
the proprietary runtime, recipient policy and device bindings are not hosted here.

Start with [Agent.md](Agent.md), [llms.txt](llms.txt), the
[language](docs/language.md), [sealed format](docs/format.md),
[security model](docs/security.md), [interop](docs/interop.md) and
[actual acceptance evidence](docs/conformance.md).

The capability kernel is inside each VM. Offline computation and granted local
callbacks require no external broker or Python on iOS/browser. Optional
providers may supply GPU inference, MCP tools, native plugins, frozen skills
or legacy agent execution through explicit approved adapters.

Frozen `.lispy` carries a complete immutable definition, asset/runtime/model
pins and permission requests. It cannot grant itself permissions. Signatures
authenticate known publishers but still do not grant effects. Raw `SKILL.md`
remains review-required data and is never imported as privileged instructions.

The language has lexical closures, general recursion, conditionals, lists and
dictionaries. Its abstract semantics express universal computation; each real
execution remains finite and budgeted.

This is a **draft/development beta**, not an Apple certification, App Store
approval, universal safety promise or proof of physical iOS deployment.
Interoperability is an approved adapter lane—not automatic compatibility with
every n8n node, MCP server or unreviewed Python file.
