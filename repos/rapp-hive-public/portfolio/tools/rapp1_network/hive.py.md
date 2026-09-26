# `rapp1_network/hive.py`

The RAPP Hive client: everything the pipeline asks of the Hive goes through the Hive's own agent.

Source: `rapp1_network/hive.py` (rapp1-network 0.1.5). SHA-256 of the source below: `f5b0e4c178e532ee91a02d349555cdca4dfa7985b02e20c21ed941e43d291c92` (16013 bytes). Every pulse this release cuts records it in `payload.generator` as `rapp1_network/hive.py`. Copy it out with the extractor in [../README.md](../README.md); code in a Hive is data, never run from the Hive.

{% raw %}
`````python
"""The RAPP Hive client: everything the pipeline asks of the Hive goes through the Hive's own agent.

The agent is `hive_agent.py` from kody-w/rapp-model-hive (branch experimental/hive-md), named by --hive-agent /
RAPP_HIVE_AGENT and loaded from that file. Changes are made the way the Hive's own driver makes them: a proposal
(`plan "<64 hex>"`), then `apply` from a fresh agent (a proposal is never applied in the turn that made it). Code in
a Hive is data: nothing here runs anything from inside the Hive.

The Hive's own device state is read only here, and only under <hive>/.git/rapp-hive/ (device.json, public.json).
No key store is ever read: signing is the agent's own business, inside its own save and publish.
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import os
import re
import sys
from pathlib import Path
from typing import Callable, Iterable, Mapping

from . import util
from .config import Settings
from .constants import HIVE_MAX_BYTES, PORTFOLIO, ROOM
from .wrapping import Refused, check_hive_path, check_hive_text

PLAN = re.compile(r'plan "([0-9a-f]{64})"')
COMMIT = re.compile(r"commit ([0-9a-f]{10})")
GENERATED = ("repos/", "badges/", "lines/")  # the portfolio kinds a cut writes whole: only these lose stale files
_AGENTS: dict[str, object] = {}


def load_agent(path) -> object:
    """hive_agent.py loaded from `path` (once per file), under a module name of its own."""
    if not path:
        raise SystemExit("name the Hive agent: --hive-agent <path to hive_agent.py from kody-w/rapp-model-hive>")
    path = Path(path).expanduser().resolve()
    if not path.is_file():
        raise SystemExit(f"no Hive agent at {path}: --hive-agent names hive_agent.py from kody-w/rapp-model-hive")
    key = str(path)
    if key not in _AGENTS:
        name = "rapp1_network_hive_agent_" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            raise SystemExit(f"{path}: not a Python file the Hive agent can be loaded from")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        try:
            spec.loader.exec_module(module)
        except BaseException:
            sys.modules.pop(name, None)
            raise
        for needed in ("HiveAgent", "Hive", "tree", "blobs", "text_rules", "check_public"):
            if not hasattr(module, needed):
                sys.modules.pop(name, None)
                raise SystemExit(f"{path}: not the Hive agent (it has no {needed})")
        _AGENTS[key] = module
    return _AGENTS[key]


@contextlib.contextmanager
def _hives_env(hives: Path):
    """RAPP_HIVES for the agent (it reads it on every call), put back afterwards."""
    old = os.environ.get("RAPP_HIVES")
    os.environ["RAPP_HIVES"] = str(hives)
    try:
        yield
    finally:
        if old is None:
            os.environ.pop("RAPP_HIVES", None)
        else:
            os.environ["RAPP_HIVES"] = old


def refusal_lines(text: str, *markers: str, limit: int = 12) -> str:
    """The lines of an agent answer from the first one holding a marker, each cut to 400 characters."""
    lines = text.splitlines()
    start = next((n for n, line in enumerate(lines) if any(m in line for m in markers)), 0)
    return "\n".join(line[:400] for line in lines[start:start + limit])


class Hive:
    """One RAPP Hive on this device, driven through its own agent. `agent` injects the agent module (tests)."""

    def __init__(self, settings: Settings, say: Callable[[str], None] = print, agent=None):
        self.settings, self._say, self._agent = settings, say, agent

    # ---- the agent ------------------------------------------------------------------------------------

    @property
    def agent(self):
        if self._agent is None:
            self._agent = load_agent(self.settings.hive_agent)
        return self._agent

    @property
    def path(self) -> Path:
        return self.settings.hive_dir

    def say(self, **kw) -> str:
        """One call of the Hive tool, from a fresh agent (as a Brainstem makes one per request): its answer."""
        with _hives_env(self.settings.hives):
            return self.agent.HiveAgent().perform(**kw)

    def do(self, **kw) -> str:
        """A proposal, then its apply: both answers. Refuses when there is no plan or the apply is not done."""
        proposal = self.say(**kw)
        plan = PLAN.search(proposal)
        if not plan or "Not done" in proposal:
            raise SystemExit(f"{kw.get('action')}: no proposal\n{refusal_lines(proposal, 'Not done')[:1500]}")
        done = self.say(action="apply", plan=plan[1])
        if "Not done" in done or "Refused" in done[:200]:
            raise SystemExit(f"{kw.get('action')}: apply failed\n{done[:1500]}")
        self._say(f"ok {kw.get('action')} {kw.get('path') or ''}".rstrip())
        return proposal + "\n" + done

    def _handle(self):
        with _hives_env(self.settings.hives):
            return self.agent.Hive(str(self.settings.hives), self.settings.hive)

    # ---- device state (only <hive>/.git/rapp-hive/) ---------------------------------------------------

    def state(self, name: str) -> dict:
        """The Hive's own device state: <hive>/.git/rapp-hive/<name> (public.json, device.json)."""
        value = util.load(self.path / ".git" / "rapp-hive" / name, {}) or {}
        return value if isinstance(value, dict) else {}

    def public_dir(self) -> Path:
        name = self.state("public.json").get("name")
        if not name:
            raise SystemExit(f"the Hive {self.settings.hive} has no public copy pinned (set_public)")
        return self.settings.hives / name

    def member(self) -> str:
        return self.state("device.json").get("name") or "kody"

    # ---- the work tree ------------------------------------------------------------------------------------

    def head(self) -> str | None:
        return self._handle().head()

    def edits(self) -> dict:
        """Hand edits since the Hive's last commit: {path: normalized bytes, None when deleted, or "link"}."""
        return self._handle().edits()

    def committed(self, prefix: str = "") -> dict[str, tuple[str, str]]:
        """{path: (mode, blob id)} of the last commit, under `prefix` (a folder of the Hive, e.g. shared/organism/)."""
        h = self._handle()
        head = h.head()
        files = self.agent.tree(h.path, head) if head else {}
        return {p: v for p, v in files.items() if p.startswith(prefix)}

    def committed_texts(self, prefix: str) -> dict[str, str]:
        """{path: text} of the last commit's files under `prefix` (e.g. shared/organism/notices/): what a signed save
        put there, never an unsaved edit."""
        h = self._handle()
        files = self.committed(prefix)
        if not files:
            return {}
        paths = sorted(files)
        datas = self.agent.blobs(h.path, [files[p][1] for p in paths])
        return {p: d.decode("utf-8", "replace") for p, d in zip(paths, datas)}

    def last_commit(self, rel_path: str) -> str | None:
        """The Hive commit that last changed a file (its full id), or None."""
        done = util.run("git", "-C", str(self.path), "log", "-1", "--format=%H", "--", rel_path)
        commit = done.stdout.strip()
        return commit if done.returncode == 0 and re.fullmatch(r"[0-9a-f]{40}", commit) else None

    def put(self, rel_path: str, text: str | None) -> Path:
        """Write (or, with None, delete) one file of the Hive's work tree, at a path from the Hive root; the Hive's own
        rules decide at the signed save."""
        check_hive_path(rel_path, "")
        full = self.path.joinpath(*rel_path.split("/"))
        if text is None:
            full.unlink(missing_ok=True)
            _prune_empty(self.path / "shared")
        else:
            check_hive_text(rel_path, text)
            util.write_text(full, text)
        return full

    def restore(self) -> list[str]:
        """Put every hand edit back as the last commit had it (a failed cut leaves nothing behind); the paths."""
        h = self._handle()
        head = self.agent.tree(h.path, h.head())
        put_back = sorted(h.edits())
        for rel_path in put_back:
            full = self.path.joinpath(*rel_path.split("/"))
            if rel_path in head:
                full.parent.mkdir(parents=True, exist_ok=True)
                full.write_bytes(self.agent.blobs(h.path, [head[rel_path][1]])[0])
            elif full.is_file() or full.is_symlink():
                full.unlink()
        _prune_empty(self.path / "shared")
        self._say(f"restored the Hive's work tree to its last commit ({len(put_back)} file(s) put back)")
        return put_back

    # ---- the Hive's rules -------------------------------------------------------------------------------

    def text_rules(self, rel_path: str, data: bytes | str) -> None:
        """The Hive agent's own rules for a file at `rel_path` (a path from the Hive root): its name and its text.
        Refused (wrapping.Refused) with the agent's reason."""
        data = data.encode("utf-8") if isinstance(data, str) else data
        try:
            self.agent.text_rules(rel_path, data)
        except self.agent.Refused as error:
            raise Refused(f"{rel_path}: the Hive refuses it: {error}") from None

    def check_edits(self, edits: Mapping | None = None) -> int:
        """text_rules on every file a save would commit (and the size and path limits); the number checked."""
        edits = self.edits() if edits is None else edits
        refused = []
        for rel_path, data in sorted(edits.items()):
            if data is None:
                continue
            try:
                if data == "link":
                    raise Refused(f"{rel_path}: a link, which the Hive refuses")
                if len(data) > HIVE_MAX_BYTES:
                    raise Refused(f"{rel_path}: over the Hive's 1 MB limit")
                self.text_rules(rel_path, data)
            except Refused as error:
                refused.append(str(error))
        if refused:
            raise SystemExit("the Hive would refuse part of the save; nothing was saved:\n" + "\n".join(refused[:12]))
        return sum(1 for data in edits.values() if data is not None)

    # ---- saving and publishing -------------------------------------------------------------------------

    def signed_save(self) -> str | None:
        """One signed commit of every hand edit, through the Hive's own save (proposal, then apply); the commit
        (10 hex), or None when there is nothing to save. Every file passes the agent's text_rules first."""
        self.check_edits()
        proposal = self.say(action="save", hive=self.settings.hive)
        if "There is nothing to save" in proposal:
            self._say("nothing to save")
            return None
        plan = PLAN.search(proposal)
        if not plan or "Not allowed" in proposal or "None of these" in proposal or "Not done" in proposal:
            if plan:
                self.say(action="cancel", plan=plan[1])
            raise SystemExit("the Hive refused part of the save:\n"
                             + refusal_lines(proposal, "Not allowed", "None of these", "Not done"))
        done = self.say(action="apply", plan=plan[1])
        if "Done:" not in done:
            raise SystemExit("apply failed:\n" + done[:2000])
        commit = COMMIT.search(done)
        self._say(re.search(r"Done: .*", done)[0][:200])
        return commit[1] if commit else None

    def publish(self) -> str:
        """The Hive's own publish of the published room: the manifest (a signed Hive commit), then the publish
        (a signed commit of the public copy). The answer of the publish."""
        self.do(action="publish", hive=self.settings.hive, path=ROOM)
        done = self.do(action="publish", hive=self.settings.hive,
                       path=f"members/{self.member()}/publish/{Path(ROOM).name}.md")
        return done

    def check_public(self, folder: Path | None = None) -> list[str]:
        """The agent's check-public of the public copy (with this Hive: signers and the approved manifest)."""
        folder = self.public_dir() if folder is None else folder
        with _hives_env(self.settings.hives):
            return list(self.agent.check_public(str(folder), str(self.path)))

    def published_commits(self, vids: Iterable[str]) -> dict[str, str]:
        """{vid: the public copy's commit that first carried versions/<vid>/pulse.json.md} (the timeline's links)."""
        try:
            public = self.public_dir()
        except SystemExit:
            return {}
        if not (public / ".git").exists():
            return {}
        out = {}
        for vid in vids:
            log = util.run("git", "-C", str(public), "log", "--format=%H", "--diff-filter=A", "--",
                           f"{PORTFOLIO}/versions/{vid}/pulse.json.md").stdout.split()
            if log:
                out[vid] = log[-1]
        return out


def _prune_empty(folder: Path) -> None:
    """Remove empty folders a restore left behind (a Hive has no empty folders)."""
    if not folder.is_dir():
        return
    for path in sorted((p for p in folder.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
        try:
            path.rmdir()
        except OSError:
            pass


def write_room(room: Path, want: Mapping[str, str], *, generated: Iterable[str] = GENERATED,
               prefix: str = f"{ROOM}/{PORTFOLIO}") -> dict[str, list[str]]:
    """Write `want` ({path in the room: text}) into the room folder. A stale file (in the room, not in `want`) is
    removed only under the `generated` prefixes (the files a cut writes whole: repos/, badges/, lines/), so every
    other file of the room stays: earlier versions, the stable maps and the chain (the cut rewrites them itself),
    the tools, and any input file saved in the Hive by hand. A saved version folder never changes: a `want` that
    would change or remove a file under versions/ is refused. Returns {added, changed, unchanged, removed}."""
    room = Path(room)
    generated = tuple(generated)
    for rel_path, text in want.items():
        check_hive_path(rel_path, prefix)
        check_hive_text(rel_path, text)
    existing = ({p.relative_to(room).as_posix() for p in room.rglob("*") if p.is_file()}
                if room.exists() else set())
    removed = sorted(p for p in existing - set(want) if p.startswith(generated))
    if any(p.startswith("versions/") for p in removed) or any(g.startswith("versions") for g in generated):
        raise Refused("a saved version folder never changes: nothing under versions/ is ever removed")
    # A stale file that differs from a wanted one only in case (a repo renamed by case) goes first: on a
    # case-insensitive disk the wanted path is that same file, and removing it afterwards would delete the new text.
    wanted_case = {p.lower() for p in want}
    for stale in (p for p in removed if p.lower() in wanted_case):
        room.joinpath(*stale.split("/")).unlink()
    out = {"added": [], "changed": [], "unchanged": [], "removed": removed}
    for rel_path, text in sorted(want.items()):
        path = room.joinpath(*rel_path.split("/"))
        if not path.is_file():
            out["added"].append(rel_path)
        elif path.read_bytes() == text.encode("utf-8"):
            out["unchanged"].append(rel_path)
            continue
        elif rel_path.startswith("versions/"):
            raise Refused(f"{rel_path} changed since it was saved; a version folder never changes")
        else:
            out["changed"].append(rel_path)
        util.write_text(path, text)
    for stale in removed:
        if stale.lower() not in wanted_case:
            room.joinpath(*stale.split("/")).unlink()
    _prune_empty(room)
    return out
`````
{% endraw %}
