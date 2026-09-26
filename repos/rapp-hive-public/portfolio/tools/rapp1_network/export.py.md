# `rapp1_network/export.py`

The pinned release copy for the RAPP Hive's `portfolio/tools/`: the package's own sources, as data.

Source: `rapp1_network/export.py` (rapp1-network 0.1.5). SHA-256 of the source below: `0ce9bc90a6e7e81f4aa84b467ef4fc7859b655238de304398190854a19f29e59` (16940 bytes). Every pulse this release cuts records it in `payload.generator` as `rapp1_network/export.py`. Copy it out with the extractor in [../README.md](../README.md); code in a Hive is data, never run from the Hive.

{% raw %}
`````python
"""The pinned release copy for the RAPP Hive's `portfolio/tools/`: the package's own sources, as data.

A Hive holds only markdown and never runs what it holds, so every source file of `rapp1_network` becomes one
`tools/rapp1_network/<file>.md` with the source in a `{% raw %}` block and a 5-backtick python fence (as version 1's
`tool_files()` did for its two files), its source path, SHA-256 and size above it. Beside them:

- `tools/RELEASE.md`: the package version, its tag and rapp1-network commit, each file's SHA-256 and bytes, and the
  pulse `generator` every version this release cuts records (`{"rapp1_network/<file>": sha256}`, contract §5);
- `tools/README.md`: which tools made which versions (version 1: the two legacy files, kept byte for byte beside
  the package; version 2 onwards: the package), and an extractor that rebuilds the package from the markdown,
  checks every hash against its file and RELEASE.md, and runs `python -m rapp1_network verify ..`.

Version 1's `tools/rapp1_portfolio.py.md` and `tools/rapp1_subway.py.md` are live URLs: they are never written,
changed or removed here. The release copy is public: it holds nothing private (no denylist, no device path).
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Mapping

from . import __version__
from .constants import OWNER
from .pulses import generator_for
from .util import run, sha256
from .wrapping import Refused

PACKAGE = "rapp1_network"
TOOLS = "tools"  # the release copy's folder in the portfolio room (served as portfolio/tools/)
LEGACY_TOOLS = ("rapp1_portfolio.py", "rapp1_subway.py")  # version 1's generator: tools/<name>.md, never changed
CODE_FENCE, LB = "`" * 5, "{"
RAW_START, RAW_END = LB + "% raw %}", LB + "% endraw %}"  # composed, so this file never ends a raw block itself
SOURCE_LINE = re.compile(r"^Source: `([^`]+)`", re.M)
SHA_LINE = re.compile(r"SHA-256 of the source below: `([0-9a-f]{64})` \(([0-9]+) bytes\)")
HIDDEN = re.compile("[\x00-\x08\x0b-\x1f\x7f-\x9f\u200b-\u200f\u2028-\u202e\u2060-\u206f\ufeff]")


def package_dir() -> Path:
    return Path(__file__).resolve().parent


def sources(folder: Path | None = None) -> dict[str, str]:
    """{file name: source text} for every Python file of the package folder (the package is its .py files; an editor's
    backup or a cache is never part of a release), refused unless each is UTF-8 text the Hive keeps byte for byte:
    NFC (the Hive normalizes what it saves), LF only, ending in LF, and holding neither the fence nor the endraw
    sequence that would end its block."""
    folder = Path(folder) if folder is not None else package_dir()
    out = {}
    for path in sorted(folder.iterdir()):
        if not path.is_file() or path.suffix != ".py" or path.name.startswith("."):
            continue
        try:
            text = path.read_bytes().decode("utf-8")
        except UnicodeDecodeError:
            raise Refused(f"{path.name}: not UTF-8 text, so it cannot be a file of the release copy") from None
        if not unicodedata.is_normalized("NFC", text):
            raise Refused(f"{path.name}: not NFC; the Hive would normalize it and its hash would change")
        if "\r" in text or not text.endswith("\n") or HIDDEN.search(text):
            raise Refused(f"{path.name}: the release copy holds LF text ending in LF, without control or "
                          "invisible characters")
        if CODE_FENCE in text or RAW_END in text:
            raise Refused(f"{path.name} holds a sequence that would end its own block")
        out[path.name] = text
    if "__init__.py" not in out:
        raise Refused(f"{folder}: not the {PACKAGE} package (no __init__.py)")
    return out


def md_name(name: str) -> str:
    """The Hive file of one source: `<name>.md`, or `package-<name>.md` for a name the Hive refuses (its names
    start with a letter or digit, so __init__.py is package-__init__.py.md; no module name holds a dash)."""
    return f"{name}.md" if name[:1].isalnum() else f"package-{name}.md"


def generator(files: Mapping[str, str]) -> dict[str, str]:
    """The pulse generator of a release copy: {"rapp1_network/<file>": SHA-256 of its source}, every file."""
    return generator_for({f"{PACKAGE}/{name}": text for name, text in files.items()})


def purpose(text: str) -> str:
    """A source's one-line purpose: the first line of its module docstring."""
    found = re.match(r'(?:#![^\n]*\n)?\s*[rub]*("""|\'\'\')(.*?)\1', text, re.S)
    first = (found[2].strip().split("\n\n")[0] if found else "").replace("\n", " ")
    return " ".join(first.split()) or "A source file of the package."


def provenance(folder: Path | None = None) -> dict:
    """{version, tag, commit, clean} of the running package: its git commit and tag when it runs from a checkout
    of rapp1-network (tag: an exact tag on that commit), and whether its folder has no uncommitted change."""
    folder = Path(folder) if folder is not None else package_dir()
    out = {"version": __version__, "tag": None, "commit": None, "clean": None}
    top = run("git", "-C", str(folder), "rev-parse", "--show-toplevel")
    if top.returncode or not (Path(top.stdout.strip()) / "src" / PACKAGE).resolve() == folder.resolve():
        return out  # not a checkout of rapp1-network (an installed or extracted copy): no commit to name
    commit = run("git", "-C", str(folder), "rev-parse", "HEAD").stdout.strip()
    tag = run("git", "-C", str(folder), "describe", "--tags", "--exact-match", "HEAD")
    status = run("git", "-C", str(folder), "status", "--porcelain", "--", ".")
    out.update(commit=commit or None, tag=tag.stdout.strip() or None if tag.returncode == 0 else None,
               clean=status.returncode == 0 and not status.stdout.strip())
    return out


def source_file(name: str, text: str, release: Mapping) -> str:
    """tools/rapp1_network/<md name>: one source in its block, with its path, hash and size above it."""
    return (f"# `{PACKAGE}/{name}`\n\n{purpose(text)}\n\n"
            f"Source: `{PACKAGE}/{name}` (rapp1-network {release['version']}). SHA-256 of the source below: "
            f"`{sha256(text)}` ({len(text.encode('utf-8'))} bytes). Every pulse this release cuts records it in "
            f"`payload.generator` as `{PACKAGE}/{name}`. Copy it out with the extractor in [../README.md](../README.md); "
            "code in a Hive is data, never run from the Hive.\n\n"
            f"{RAW_START}\n{CODE_FENCE}python\n{text}{CODE_FENCE}\n{RAW_END}\n")


def release_md(files: Mapping[str, str], release: Mapping) -> str:
    gen = generator(files)
    commit = release.get("commit")
    made = (f"rapp1-network commit `{commit}`" + ("" if release.get("clean") in (True, None) else
                                                 " with local changes (the hashes below are the files as they ran)")
            if commit else "no recorded rapp1-network commit (the hashes below are the files as they ran)")
    rows = [f"| `{PACKAGE}/{name}` | [`{md_name(name)}`]({PACKAGE}/{md_name(name)}) | `{sha256(text)}` | "
            f"{len(text.encode('utf-8'))} |" for name, text in sorted(files.items())]
    return "\n".join([
        "# Release copy", "",
        f"Package `{PACKAGE}`, rapp1-network {release['version']}"
        + (f" (tag `{release['tag']}`)" if release.get("tag") else " (no tag)") + f", made from {made}.", "",
        f"Its {len(files)} source file(s), each in one markdown file of `{PACKAGE}/` (linked below), with the SHA-256 and "
        "size of the source as the extractor in [README.md](README.md) writes it back:", "",
        "| Source | Markdown | SHA-256 | Bytes |", "|---|---|---|---|", *rows, "",
        "Every pulse this release cuts records exactly this `generator` in its payload:", "",
        "```json", json.dumps(gen, indent=1, sort_keys=True), "```", "",
        "Version 1's pulse names the two single-file tools instead (`rapp1_portfolio.py`, `rapp1_subway.py`), kept "
        "unchanged beside this copy.", ""])


EXTRACTOR = r"""python3 - <<'PY'
import hashlib, json, os, pathlib, re, subprocess, sys
fence, tick, out = chr(96) * 5, chr(96), pathlib.Path('release')
release = pathlib.Path('RELEASE.md').read_text(encoding='utf-8')
listed = json.loads(release.split(tick * 3 + 'json\n', 1)[1].split(tick * 3, 1)[0])
found = {}
for md in sorted(pathlib.Path('rapp1_network').glob('*.md')):
    text = md.read_text(encoding='utf-8')
    data = text.split(fence + 'python\n', 1)[1].rsplit(fence + '\n', 1)[0].encode('utf-8')
    path = re.search(r'^Source: .(rapp1_network/[^/ ]+?). ', text, re.M).group(1)
    want, size = re.search(r'SHA-256 of the source below: .([0-9a-f]{64}). .([0-9]+) bytes.', text).groups()
    assert hashlib.sha256(data).hexdigest() == want == listed.get(path) and len(data) == int(size), md.name
    assert path not in found, path
    found[path] = data
assert sorted(found) == sorted(listed), 'the markdown files are not exactly the files RELEASE.md lists'
for path, data in found.items():
    (out / path).parent.mkdir(parents=True, exist_ok=True)
    (out / path).write_bytes(data)
    print('ok', path, listed[path])
env = {**os.environ, 'PYTHONPATH': str(out.resolve())}
sys.exit(subprocess.run([sys.executable, '-B', '-m', 'rapp1_network', 'verify', '..', '--work', str(out)], env=env).returncode)
PY"""

LEGACY_EXTRACTOR = r"""python3 - <<'PY'
import hashlib, pathlib, re
fence = chr(96) * 5
for md in sorted(pathlib.Path('.').glob('*.py.md')):
    text = md.read_text(encoding='utf-8')
    source = text.split(fence + 'python\n', 1)[1].rsplit(fence + '\n', 1)[0]
    want = re.search(r'SHA-256 of the source below: .([0-9a-f]+).', text).group(1)
    assert hashlib.sha256(source.encode('utf-8')).hexdigest() == want, md.name
    pathlib.Path(md.name[:-3]).write_text(source, encoding='utf-8')
    print('ok', md.name[:-3], want)
PY"""


PUBLIC_TREE = f"https://github.com/{OWNER}/rapp-hive-public/tree"


def _versions(numbers: list[int]) -> str:
    return f"Version {numbers[0]}" if len(numbers) == 1 else f"Versions {numbers[0]} to {numbers[-1]}"


def made_by(release: Mapping, history=None, current: Mapping | None = None) -> list[str]:
    """Which tools made which version, from each pulse's `generator` (`history`: [(number, vid, generator,
    public commit that first carried it or None)], oldest first, the version being cut last). Version 1's two files
    stay here; the current release is this folder; an earlier release's copy is in the public copy's history."""
    legacy = ("- **Version 1** (pulse 0) was made by the two single-file tools `rapp1_portfolio.py` and "
              "`rapp1_subway.py`, kept here unchanged ([rapp1_portfolio.py.md](rapp1_portfolio.py.md), "
              "[rapp1_subway.py.md](rapp1_subway.py.md)); version 1's pulse names their SHA-256 in `payload.generator`.")
    this = (f"made by the package `{PACKAGE}` (rapp1-network {release['version']}), every source file of it in "
            f"`{PACKAGE}/`: [RELEASE.md](RELEASE.md) links each file and lists its SHA-256 and size, the release and its "
            "commit, and the `generator` each of its pulses records.")
    if not history:
        return [legacy, f"- **Package versions** are {this}"]
    lines, groups = [], []
    for number, _vid, gen, first in history:
        if not any(str(name).startswith(f"{PACKAGE}/") for name in gen):
            if not lines:
                lines.append(legacy)
            continue
        if groups and groups[-1][1] == gen:
            groups[-1][0].append(number)
        else:
            groups.append(([number], gen, first))
    for k, (numbers, gen, first) in enumerate(groups):
        if current is not None and gen == current and k == len(groups) - 1:
            lines.append(f"- **Version {numbers[0]} onwards** are {this}")
        elif first:
            lines.append(f"- **{_versions(numbers)}** {'was' if len(numbers) == 1 else 'were'} made by an earlier release "
                         f"of the package: its release copy is in this public copy's history at commit "
                         f"[`{first[:7]}`]({PUBLIC_TREE}/{first}/portfolio/tools) (its RELEASE.md names the release), "
                         "and each pulse names every file's SHA-256 in `payload.generator`.")
        else:
            lines.append(f"- **{_versions(numbers)}** {'was' if len(numbers) == 1 else 'were'} made by an earlier release "
                         "of the package; each pulse names every file's SHA-256 in `payload.generator`.")
    return lines


def readme(release: Mapping, history=None, current: Mapping | None = None) -> str:
    return "\n".join([
        "# Tools", "",
        "The standard-library Python tools that made this portfolio, as data: a Hive holds only markdown, so each "
        "source file is one `.md` file with the source in a fenced block and its SHA-256 above it. Code in a Hive "
        "is never run from the Hive; copy it out first.", "",
        *made_by(release, history, current), "",
        "Rebuild the package from the markdown, check every file against its hash and RELEASE.md, and verify the "
        "published chain with it (run this in a clone of `kody-w/rapp-hive-public`, inside `portfolio/tools/`; it "
        "needs git and Python 3.12, writes the package to `release/`, and clones `kody-w/rapp-1` at the canon pin "
        "into `release/checker/rapp-1` unless `RAPP1_CHECKER` names a checkout at the pin):", "",
        "```bash", EXTRACTOR, "```", "",
        "`python -m rapp1_network verify ..` checks every pulse from the published genesis (RAPP/1 §7.5 steps 1-5 with "
        "rapp-1's reference `rapp.py`), rapp-1's own `rapp_check.py` on the chain, and each version's maps against "
        "the hashes its pulse recorded.", "",
        "Crawl again and cut the next version (needs git, a signed-in `gh`, Chrome, and a Hive with `hive_agent.py` "
        "from `kody-w/rapp-model-hive`):", "",
        "```bash",
        "PYTHONPATH=release python3 -B -m rapp1_network crawl --work <work folder> --hive-agent <path to hive_agent.py> "
        "[--denylist <private scanner>]",
        "```", "",
        "Version 1's two files, copied out and checked the way version 1's README said:", "",
        "```bash", LEGACY_EXTRACTOR, "```", ""])


def tool_files(files: Mapping[str, str] | None = None, *, release: Mapping | None = None,
               history=None) -> dict[str, str]:
    """{path in the portfolio room: text}: `tools/rapp1_network/<file>.md` for every package source,
    `tools/RELEASE.md` and `tools/README.md`. Version 1's two tool files are not among them: they stay as they are.
    `files` defaults to the running package's sources, `release` to its provenance(); `history` (see made_by) lets
    the README say which release made each version."""
    files = sources() if files is None else dict(files)
    release = {"version": __version__, "tag": None, "commit": None, "clean": None, **(release or {})}
    out = {f"{TOOLS}/{PACKAGE}/{md_name(name)}": source_file(name, text, release) for name, text in sorted(files.items())}
    out[f"{TOOLS}/RELEASE.md"] = release_md(files, release)
    out[f"{TOOLS}/README.md"] = readme(release, history, generator(files))
    for rel_path in out:
        if any(rel_path == f"{TOOLS}/{name}.md" for name in LEGACY_TOOLS):
            raise Refused(f"{rel_path} is version 1's; it never changes")
    return out


def extract(tools_dir: Path, out: Path) -> dict[str, str]:
    """The package rebuilt from a tools/ folder into out/rapp1_network/ (what the README's extractor does, without
    running verify): {path: sha256}, refused unless every file matches its hash and RELEASE.md."""
    tools_dir, out = Path(tools_dir), Path(out)
    listed = json.loads((tools_dir / "RELEASE.md").read_text(encoding="utf-8").split("```json\n", 1)[1]
                        .split("```", 1)[0])
    found = {}
    for md in sorted((tools_dir / PACKAGE).glob("*.md")):
        text = md.read_text(encoding="utf-8")
        source = text.split(CODE_FENCE + "python\n", 1)[1].rsplit(CODE_FENCE + "\n", 1)[0]
        path = SOURCE_LINE.search(text)[1]
        want, size = SHA_LINE.search(text).groups()
        data = source.encode("utf-8")
        if not (sha256(data) == want == listed.get(path) and len(data) == int(size)) or path in found:
            raise Refused(f"{md.name}: its source does not match its hash or RELEASE.md")
        if md.name != md_name(path.split("/", 1)[1]) or not path.startswith(f"{PACKAGE}/"):
            raise Refused(f"{md.name}: not the markdown file of {path}")
        found[path] = want
        target = out.joinpath(*path.split("/"))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    if found != listed:
        raise Refused("the markdown files are not exactly the files RELEASE.md lists")
    return found
`````
{% endraw %}
