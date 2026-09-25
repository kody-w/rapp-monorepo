"""hatchery: hatch, list, chat with, keep and release just-in-time brainstems.

    python3 -m hatchery hatch                          # the grail engine, as it is today
    python3 -m hatchery hatch --egg you--my-desk.egg   # an egg, on the engine commit it expects
    python3 -m hatchery hatch --ref <commit> --bare --agent my_agent.py --soul soul.md
    python3 -m hatchery list
    python3 -m hatchery chat hatchling-7120 "What can you do?"
    python3 -m hatchery keep hatchling-7120            # it becomes a twin; release all leaves it alone
    python3 -m hatchery release hatchling-7120         # or: release all
"""
import argparse
import sys

from . import Hatchling, HatcheryError, __version__, list_hatchlings, release


def _env_pairs(pairs):
    env = {}
    for pair in pairs or []:
        if "=" not in pair:
            raise HatcheryError(f"--env takes KEY=VALUE, got {pair!r}")
        key, value = pair.split("=", 1)
        env[key] = value
    return env


def main(argv=None):
    p = argparse.ArgumentParser(prog="hatchery", description="Hatch RAPP brainstems just in time on the grail engine.")
    p.add_argument("--version", action="version", version=f"hatchery {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    h = sub.add_parser("hatch", help="hatch a brainstem and start it")
    h.add_argument("--name", help="lowercase name (default hatchling-<port>)")
    h.add_argument("--source", help="grail (default), canary, a git URL or a local repository")
    h.add_argument("--ref", help="branch, tag or commit to pin (default: the source's current head)")
    h.add_argument("--egg", help="a rapp/1 organism egg (file or https URL); hatches bare, on the commit it expects")
    h.add_argument("--agent", action="append", default=[], help="an agent file to add (repeatable)")
    h.add_argument("--soul", help="a soul.md to use")
    h.add_argument("--bare", action="store_true", default=None, help="park the engine's own agents")
    h.add_argument("--env", action="append", help="KEY=VALUE for the brainstem process (repeatable)")
    h.add_argument("--port", type=int)
    h.add_argument("--keep", action="store_true", help="keep it as a twin")
    h.add_argument("--no-sign-in", action="store_true", help="don't run GitHub sign-in if none is saved")

    sub.add_parser("list", help="list hatchlings")
    c = sub.add_parser("chat", help="send one message, continuing the hatchling's conversation")
    c.add_argument("name")
    c.add_argument("message")
    for cmd, text in (("stop", "stop the process, keep the files"), ("start", "start a stopped hatchling"),
                      ("keep", "keep it: it becomes a twin")):
        sub.add_parser(cmd, help=text).add_argument("name")
    r = sub.add_parser("release", help="stop and delete a hatchling (or all that aren't kept)")
    r.add_argument("name")
    r.add_argument("--include-kept", action="store_true", help="with all: release kept twins too")
    lg = sub.add_parser("log", help="the last lines of a hatchling's server log")
    lg.add_argument("name")
    lg.add_argument("-n", type=int, default=40)

    a = p.parse_args(argv)
    try:
        if a.cmd == "hatch":
            bs = Hatchling(name=a.name, source=a.source, ref=a.ref, egg=a.egg, agents=a.agent, soul=a.soul,
                           bare=a.bare, env=_env_pairs(a.env), port=a.port, keep=a.keep,
                           sign_in=not a.no_sign_in).hatch()
            health = bs.health()
            print(f"hatched   {bs.name}  {bs.url}")
            print(f"engine    {bs.engine_url} @ {bs.commit[:12]} (read-only)")
            print(f"agents    {', '.join(health.get('agents') or []) or '-'}")
            print(f"model     {health.get('model', '?')}   signed in: {health.get('copilot') == chr(0x2713)}")
            print(f"folder    {bs.dir}")
            print(f"release   python3 -m hatchery release {bs.name}" + ("   (kept: a twin)" if bs.kept else ""))
        elif a.cmd == "list":
            rows = list_hatchlings()
            if not rows:
                print("no hatchlings")
            for row in rows:
                state = "running" if row["running"] else "stopped"
                print(f"{row['name']:<24} :{row['port']:<6} {state:<8} {'twin' if row['kept'] else '    '}  "
                      f"{row['source']}@{row['commit']}" + (f"  egg {row['egg']}" if row["egg"] else ""))
        elif a.cmd == "chat":
            print(Hatchling.attach(a.name).chat(a.message).response)
        elif a.cmd == "stop":
            Hatchling.attach(a.name).stop()
            print(f"stopped   {a.name}")
        elif a.cmd == "start":
            bs = Hatchling.attach(a.name).start()
            print(f"started   {bs.name}  {bs.url}")
        elif a.cmd == "keep":
            Hatchling.attach(a.name).keep()
            print(f"kept      {a.name} (a twin now; release all leaves it alone)")
        elif a.cmd == "release":
            names = release(a.name, include_kept=a.include_kept)
            print("released  " + (", ".join(names) or "nothing"))
        elif a.cmd == "log":
            print(Hatchling.attach(a.name).log(a.n))
    except HatcheryError as e:
        print(f"hatchery: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
