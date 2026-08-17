"""brainstem_agent.py — run RAPP agent.py files on the GitHub Copilot harness.

A RAPP agent is a single file with three things: a `name`, a `metadata` dict
carrying a JSON Schema, and a `perform(**kwargs)`. An Agent Framework tool wants
a name, a description, a JSON Schema, and a callable.

Those are the same four things. The measured finding this file is built on:

    tool(fn, name=..., description=..., schema=agent.metadata["parameters"])

accepts a RAPP schema **byte-identical** — verified against
agent-framework 1.13.0 / agent-framework-github-copilot 1.0.1. Nothing is
translated, so nothing can drift.

That matters more than convenience. A converter that RE-IMPLEMENTED perform()
in the harness idiom would make a side-by-side benchmark meaningless: you would
be measuring the transcription, not the harness. Here the *same function object*
runs on both sides and the *same schema* describes it, so a difference in the
results is a difference in the harness.

    python3 brainstem_agent.py discover  agents/
    python3 brainstem_agent.py emit      agents/ -o harness_app.py
    python3 brainstem_agent.py compare   agents/ --case MeetingCost:people=6,minutes=45
    python3 brainstem_agent.py run       agents/ --prompt "what does a 6-person 45-minute meeting cost?"

`discover`, `emit` and `compare` need no credentials and no network — they
exercise the adapter only. `run` drives the real Copilot loop and needs an
authenticated Copilot CLI. Keeping that line visible is deliberate: most of what
can go wrong in a port is provable without a model in the way.

This file is itself a RAPP agent — name, metadata, perform — so it can convert
its own kind, including itself.
"""
from __future__ import annotations

import argparse
import asyncio
import importlib.util
import inspect
import json
import sys
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable

SPEC = "brainstem-harness/1.0"

# JSON Schema type -> Python annotation, for the emitted source only. The live
# adapter never uses this: it passes the schema through untouched.
_PY_TYPE = {"string": "str", "integer": "int", "number": "float",
            "boolean": "bool", "array": "list", "object": "dict"}


# ── discovery ───────────────────────────────────────────────────────────────

@dataclass
class Discovered:
    """One RAPP agent found on disk, plus why it was or was not usable."""
    path: Path
    cls_name: str = ""
    name: str = ""
    description: str = ""
    schema: dict = field(default_factory=dict)
    instance: Any = None
    error: str = ""

    @property
    def ok(self) -> bool:
        return self.instance is not None and not self.error


def _looks_like_agent(obj: Any) -> bool:
    """Duck-typed on purpose.

    Requiring `issubclass(obj, BasicAgent)` would only find agents that imported
    the same BasicAgent this process can see -- and in practice each project
    vendors its own (`from agents.basic_agent import BasicAgent`). The contract
    that actually matters is the shape, not the ancestor.
    """
    return (inspect.isclass(obj)
            and callable(getattr(obj, "perform", None))
            and obj.__name__ != "BasicAgent")


def _load_module(path: Path):
    """Import a lone agent file, with its own directory and parent importable.

    RAPP agents commonly do `from agents.basic_agent import BasicAgent`, which
    resolves only if the directory ABOVE `agents/` is on sys.path. Adding both
    is what lets a group of files be converted where they sit, rather than
    demanding they be restructured first.
    """
    added = []
    for p in (str(path.parent), str(path.parent.parent)):
        if p not in sys.path:
            sys.path.insert(0, p)
            added.append(p)
    mod_name = f"_rapp_{path.stem}"
    try:
        spec = importlib.util.spec_from_file_location(mod_name, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"no import spec for {path}")
        mod = importlib.util.module_from_spec(spec)
        # Register BEFORE exec. Skipping this breaks any agent that uses
        # @dataclass: dataclasses resolves a field's type via
        # sys.modules.get(cls.__module__).__dict__, which is None for a module
        # that was executed but never registered, and the agent fails to load
        # with a bewildering AttributeError about __dict__. Found because this
        # file uses @dataclass and could not convert itself.
        sys.modules[mod_name] = mod
        try:
            spec.loader.exec_module(mod)
        except Exception:
            sys.modules.pop(mod_name, None)
            raise
        return mod
    finally:
        for p in added:
            try:
                sys.path.remove(p)
            except ValueError:
                pass


def discover(target: str | Path) -> list[Discovered]:
    """Every RAPP agent under a file or directory, loadable or not.

    A file that fails to import is REPORTED rather than skipped. A converter
    that silently drops what it could not read would quietly shrink the thing
    being benchmarked, and the missing agent is exactly what you would want to
    know about.
    """
    target = Path(target).expanduser()
    files = ([target] if target.is_file()
             else sorted(p for p in target.rglob("*.py")
                         if not p.name.startswith("_")
                         and p.name not in ("basic_agent.py", "brainstem_agent.py")))
    out: list[Discovered] = []
    for f in files:
        try:
            mod = _load_module(f)
        except Exception as exc:
            out.append(Discovered(path=f, error=f"{type(exc).__name__}: {exc}"))
            continue
        for _, obj in vars(mod).items():
            if not _looks_like_agent(obj) or obj.__module__ != mod.__name__:
                continue
            d = Discovered(path=f, cls_name=obj.__name__)
            try:
                inst = obj()
                meta = dict(getattr(inst, "metadata", {}) or {})
                d.instance = inst
                d.name = getattr(inst, "name", None) or meta.get("name") or obj.__name__
                d.description = meta.get("description", "") or (obj.__doc__ or "").strip()
                d.schema = meta.get("parameters") or {"type": "object", "properties": {}}
            except Exception as exc:
                d.error = f"{type(exc).__name__}: {exc}"
            out.append(d)
    return out


# ── adaptation: the whole point ─────────────────────────────────────────────

def to_tool(d: Discovered):
    """Wrap a discovered RAPP agent as an Agent Framework tool.

    The agent's own `perform` is what runs. The agent's own schema is what
    describes it. This function adds no behaviour of its own beyond awaiting an
    async `perform` and stringifying a non-string return, both of which are
    adapter concerns rather than agent concerns.
    """
    from agent_framework import tool  # imported lazily so `discover` needs no SDK

    perform = d.instance.perform
    is_async = inspect.iscoroutinefunction(perform)

    if is_async:
        async def _call(**kwargs):
            return _stringify(await perform(**kwargs))
    else:
        def _call(**kwargs):
            return _stringify(perform(**kwargs))

    _call.__name__ = d.name
    _call.__doc__ = d.description or f"RAPP agent {d.name}"
    return tool(_call, name=d.name, description=_call.__doc__, schema=d.schema)


def _stringify(v: Any) -> str:
    if isinstance(v, str):
        return v
    try:
        return json.dumps(v, ensure_ascii=False, default=str)
    except Exception:
        return str(v)


def build_agent(discovered: Iterable[Discovered], *, instructions: str | None = None,
                model: str | None = None, approve_all: bool = True,
                require_approval: bool = False):
    """A GitHubCopilotAgent exposing every usable RAPP agent as a tool."""
    from agent_framework.github import GitHubCopilotAgent, GitHubCopilotOptions

    usable = [d for d in discovered if d.ok]
    tools = [to_tool(d) for d in usable]

    options: dict[str, Any] = {}
    if model:
        options["model"] = model
    if approve_all and not require_approval:
        try:
            from copilot.session import PermissionHandler
            options["on_permission_request"] = PermissionHandler.approve_all
        except Exception:
            pass    # the SDK's own default applies; never fail construction for this

    names = ", ".join(d.name for d in usable) or "(none)"
    return GitHubCopilotAgent(
        instructions=instructions or (
            "You are a RAPP brainstem running on the GitHub Copilot harness. "
            f"These capabilities are available as tools: {names}. "
            "Prefer a tool over reasoning it out yourself when one fits — each is "
            "deterministic and is the same code the native brainstem runs."),
        tools=tools,
        default_options=GitHubCopilotOptions(**options) if options else None,
    )


# ── side-by-side ────────────────────────────────────────────────────────────

def _parse_case(spec: str) -> tuple[str, dict]:
    """`Name:k=v,k=v` -> (Name, {k: v}) with ints and floats recovered."""
    name, _, rest = spec.partition(":")
    args: dict[str, Any] = {}
    for pair in filter(None, (p.strip() for p in rest.split(","))):
        k, _, v = pair.partition("=")
        k, v = k.strip(), v.strip()
        for cast in (int, float):
            try:
                args[k] = cast(v)
                break
            except ValueError:
                continue
        else:
            args[k] = {"true": True, "false": False}.get(v.lower(), v)
    return name, args


async def compare(discovered: list[Discovered], cases: list[str]) -> dict:
    """Run each case natively and through the harness tool, and diff.

    This is the honest half of the benchmark and it needs no credentials. If the
    two sides ever disagree, the adapter is wrong -- the same perform() ran
    both times -- and any higher-level comparison built on it is worthless.
    """
    by_name = {d.name: d for d in discovered if d.ok}
    results = []
    for spec in cases:
        name, args = _parse_case(spec)
        d = by_name.get(name)
        if d is None:
            results.append({"case": spec, "status": "no such agent",
                            "available": sorted(by_name)})
            continue

        async def _native():
            r = d.instance.perform(**args)
            if inspect.isawaitable(r):
                r = await r
            return _stringify(r)

        t0 = time.perf_counter()
        try:
            native, native_err = await _native(), ""
        except Exception as exc:
            native, native_err = "", f"{type(exc).__name__}: {exc}"
        native_ms = (time.perf_counter() - t0) * 1000

        # Call the agent a SECOND time natively before involving the harness.
        # compare() necessarily runs perform() twice, so a stateful agent would
        # return two different answers and the difference would be blamed on the
        # adapter -- a confident, wrong accusation. Found by testing this tool
        # against a deliberately stateful agent. If the agent disagrees with
        # itself, no conclusion about the adapter is available from this case.
        try:
            deterministic = (await _native()) == native and not native_err
        except Exception:
            deterministic = False

        t0 = time.perf_counter()
        try:
            out = to_tool(d).invoke(arguments=args)
            if inspect.isawaitable(out):
                out = await out
            harness, harness_err = _content_text(out), ""
        except Exception as exc:
            harness, harness_err = "", f"{type(exc).__name__}: {exc}"
        harness_ms = (time.perf_counter() - t0) * 1000

        results.append({
            "case": spec, "agent": name, "arguments": args,
            "native": native, "native_error": native_err,
            "harness": harness, "harness_error": harness_err,
            "deterministic": deterministic,
            "identical": (native == harness and not native_err and not harness_err),
            "native_ms": round(native_ms, 3), "harness_ms": round(harness_ms, 3),
        })
    judged = [r for r in results if not r.get("status") and r.get("deterministic")]
    inconclusive = [r for r in results if not r.get("status") and not r.get("deterministic")]
    agreed = sum(1 for r in judged if r["identical"])
    if not judged:
        verdict = "no conclusion — every case used a non-deterministic agent"
    elif agreed == len(judged):
        verdict = "adapter faithful"
    else:
        verdict = "MISMATCH — the adapter changed behaviour"
    if inconclusive:
        verdict += f" ({len(inconclusive)} inconclusive: agent not deterministic)"
    return {"spec": SPEC, "cases": len(results), "judged": len(judged),
            "identical": agreed, "inconclusive": len(inconclusive),
            "results": results, "verdict": verdict}


def _content_text(out: Any) -> str:
    """Pull text out of whatever the SDK hands back.

    invoke() returns a list of Content objects rather than a string, and the
    attribute carrying the text has moved between versions, so this looks for
    the value instead of assuming a shape.
    """
    if isinstance(out, str):
        return out
    items = out if isinstance(out, (list, tuple)) else [out]
    parts = []
    for it in items:
        for attr in ("text", "value", "result", "content"):
            v = getattr(it, attr, None)
            if isinstance(v, str):
                parts.append(v)
                break
        else:
            parts.append(_stringify(getattr(it, "__dict__", it)))
    return "".join(parts)


# ── emit a standalone harness app ───────────────────────────────────────────

def emit(discovered: list[Discovered], out_path: Path, *, model: str | None = None) -> str:
    """Write a runnable harness module that imports the agents where they live.

    It imports rather than inlines on purpose. A generated copy of perform()
    would drift from the original the first time anyone edited either, and then
    the benchmark would be comparing two different programs.
    """
    usable = [d for d in discovered if d.ok]
    lines = [
        '"""Generated by brainstem_agent.py — RAPP agents on the GitHub Copilot harness.',
        "",
        "Every agent below is IMPORTED from its original file, not copied. The RAPP",
        "JSON Schema is handed to the SDK unchanged. Editing an agent changes both",
        "this harness and the native brainstem, which is what keeps a side-by-side",
        "comparison meaningful.",
        f'"""',
        "from __future__ import annotations",
        "",
        "import asyncio, importlib.util, inspect, json, sys",
        "from pathlib import Path",
        "",
        "from agent_framework import tool",
        "from agent_framework.github import GitHubCopilotAgent, GitHubCopilotOptions",
        "",
        "",
        "def _load(path, stem):",
        "    for p in (str(Path(path).parent), str(Path(path).parent.parent)):",
        "        if p not in sys.path:",
        "            sys.path.insert(0, p)",
        "    spec = importlib.util.spec_from_file_location(f'_rapp_{stem}', path)",
        "    mod = importlib.util.module_from_spec(spec)",
        "    spec.loader.exec_module(mod)",
        "    return mod",
        "",
        "",
        "def _wrap(inst, name, description, schema):",
        "    perform = inst.perform",
        "    if inspect.iscoroutinefunction(perform):",
        "        async def _call(**kw):",
        "            r = await perform(**kw)",
        "            return r if isinstance(r, str) else json.dumps(r, default=str)",
        "    else:",
        "        def _call(**kw):",
        "            r = perform(**kw)",
        "            return r if isinstance(r, str) else json.dumps(r, default=str)",
        "    _call.__name__, _call.__doc__ = name, description",
        "    return tool(_call, name=name, description=description, schema=schema)",
        "",
        "",
        "TOOLS = []",
    ]
    for d in usable:
        lines += [
            "",
            f"# {d.name} — {d.path}",
            f"_m = _load({str(d.path)!r}, {d.path.stem!r})",
            f"_i = _m.{d.cls_name}()",
            f"TOOLS.append(_wrap(_i, {d.name!r}, {d.description!r}, "
            f"{json.dumps(d.schema)}))",
        ]
    names = ", ".join(d.name for d in usable) or "(none)"
    opts = f'GitHubCopilotOptions(model={model!r})' if model else "None"
    lines += [
        "",
        "",
        "def build():",
        "    return GitHubCopilotAgent(",
        f"        instructions=(\"You are a RAPP brainstem on the GitHub Copilot harness. \"",
        f"                      \"Capabilities available as tools: {names}. \"",
        "                      \"Prefer a tool over reasoning it out yourself when one fits.\"),",
        "        tools=TOOLS,",
        f"        default_options={opts},",
        "    )",
        "",
        "",
        "async def main():",
        "    prompt = \" \".join(sys.argv[1:]) or \"List your tools and what each one does.\"",
        "    async with build() as agent:",
        "        print(await agent.run(prompt))",
        "",
        "",
        "if __name__ == '__main__':",
        "    asyncio.run(main())",
        "",
    ]
    src = "\n".join(lines)
    out_path = Path(out_path).expanduser()
    out_path.write_text(src, encoding="utf-8")
    return src


# ── this file is itself a RAPP agent ────────────────────────────────────────

class BrainstemHarnessAgent:
    """Convert a group of RAPP agent.py files onto the GitHub Copilot harness."""

    def __init__(self):
        self.name = "BrainstemHarness"
        self.metadata = {
            "name": self.name,
            "description": ("Convert RAPP agent.py files into GitHub Copilot harness "
                            "tools, and prove the adapter did not change behaviour."),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string",
                             "description": "file or directory holding agent.py files"},
                    "action": {"type": "string",
                               "description": "discover | emit | compare"},
                    "out": {"type": "string",
                            "description": "output module path, for emit"},
                    "cases": {"type": "string",
                              "description": "comparison cases, e.g. 'MeetingCost:people=6,minutes=45'"},
                },
                "required": ["path"],
            },
        }

    def perform(self, **kwargs):
        path = kwargs.get("path", ".")
        action = (kwargs.get("action") or "discover").lower()
        found = discover(path)
        if action == "emit":
            out = Path(kwargs.get("out") or "harness_app.py")
            emit(found, out)
            return f"wrote {out} exposing {sum(1 for d in found if d.ok)} agent(s)"
        if action == "compare":
            cases = [c for c in (kwargs.get("cases") or "").split(";") if c.strip()]
            return _stringify(asyncio.run(compare(found, cases)))
        ok = [d.name for d in found if d.ok]
        bad = [f"{d.path.name}: {d.error}" for d in found if not d.ok]
        return _stringify({"usable": ok, "unusable": bad})


# ── cli ─────────────────────────────────────────────────────────────────────

def _print_discovery(found: list[Discovered]) -> None:
    usable = [d for d in found if d.ok]
    print(f"{SPEC}\n{'=' * 72}")
    for d in usable:
        props = list((d.schema or {}).get("properties", {}))
        req = set((d.schema or {}).get("required", []))
        shown = ", ".join(f"{p}{'' if p in req else '?'}" for p in props) or "(no inputs)"
        print(f"  [ok  ] {d.name:22s} {shown}")
        print(f"         {d.path}")
    for d in found:
        if not d.ok:
            print(f"  [FAIL] {d.path.name}: {d.error}")
    print("=" * 72)
    print(f"  {len(usable)} usable, {len(found) - len(usable)} unusable")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Run RAPP agents on the GitHub Copilot harness.")
    ap.add_argument("action", choices=["discover", "emit", "compare", "run"])
    ap.add_argument("path", help="file or directory of agent.py files")
    ap.add_argument("-o", "--out", default="harness_app.py")
    ap.add_argument("--case", action="append", default=[],
                    help="Name:k=v,k=v — repeatable")
    ap.add_argument("--prompt", default="List your tools and what each one does.")
    ap.add_argument("--model", default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    found = discover(a.path)

    if a.action == "discover":
        if a.json:
            print(json.dumps([{"name": d.name, "path": str(d.path), "ok": d.ok,
                               "error": d.error, "schema": d.schema} for d in found], indent=2))
        else:
            _print_discovery(found)
        return 0 if any(d.ok for d in found) else 1

    if a.action == "emit":
        emit(found, Path(a.out), model=a.model)
        print(f"wrote {a.out} — {sum(1 for d in found if d.ok)} agent(s), "
              f"imported from source, schemas passed through")
        return 0

    if a.action == "compare":
        if not a.case:
            print("compare needs at least one --case Name:k=v,k=v", file=sys.stderr)
            return 2
        rep = asyncio.run(compare(found, a.case))
        if a.json:
            print(json.dumps(rep, indent=2))
            return 0 if rep["judged"] and rep["identical"] == rep["judged"] else 1
        print(f"{SPEC} — side by side\n{'=' * 72}")
        for r in rep["results"]:
            if r.get("status"):
                print(f"  [SKIP] {r['case']}: {r['status']} (have: {', '.join(r['available'])})")
                continue
            mark = ("MATCH" if r["identical"] else "DIFFER") if r["deterministic"] else "INCONC"
            print(f"  [{mark}] {r['agent']}  {r['arguments']}"
                  + ("" if r["deterministic"]
                     else "   <- agent is not deterministic; says nothing about the adapter"))
            print(f"         native  ({r['native_ms']:.2f}ms): {r['native'] or r['native_error']}")
            print(f"         harness ({r['harness_ms']:.2f}ms): {r['harness'] or r['harness_error']}")
        print("=" * 72)
        print(f"  {rep['identical']}/{rep['judged']} identical of the judgeable — {rep['verdict']}")
        return 0 if rep["judged"] and rep["identical"] == rep["judged"] else 1

    # run: the only path that needs an authenticated Copilot CLI
    async def _go():
        agent = build_agent(found, model=a.model)
        async with agent:
            print(await agent.run(a.prompt))
    try:
        asyncio.run(_go())
        return 0
    except Exception as exc:
        print(f"harness run failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        print("`discover`, `emit` and `compare` need no credentials — start there "
              "to tell an adapter problem from an auth problem.", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
