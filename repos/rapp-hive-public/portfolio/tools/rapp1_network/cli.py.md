# `rapp1_network/cli.py`

The command line: `python -m rapp1_network <command>` (or `rapp1-network <command>`).

Source: `rapp1_network/cli.py` (rapp1-network 0.1.6). SHA-256 of the source below: `be9e096eafd76ded2818bcdf128ee3c469413a0d840f9a18e7591afefa465aa7` (13377 bytes). Every pulse this release cuts records it in `payload.generator` as `rapp1_network/cli.py`. Copy it out with the extractor in [../README.md](../README.md); code in a Hive is data, never run from the Hive.

{% raw %}
`````python
"""The command line: `python -m rapp1_network <command>` (or `rapp1-network <command>`).

    crawl [--no-wait]           the one rerun: discover, the full crawl, cut, publish, the Pages check, status
    discover                    the RAPP family from gh (data/family.json; held-back repos stay in local/)
    sweep [--wave 1|2|all] [--repos a,b] [--workers 6]   crawl the family (or part of it) with rapp_check.py
    cut [--dry-run]             build the next version from the current records into the Hive room and save it;
                                --dry-run builds it in a scratch copy under <work>/scratch/ and never saves
    publish [--no-wait]         the Hive's publish, check-public, the privacy scans, the push (also a retry), and
                                the Pages check of every URL (unless --no-wait)
    status                      totals per wave and per line, and the head of the pulse chain
    verify [folder]             every pulse from genesis and every version's files (default: the Hive's chain)
    header <README> <repo> [--check]   add or refresh the network header in one README
    prs start <repo> | prs finish <repo> [--note TEXT] | prs ci [repo...]   the wave-1 header PRs
    wave2 plan | wave2 open [--owner-approved | --rehearse] [--limit N] [--only a,b] [--pace S]
    subway <folder> [--pdf | --check]  draw (or check) the stable maps of a portfolio folder
    export-tools <out>          write the release copy (tools/ of the portfolio room) into <out>
    notice <repo> --lifecycle deprecated|superseded --since YYYY-MM-DD --notice TEXT [--superseded-by REPO]
           [--dry-run]          save a repo's notice in the Hive (shared/organism/notices/<repo>.md, signed save);
                                --dry-run prints the file and changes nothing
    notice <repo> --clear [--dry-run]   take a repo's notice away (signed save)
    notice check                check every notice file the Hive holds, writing nothing

Settings, each from its flag, then its environment variable, then <work>/local/settings.json:
    --work DIR (RAPP1_WORK, default: this folder)   --hives DIR (RAPP_HIVES, default ~/Hives)
    --hive NAME (RAPP1_HIVE, default rapp-hive)     --hive-agent PATH (RAPP_HIVE_AGENT)
    --checker PATH (RAPP1_CHECKER, default <work>/checker/rapp-1)   --denylist PATH (RAPP1_DENYLIST)
    --lts-pins PATH (RAPP1_LTS_PINS: the estate's LTS pins; without it, the known pins)

Exit codes: 0 done, 1 refused or failed (the reason is printed), 2 usage.
"""
from __future__ import annotations

import sys
from pathlib import Path

from . import config, util
from .wrapping import Refused

COMMANDS = ("crawl", "discover", "sweep", "cut", "publish", "status", "verify", "header", "prs", "wave2", "subway",
            "export-tools", "notice")
NOTICE_USAGE = ("notice <repo> --lifecycle deprecated|superseded --since YYYY-MM-DD --notice TEXT [--superseded-by REPO] "
                "[--dry-run] | notice <repo> --clear [--dry-run] | notice check")
NOTICE_OPTIONS = ("--lifecycle", "--since", "--notice", "--superseded-by")


WAIT_OPTIONS = ("fetch", "sleep", "clock", "timeout", "retries")


class Usage(Exception):
    """A command line that names no command, or a command without what it needs."""


def _need(rest, n, what):
    if len(rest) < n:
        raise Usage(what)


def run_command(command: str, rest: list[str], settings: config.Settings, *, gh=("gh",), say=print, **inject) -> int:
    from . import checker, crawl, export, headers, inventory, pipeline, prs, pulses, subway, wave2
    from .privacy import Denylist

    def deny():
        return Denylist(settings.denylist, warn=lambda text: say(text))

    if command == "crawl":
        unknown = [a for a in rest if a != "--no-wait"]
        if unknown:
            raise Usage(f"crawl takes only --no-wait, not {' '.join(unknown)} (sweep takes --wave and --repos)")
        pipeline.crawl(settings, rest, deny=deny(), gh=gh, say=say, **inject)
    elif command == "discover":
        inventory.discover(settings, deny(), gh=gh, say=say)
    elif command == "sweep":
        crawl.sweep(settings, **crawl.sweep_args(rest), say=say, gh=gh, **inject)
    elif command == "cut":
        unknown = [a for a in rest if a != "--dry-run"]
        if unknown:
            raise Usage(f"cut takes only --dry-run, not {' '.join(unknown)}")
        pipeline.cut(settings, deny=deny(), dry_run="--dry-run" in rest, say=say, **inject)
    elif command == "publish":
        unknown = [a for a in rest if a != "--no-wait"]
        if unknown:
            raise Usage(f"publish takes only --no-wait, not {' '.join(unknown)}")
        commit = pipeline.publish(settings, deny=deny(), say=say)
        if "--no-wait" not in rest:
            pipeline.wait_for_pages(settings, None, commit, gh=gh, say=say,
                                    **{k: v for k, v in inject.items() if k in WAIT_OPTIONS})
    elif command == "status":
        pipeline.status(settings, say=say)
    elif command == "verify":
        folder = Path(rest[0]).expanduser() if rest else None
        checker.ensure_checker(settings.checker)
        if folder is None:  # the Hive's own chain, against this device's verified head
            home = pulses.chain_home(settings)
            if home is None:
                raise SystemExit(f"no pulse chain in {settings.portfolio_dir} or {settings.private_chain_dir}")
            return pulses.verify(home, settings.checker, say=say, maps=settings.portfolio_dir,
                                 known_head=pulses.known_head(settings))
        return pulses.verify(folder, settings.checker, say=say)
    elif command == "header":
        if len([a for a in rest if a != "--check"]) != 2:
            raise Usage("header <README> <repo> [--check]")
        return headers.header_cli(rest, say=say)
    elif command == "prs":
        _need(rest, 1, "prs start <repo> | prs finish <repo> [--note TEXT] | prs ci [repo...]")
        action, args = rest[0], rest[1:]
        if action in ("start", "finish"):
            _need(args, 1, f"prs {action} <repo>")
            if action == "start":
                prs.start(settings, args[0], deny(), gh, say=say)
            else:
                prs.finish(settings, args[0], deny(), gh, note=util.arg(args, "--note", ""), say=say)
        elif action == "ci":
            prs.ci(settings, [a for a in args if not a.startswith("--")], deny(), gh, say=say)
        else:
            raise Usage(f"prs {action}: use start, finish or ci")
    elif command == "wave2":
        _need(rest, 1, "wave2 plan | wave2 open [--owner-approved | --rehearse] [--limit N] [--only a,b] [--pace S]")
        if rest[0] == "plan":
            wave2.plan(settings, say=say)
        elif rest[0] == "open":
            wave2.open_prs(settings, rest[1:], deny() if settings.denylist else None, gh, say=say)
        else:
            raise Usage(f"wave2 {rest[0]}: use plan or open")
    elif command == "subway":
        _need(rest, 1, "subway <portfolio folder> [--pdf | --check]")
        return subway.main(rest)
    elif command == "export-tools":
        _need(rest, 1, "export-tools <out folder>")
        out = Path(rest[0]).expanduser()
        files = export.tool_files(release=export.provenance())
        for rel_path, text in files.items():
            util.write_text(out.joinpath(*rel_path.split("/")[1:]), text)
        say(f"release copy: {len(files)} file(s) in {out}")
    elif command == "notice":
        return notice(settings, rest, deny=deny, say=say, **{k: v for k, v in inject.items() if k in ("hive",)})
    else:
        raise Usage(f"unknown command {command!r}")
    return 0


def _notice_args(args: list[str]) -> dict:
    """{option: value} of `notice <repo> ...`; flags --clear and --dry-run as True."""
    out, i = {}, 0
    while i < len(args):
        arg = args[i]
        name, eq, value = arg.partition("=")
        if name in ("--clear", "--dry-run") and not eq:
            out[name] = True
        elif name in NOTICE_OPTIONS:
            if not eq:
                if i + 1 >= len(args):
                    raise Usage(f"{name} needs a value")
                value, i = args[i + 1], i + 1
            out[name] = value
        else:
            raise Usage(f"notice: unknown option {arg!r}\n{NOTICE_USAGE}")
        i += 1
    return out


def notice(settings: config.Settings, rest: list[str], *, deny, say=print, hive=None) -> int:
    """`notice <repo> ...` and `notice check`: validate a notice (the rules a cut reads it with), write it into the
    Hive's work tree through the Hive client, scan it, and ask the Hive for its signed save; `--dry-run` prints the
    file and changes nothing; `--clear` removes the file (a signed save too); `check` checks every committed one."""
    from . import lifecycle, pipeline
    from .hive import Hive
    from .privacy import require
    if not rest:
        raise Usage(NOTICE_USAGE)
    hive = hive or Hive(settings, say=say)
    names = pipeline.notice_names(settings)
    if rest[0] == "check":
        if len(rest) > 1:
            raise Usage("notice check takes nothing else")
        found = pipeline.read_notices(hive, names)
        say(f"notices: {len(found)} file(s) in {lifecycle.NOTICES}/, every one valid"
            + "".join(f"\n  {n}: {v['lifecycle']} since {v['since']}" for n, v in sorted(found.items())))
        unsaved = sorted(p for p in hive.edits() if p.startswith(lifecycle.NOTICES + "/"))
        if unsaved:
            say(f"unsaved edits, not read by a cut until they are saved: {', '.join(unsaved)}")
        return 0
    repo, opts = rest[0], _notice_args(rest[1:])
    path = lifecycle.notice_path(repo)
    committed = hive.committed_texts(lifecycle.NOTICES + "/").get(path)
    if opts.get("--clear"):
        if set(opts) - {"--clear", "--dry-run"}:
            raise Usage("notice <repo> --clear takes only --dry-run")
        if committed is None:
            raise SystemExit(f"{path}: there is no saved notice for {repo}")
        text = None
    else:
        missing = [o for o in ("--lifecycle", "--since", "--notice") if o not in opts]
        if missing:
            raise Usage(f"notice {repo} needs {', '.join(missing)}\n{NOTICE_USAGE}")
        life = opts["--lifecycle"]
        if life not in lifecycle.NOTICED:
            raise Usage(f"--lifecycle is {' or '.join(lifecycle.NOTICED)} (archived comes only from GitHub)")
        if (life == "superseded") != ("--superseded-by" in opts):
            raise Usage("--superseded-by names the successor of a superseded repo, and only of one")
        text = lifecycle.notice_file(repo, life, opts["--since"], opts["--notice"], opts.get("--superseded-by"))
        lifecycle.parse_notice(path, text, names)  # the cut's own rules (Refused names the file and the rule)
    if opts.get("--dry-run"):
        say(f"would remove {path}" if text is None else f"{path}:\n{text}")
        say("dry run: nothing was written or saved")
        return 0
    if text is not None and committed == text:
        say(f"{path}: this notice is saved already; nothing to do")
        return 0
    with pipeline.CrawlLock(settings):
        if hive.edits():
            raise SystemExit("the Hive has unsaved edits; save or put them back before a notice")
        try:
            hive.put(path, text)
            if text is not None:
                require(deny().tree(hive.path.joinpath(*lifecycle.NOTICES.split("/"))), "tree", "nothing was saved",
                        say=say)
            saved = hive.signed_save()
            if saved is None:
                raise SystemExit("the Hive saved nothing")
        except BaseException:
            hive.restore()
            raise
    say(f"{'removed' if text is None else 'saved'} {path} in Hive commit {saved}; the next crawl shows it on the "
        "badge, the portfolio, the map, the notices page and the pulse")
    return 0


def main(argv=None, *, gh=("gh",), say=print, err=None, **inject) -> int:
    """`python -m rapp1_network <command> [options]`; the exit code (0 done, 1 refused or failed, 2 usage).
    Progress goes to `say`, refusals and usage to `err` (default: standard error when `say` is print)."""
    argv = list(sys.argv[1:] if argv is None else argv)
    err = err or ((lambda text: print(text, file=sys.stderr, flush=True)) if say is print else say)
    try:
        flags, rest = config.split_flags(argv)
    except SystemExit as error:
        err(f"usage: {error}")
        return 2
    if not rest or rest[0] in ("-h", "--help", "help"):
        say(__doc__.strip())
        return 0 if rest else 2
    command, rest = rest[0], rest[1:]
    if command not in COMMANDS:
        err(f"unknown command {command!r}\n\n{__doc__.strip()}")
        return 2
    settings = config.resolve(flags)
    try:
        return int(run_command(command, rest, settings, gh=gh, say=say, **inject) or 0)
    except Usage as error:
        err(f"usage: {error}")
        return 2
    except Refused as error:
        err(f"refused: {error}")
        return 1
    except SystemExit as error:
        if error.code in (None, 0):
            return 0
        if isinstance(error.code, int):
            return 1
        err(str(error.code))
        return 1
    except KeyboardInterrupt:
        err("interrupted")
        return 1


if __name__ == "__main__":
    sys.exit(main())
`````
{% endraw %}
