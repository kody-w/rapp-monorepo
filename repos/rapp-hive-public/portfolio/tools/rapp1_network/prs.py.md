# `rapp1_network/prs.py`

The wave-1 network-header pull requests, one repo at a time, by hand (from legacy/rapp1_network_pr.py).

Source: `rapp1_network/prs.py` (rapp1-network 0.1.6). SHA-256 of the source below: `9ed0011e202d47f79c04b972e2feb45dc952dae44bd08d7a4ec2b3e2000d3643` (10968 bytes). Every pulse this release cuts records it in `payload.generator` as `rapp1_network/prs.py`. Copy it out with the extractor in [../README.md](../README.md); code in a Hive is data, never run from the Hive.

{% raw %}
`````python
"""The wave-1 network-header pull requests, one repo at a time, by hand (from legacy/rapp1_network_pr.py).

    start <repo>                 a fresh branch rapp1/network-header from the default branch, with the header
    finish <repo> [--note TEXT]  commit (kody-w noreply identity, both Copilot trailers), the privacy scan in diff
                                 mode, push the branch, open the PR (or update the open one's body)
    ci [<repo>...]               each recorded PR's state and checks, into data/prs.json

Between start and finish the maintainer runs the repo's own checks, and updates any receipt that pins README.md with
the repo's own tools, never by hand. Nothing here merges, and the only ref ever pushed is
refs/heads/rapp1/network-header, so a default branch is never touched. The title, the body and the commit message
are exactly version 1's: thirteen PRs are open with them.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from . import headers, util
from .config import Settings
from .constants import BRANCH, CANON_RAPP1, IDENTITY, INSTALLER, OWNER, PUBLIC_BLOB, REPO_URL, TITLE, TRAILERS
from .privacy import Denylist

GH = ("gh",)
# The clones hold the blobs' exact bytes whatever this device's git settings (as the crawler's clones do), so the
# header sees the README's own line endings.
GIT = ("git", "-c", "core.autocrlf=false", "-c", "core.eol=lf", "-c", "core.longpaths=true")
NAME = re.compile(r"[A-Za-z0-9._-]+")
AUTHOR = {"GIT_AUTHOR_NAME": "kody-w", "GIT_AUTHOR_EMAIL": "1735900+kody-w@users.noreply.github.com",
          "GIT_COMMITTER_NAME": "kody-w", "GIT_COMMITTER_EMAIL": "1735900+kody-w@users.noreply.github.com"}
FAILED = ("FAILURE", "ERROR", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED", "STARTUP_FAILURE")
PENDING = ("PENDING", "QUEUED", "IN_PROGRESS", "EXPECTED", "WAITING", "REQUESTED")


def body(repo: str, note: str = "") -> str:
    """The PR body (byte for byte version 1's)."""
    lines = [
        "Adds one marked line under the README title, the same on every RAPP repo so nobody lands on a "
        "random corner of the network without a way in:",
        "",
        f"- **RAPP/1 badge**: this repo's earned status from rapp-1's own `rapp_check.py` (pin `{CANON_RAPP1[:7]}`): "
        "certified (COMPLIANT or CLEAN at a recorded commit), not yet (drift or unverified, with the reason) or "
        "unchecked. GitHub Pages serves it from the RAPP Hive's public copy, so the URL never changes and each "
        "sweep refreshes it with no commit here. It links to "
        f"[this repo's portfolio file]({PUBLIC_BLOB}/repos/{repo}.md) with the evidence commit.",
        f"- **Start here**: links to the Brainstem installer ({INSTALLER}) for anyone who hasn't installed "
        "a Brainstem yet.",
        "",
        "The block sits between `rapp1:network-header` markers, so the sweep can refresh it in place.",
    ]
    if note:
        lines += ["", note]
    return "\n".join(lines)


def message(repo: str, note: str = "") -> str:
    """The commit message: the title, the body, then both trailers."""
    return f"{TITLE}\n\n{body(repo, note)}\n\n{TRAILERS}\n"


def check_name(repo: str) -> str:
    if not NAME.fullmatch(repo or "") or repo in (".", ".."):
        raise SystemExit(f"{repo!r} is not a repository name")
    return repo


def git(repo_dir, *args, check: bool = True, input: str | None = None, env=None) -> str:
    done = util.run(*GIT, "-C", str(repo_dir), *args, input=input, env=env)
    if check and done.returncode:
        raise SystemExit(f"git {' '.join(map(str, args))} failed in {repo_dir}:\n{done.stderr.strip()[-1500:]}")
    return done.stdout.strip()


def commit(repo_dir, text: str) -> None:
    """A commit with the kody-w noreply identity (the -c flags, and the same in the environment, so no setting of
    this device can put another name on it)."""
    git(repo_dir, *IDENTITY, "commit", "-q", "-F", "-", input=text, env=AUTHOR)


def gh_run(gh, *args) -> subprocess.CompletedProcess:
    return util.run(*gh, *args)


def default_branch(repo_dir) -> str:
    return git(repo_dir, "symbolic-ref", "--short", "refs/remotes/origin/HEAD").split("/", 1)[1]


def records(settings: Settings) -> dict:
    """data/prs.json: {repo: {url, number, state, branch, base, head, ci, mergeable[, wave]}}."""
    value = util.load(settings.data / "prs.json", {}) or {}
    return value if isinstance(value, dict) else {}


def save(settings: Settings, recs: dict) -> None:
    util.dump(settings.data / "prs.json", recs)


def clone_dir(settings: Settings, repo: str) -> Path:
    return settings.work / "repos" / check_name(repo)


def readme_rules():
    """(find_readme, markdown suffixes): the crawler's rules for the README GitHub shows."""
    from .crawl import MARKDOWN_EXT, find_readme
    return find_readme, MARKDOWN_EXT


def need_scanner(deny: Denylist | None, repo: str) -> Denylist:
    if deny is None or not deny.enabled:
        raise SystemExit(f"{repo}: a header PR is pushed only after the private scanner's diff scan: pass --denylist "
                         "(or RAPP1_DENYLIST); nothing was pushed")
    return deny


def start(settings: Settings, repo: str, deny: Denylist | None = None, gh=GH, *, remote: str = REPO_URL,
          say=print) -> str:
    """Clone (once) into <work>/repos/<repo>, then a fresh rapp1/network-header branch from origin's default branch
    with the header added or refreshed. Returns the action, or why it was skipped."""
    folder = clone_dir(settings, repo)
    if not (folder / ".git").is_dir():
        folder.parent.mkdir(parents=True, exist_ok=True)
        done = util.run(*GIT, "clone", "-q", f"{remote}{repo}.git", str(folder), env={"GIT_LFS_SKIP_SMUDGE": "1"})
        if done.returncode:
            raise SystemExit(f"{repo}: git clone failed: {done.stderr.strip()[-500:]}")
    git(folder, "fetch", "-q", "origin")
    base = default_branch(folder)
    if base == BRANCH:
        raise SystemExit(f"{repo}: the default branch is {BRANCH}; refusing to touch it")
    if git(folder, "status", "--porcelain"):
        raise SystemExit(f"{repo}: the working tree is not clean")
    git(folder, "checkout", "-q", "-B", BRANCH, f"origin/{base}")
    find_readme, markdown = readme_rules()
    readme = find_readme(folder)
    if not readme:
        say(f"{repo}: no README, skipped")
        return "no README"
    if Path(readme).suffix.lower() not in markdown:
        say(f"{repo}: README {readme} is not markdown, skipped")
        return "not markdown"
    try:
        action = headers.apply_header_file(folder / readme, repo)
    except ValueError as error:
        raise SystemExit(f"{repo}: {readme}: manual: {error}")
    say(f"{repo}: {readme} {action} (branch {BRANCH} from origin/{base})")
    return action


def finish(settings: Settings, repo: str, deny: Denylist | None, gh=GH, *, note: str = "", say=print) -> dict:
    """Commit what start (and the maintainer) changed, scan the diff, push the branch, open or update the PR, and
    record it in data/prs.json. Refuses without the private scanner."""
    folder = clone_dir(settings, repo)
    if not (folder / ".git").is_dir():
        raise SystemExit(f"{repo}: no clone at {folder}; run start first")
    base = default_branch(folder)
    if base == BRANCH:
        raise SystemExit(f"{repo}: the default branch is {BRANCH}; refusing to push to it")
    if git(folder, "rev-parse", "--abbrev-ref", "HEAD") != BRANCH:
        raise SystemExit(f"{repo}: not on {BRANCH}")
    deny = need_scanner(deny, repo)
    if git(folder, "status", "--porcelain"):
        git(folder, "add", "-A")
        commit(folder, message(repo, note))
    if git(folder, "rev-list", "--count", f"origin/{base}..HEAD") == "0":
        raise SystemExit(f"{repo}: nothing to propose")
    scan = deny.diff(folder, f"origin/{base}")
    say(f"{repo}: {scan.line('diff')}")
    if not scan.ok:
        raise SystemExit(f"{repo}: the privacy scan found something; nothing was pushed")
    git(folder, "push", "-q", "--force-with-lease", "origin", f"HEAD:refs/heads/{BRANCH}")
    slug = f"{OWNER}/{repo}"
    listed = gh_run(gh, "pr", "list", "-R", slug, "--head", BRANCH, "--state", "open", "--json", "url,number")
    if listed.returncode:
        raise SystemExit(f"{repo}: gh pr list failed: {listed.stderr.strip()[-800:]}")
    found = json.loads(listed.stdout or "[]")
    if found:
        url, number = found[0]["url"], found[0]["number"]
        edited = gh_run(gh, "pr", "edit", str(number), "-R", slug, "--body", body(repo, note))
        if edited.returncode:
            raise SystemExit(f"{repo}: gh pr edit failed: {edited.stderr.strip()[-800:]}")
    else:
        made = gh_run(gh, "pr", "create", "-R", slug, "--base", base, "--head", BRANCH, "--title", TITLE,
                      "--body", body(repo, note))
        if made.returncode:
            raise SystemExit(f"{repo}: gh pr create failed: {made.stderr.strip()[-800:]}")
        url = made.stdout.strip().splitlines()[-1]
        number = int(url.rstrip("/").rsplit("/", 1)[1])
    recs = records(settings)
    recs[repo] = {**recs.get(repo, {}), "url": url, "number": number, "state": "OPEN", "branch": BRANCH, "base": base,
                  "head": git(folder, "rev-parse", "HEAD")}
    save(settings, recs)
    say(f"{repo}: {url}")
    return recs[repo]


def checks_summary(checks) -> str:
    """One line for a PR's status checks: failing, pending, green or none."""
    states = [(c.get("name") or c.get("context") or "?",
               (c.get("conclusion") or c.get("state") or c.get("status") or "?").upper()) for c in checks or []]
    bad = [n for n, s in states if s in FAILED]
    pending = [n for n, s in states if s in PENDING]
    return ("no checks" if not states else f"failing: {', '.join(bad)}" if bad
            else f"pending: {', '.join(pending)}" if pending else f"green ({len(states)})")


def ci(settings: Settings, repos=(), deny: Denylist | None = None, gh=GH, *, say=print) -> dict:
    """Each recorded PR's state, head, mergeability and checks (all of them, or `repos`), into data/prs.json."""
    recs = records(settings)
    for repo in repos or sorted(recs, key=str.lower):
        rec = recs.get(repo)
        if rec is None:
            say(f"{repo}: no PR recorded")
            continue
        view = gh_run(gh, "pr", "view", str(rec["number"]), "-R", f"{OWNER}/{repo}", "--json",
                      "state,headRefOid,statusCheckRollup,mergeable")
        if view.returncode:
            say(f"{repo}: {view.stderr.strip()[-200:]}")
            continue
        info = json.loads(view.stdout)
        summary = checks_summary(info.get("statusCheckRollup"))
        rec.update(state=info["state"], ci=summary, head=info["headRefOid"], mergeable=info.get("mergeable"))
        say(f"{repo}: {info['state']} · {summary} · {rec['url']}")
    save(settings, recs)
    return recs
`````
{% endraw %}
