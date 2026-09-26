# `rapp1_network/wave2.py`

Wave 2 of the network header: a dry run now, the pull requests only after the owner approves (from legacy/rapp1_wave2.py).

Source: `rapp1_network/wave2.py` (rapp1-network 0.1.5). SHA-256 of the source below: `936214982d06b4369d85793a11494d736196dc22b0ab66bd7639a82f7675122f` (14026 bytes). Every pulse this release cuts records it in `payload.generator` as `rapp1_network/wave2.py`. Copy it out with the extractor in [../README.md](../README.md); code in a Hive is data, never run from the Hive.

{% raw %}
`````python
"""Wave 2 of the network header: a dry run now, the pull requests only after the owner approves
(from legacy/rapp1_wave2.py).

    plan                                                     the dry run, from the crawl's records (no clones)
    open --rehearse [--limit N] [--only a,b]                 everything but the push
    open --owner-approved [--limit N] [--only a,b] [--pace 5]

`plan` writes <work>/wave2/plan.json, DRY-RUN.md and samples/*.diff: for every wave-2 repo, whether a README exists,
the exact action, and why a repo is held for a hand-made PR (receipts that pin the README's bytes, a generated README,
or tests that read it). `open` handles only the rows the plan marks `auto`, one at a time: a fresh shallow clone, the
README's facts checked again on it with the crawler's own rules, the header, a commit with the kody-w noreply identity
and both Copilot trailers, the private scanner's diff scan, a push of rapp1/network-header and an ordinary PR (never
merged, never a push to a default branch). It paces about one PR per 5 s and backs off on GitHub's secondary rate
limits. Repos already in data/prs.json are skipped, so a re-run resumes.
"""
from __future__ import annotations

import re
import time
from collections import Counter
from pathlib import Path

from . import headers, prs, util
from .config import Settings
from .constants import BRANCH, OWNER, REPO_URL, TITLE
from .lines import LINE
from .privacy import Denylist

GENERATED_FROM = "the sweep's fresh clones (data/family.json, sweep/*.record.json)"
COMMAND = "python -m rapp1_network wave2 open --owner-approved --denylist <private scanner>"
APPROVAL = ("wave 2 opens PRs only after the owner approves: re-run with --owner-approved "
            "(or --rehearse to stop before any push)")
RATE_LIMITED = re.compile(r"rate limit|abuse|submitted too quickly|http 429", re.I)
MAX_SAMPLES = 16


def out_dir(settings: Settings) -> Path:
    return settings.work / "wave2"


def family(settings: Settings) -> list[dict]:
    """data/family.json (as inventory.family reads it); refuses when there is none yet."""
    entries = util.load(settings.data / "family.json")
    if not entries or not isinstance(entries, list):
        raise SystemExit("run discover first: there is no data/family.json")
    return entries


def decide(item: dict, rec: dict) -> dict:
    """The item with its action (auto, manual, none or skip) and why, from a record's README facts alone."""
    item = dict(item)
    if not rec.get("evidence_commit"):
        return {**item, "action": "skip", "why": rec.get("reason") or "not crawled yet"}
    readme = rec.get("readme", "")
    if not readme:
        return {**item, "action": "skip", "why": "no README"}
    if not rec.get("readme_markdown"):
        return {**item, "action": "skip", "why": f"README is not markdown ({readme})"}
    action, pinned, tests = rec.get("header_action", ""), rec.get("readme_receipts", []), rec.get(
        "readme_test_readers", [])
    item.update(readme_sha256=rec.get("readme_sha256"), header_action=action, evidence_commit=rec["evidence_commit"])
    if action.startswith("manual"):
        item.update(action="manual", why=action.split(": ", 1)[-1])
    elif action == "unchanged":
        item.update(action="none", why="the header is already current")
    elif pinned:
        item.update(action="manual", why="tracked files pin the README's exact bytes: " + ", ".join(pinned[:6])
                    + (f" and {len(pinned) - 6} more" if len(pinned) > 6 else ""))
    elif rec.get("readme_generated"):
        item.update(action="manual", why="the README says it is generated; change its source instead")
    elif tests:
        item.update(action="manual", why="tests read README.md (run them before a PR): " + ", ".join(tests[:4])
                    + (f" and {len(tests) - 4} more" if len(tests) > 4 else ""))
    else:
        item.update(action="auto", why=action)
    return item


def plan_one(settings: Settings, entry: dict) -> tuple[dict, str | None]:
    """(the plan row for one repo, its header diff or None), from its crawl record alone."""
    repo = entry["repo"]
    rec = util.load(settings.sweep / f"{repo}.record.json", {}) or {}
    item = {"repo": repo, "family": entry["family"], "line": LINE[entry["family"]]["name"],
            "status": rec.get("status", "unchecked"), "default_branch": entry["default_branch"],
            "readme": rec.get("readme", ""), "readme_exists": bool(rec.get("readme"))}
    item = decide(item, rec)
    return item, (rec.get("header_diff") or None) if item["action"] in ("auto", "manual", "none") else None


def pick_samples(items: list[dict]) -> list[str]:
    """One sample diff per (action, header action), then one per line among the automatic ones; at most 16."""
    wanted, seen = [], set()
    for item in items:
        key = (item["action"], item.get("header_action"))
        if item["action"] in ("auto", "manual") and item.get("header_action") and key not in seen:
            seen.add(key)
            wanted.append(item["repo"])
    for item in items:
        if item["action"] == "auto" and item["family"] not in {i["family"] for i in items if i["repo"] in wanted}:
            wanted.append(item["repo"])
    return wanted[:MAX_SAMPLES]


def report(items: list[dict], samples: list[str], diffs: dict[str, str]) -> str:
    """DRY-RUN.md."""
    counts = Counter(i["action"] for i in items)
    fam = Counter(i["line"] for i in items)
    fam_auto = Counter(i["line"] for i in items if i["action"] == "auto")
    lines = ["# RAPP/1 network header: wave 2 dry run", "",
             "Nothing here has been pushed. `open` acts only on the `auto` rows, after the owner approves:", "",
             f"    {COMMAND}", "",
             f"- Repos: {len(items)} (public, unarchived, non-fork kody-w repos in the RAPP family, outside wave 1; "
             "denylist hits are held back in a local-only report).",
             f"- Actions: {counts.get('auto', 0)} automatic PRs, {counts.get('manual', 0)} held for a hand-made PR, "
             f"{counts.get('skip', 0)} skipped, {counts.get('none', 0)} already current.",
             f"- READMEs: {sum(i['readme_exists'] for i in items)} exist; "
             f"{sum(1 for i in items if not i['readme_exists'] and i['action'] == 'skip')} repos have none or are "
             "empty.", "",
             "| Line (family) | Repos | Automatic PRs |", "|---|---|---|"]
    lines += [f"| {f} | {n} | {fam_auto.get(f, 0)} |" for f, n in sorted(fam.items())]
    lines += ["", "## Every repo", "", "| Repo | Line | RAPP/1 status | README | Action | Detail |",
              "|---|---|---|---|---|---|"]
    for i in sorted(items, key=lambda i: (i["line"], i["repo"].lower())):
        lines.append(f"| {i['repo']} | {i['line']} | {i['status']} | {i['readme'] or 'none'} | {i['action']} | "
                     f"{i['why'].replace('|', '/')} |")
    lines += ["", "## Sample diffs", ""]
    for repo in samples:
        lines += [f"### {repo}", "", "```diff", diffs[repo].rstrip("\n"), "```", ""]
    return "\n".join(lines)


def plan(settings: Settings, say=print) -> list[dict]:
    """The dry run: <work>/wave2/plan.json, DRY-RUN.md and samples/<repo>.diff. Pushes nothing, clones nothing."""
    out = out_dir(settings)
    items, diffs = [], {}
    for entry in family(settings):
        if entry["wave"] != 2:
            continue
        item, diff = plan_one(settings, entry)
        items.append(item)
        if diff:
            diffs[item["repo"]] = diff
    util.dump(out / "plan.json", {"generated_from": GENERATED_FROM, "repos": items})
    samples = pick_samples(items)
    (out / "samples").mkdir(parents=True, exist_ok=True)
    for repo in samples:
        util.write_text(out / "samples" / f"{repo}.diff", diffs[repo])
    util.write_text(out / "DRY-RUN.md", report(items, samples, diffs))
    say(f"wave 2: {len(items)} repos; actions: {dict(Counter(i['action'] for i in items))}")
    say(f"by line: {dict(sorted(Counter(i['line'] for i in items).items()))}")
    say(f"wrote {out / 'DRY-RUN.md'}, {out / 'plan.json'} and {len(samples)} sample diffs")
    return items


def gh_with_backoff(gh, args, *, attempts: int = 6, sleep=time.sleep, say=print):
    """gh with retries on GitHub's rate limits (secondary included): 60 s, doubling, at most 900 s a wait. Any
    other failure returns at once."""
    done = None
    for attempt in range(attempts):
        done = prs.gh_run(gh, *args)
        if done.returncode == 0 or not RATE_LIMITED.search(done.stderr or ""):
            return done
        if attempt + 1 < attempts:
            wait = min(60 * 2 ** attempt, 900)
            say(f"  rate limited; waiting {wait} s (attempt {attempt + 1}/{attempts})")
            sleep(wait)
    return done


def crawl_rules():
    """(readme_facts, tracked): the crawler's own README facts, checked again on the fresh clone."""
    from .crawl import readme_facts, tracked
    return readme_facts, tracked


def _open_one(settings, item, clone, deny, gh, *, remote, rehearse, rules, sleep, say) -> str:
    repo = item["repo"]
    done = util.run(*prs.GIT, "clone", "-q", "--depth", "1", f"{remote}{repo}.git", str(clone),
                    env={"GIT_LFS_SKIP_SMUDGE": "1"})
    if done.returncode:
        return f"failed (git clone: {done.stderr.strip()[-200:]})"
    readme_facts, tracked = rules
    facts = readme_facts(clone, tracked(clone), repo)
    if facts.get("readme") != item["readme"]:
        return f"skipped: the README is now {facts.get('readme') or 'gone'!r}, not {item['readme']!r}; re-plan"
    fresh = decide(item, {**facts, "evidence_commit": prs.git(clone, "rev-parse", "HEAD")})
    if fresh["action"] != "auto":
        return f"skipped: now {fresh['action']}: {fresh['why']}"
    base = prs.git(clone, "rev-parse", "--abbrev-ref", "HEAD")
    if base == BRANCH:
        return f"skipped: the default branch is {BRANCH}"
    prs.git(clone, "checkout", "-q", "-b", BRANCH)
    try:
        action = headers.apply_header_file(clone / item["readme"], repo)
    except ValueError as error:
        return f"skipped: manual: {error}"
    if action == "unchanged":
        return "already current"
    prs.git(clone, "add", "--", item["readme"])
    prs.commit(clone, prs.message(repo))
    scan = deny.diff(clone, f"origin/{base}")
    if not scan.ok:
        return "privacy scan found something; not pushed"
    if rehearse:
        stat = prs.git(clone, "show", "--stat", "--format=%an <%ae>%n%s%n%(trailers:only)", "HEAD")
        return (f"rehearsed ({action}; {scan.line('diff')}); would push {BRANCH} and open a PR against {base}\n    "
                + stat.replace("\n", "\n    "))
    if prs.git(clone, "ls-remote", "--heads", "origin", BRANCH):
        return f"skipped: {BRANCH} already exists on the remote; finish it with the wave-1 helper"
    prs.git(clone, "push", "-q", "origin", f"HEAD:refs/heads/{BRANCH}")
    made = gh_with_backoff(gh, ["pr", "create", "-R", f"{OWNER}/{repo}", "--base", base, "--head", BRANCH,
                                "--title", TITLE, "--body", prs.body(repo)], sleep=sleep, say=say)
    if made.returncode:
        return f"failed (gh pr create: {made.stderr.strip()[-300:]})"
    url = made.stdout.strip().splitlines()[-1]
    recs = prs.records(settings)
    recs[repo] = {"url": url, "number": int(url.rstrip("/").rsplit("/", 1)[1]), "state": "OPEN", "branch": BRANCH,
                  "base": base, "head": prs.git(clone, "rev-parse", "HEAD"), "wave": 2}
    prs.save(settings, recs)
    return url


def open_prs(settings: Settings, args, deny: Denylist | None, gh=prs.GH, *, remote: str = REPO_URL,
             sleep=time.sleep, clock=time.monotonic, rules=None, say=print) -> dict[str, str]:
    """Open the plan's automatic PRs (see the module docstring); {repo: outcome} for each one tried.
    Refuses without --owner-approved (or --rehearse), and --owner-approved refuses without the private scanner."""
    args = list(args)
    rehearse = "--rehearse" in args  # everything up to the push, then stop: nothing leaves this machine
    if "--owner-approved" not in args and not rehearse:
        raise SystemExit(APPROVAL)
    if not rehearse:
        prs.need_scanner(deny, "wave 2")
    deny = deny if deny is not None else Denylist(None, warn=say)
    plan_data = util.load(out_dir(settings) / "plan.json")
    if not plan_data:
        raise SystemExit("run plan first")
    only = {n for n in util.arg(args, "--only", "").split(",") if n}
    try:
        limit, pace = int(util.arg(args, "--limit", "0")), float(util.arg(args, "--pace", "5"))
    except ValueError:
        raise SystemExit("--limit takes a whole number and --pace a number of seconds") from None
    recorded = prs.records(settings)
    queue = [i for i in plan_data["repos"] if i["action"] == "auto" and (not only or i["repo"] in only)
             and i["repo"] not in recorded]
    if limit:
        queue = queue[:limit]
    rules = rules or crawl_rules()
    clones = out_dir(settings) / "clones"
    clones.mkdir(parents=True, exist_ok=True)
    say(f"{'rehearsing' if rehearse else 'opening'} {len(queue)} PR(s), one about every {pace:g} s")
    outcomes = {}
    for n, item in enumerate(queue, 1):
        repo, started = prs.check_name(item["repo"]), clock()
        clone = clones / repo
        try:
            util.remove_tree(clone)
            outcomes[repo] = _open_one(settings, item, clone, deny, gh, remote=remote, rehearse=rehearse,
                                       rules=rules, sleep=sleep, say=say)
        except (SystemExit, OSError, UnicodeDecodeError, RuntimeError) as error:
            outcomes[repo] = f"failed ({str(error)[:200]})"
        finally:
            util.remove_tree(clone)
        say(f"[{n}/{len(queue)}] {repo}: {outcomes[repo]}")
        if n < len(queue):
            sleep(max(0.0, pace - (clock() - started)))
    say("done; next: `prs ci` for the PRs' checks; the next crawl shows them in the portfolio")
    return outcomes
`````
{% endraw %}
