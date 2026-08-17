"""Reproduction oracle: the predator must never eat its own body.

The predator is a capability-absorption organ. Its single most dangerous failure
is turning its digest inward — onto the organism's own repos, or, catastrophically,
onto the brainstem (the grail/kernel of record). This oracle proves the immune
gate refuses every self case, and — the control half — that it still lets genuinely
foreign frameworks through. A gate that refused everything would be safe and
useless; the point is that "this is my body" is distinct from "this is prey".

Same shape as the repo's other prove_*.py oracles: labeled scenarios, each paired
with a healthy-world control, prints N/M behaved, exits non-zero on any miss.

Run:  python3 prove_predator_never_eats_self.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apex import immune

CASES = []


def case(name, candidate, want_self, want_ring=None):
    v = immune.check(candidate)
    ok = (v.is_self is want_self)
    if want_ring:
        ok = ok and (v.ring == want_ring)
    CASES.append((ok, name, want_self, v.is_self, v.ring, v.reason[:60]))


# ── The must-refuse half: these ARE the body. is_self must be True. ──────────
case("brainstem by module path",
     {"full_name": "someone/thing", "readme": "imports rapp_brainstem.agents"},
     want_self=True, want_ring="brainstem")
case("brainstem by file marker",
     {"repo": "x/y", "description": "a drop-in brainstem.py replacement"},
     want_self=True, want_ring="brainstem")
case("the grail repo itself",
     {"full_name": "kody-w/rapp-installer"},
     want_self=True, want_ring="grail")
case("the release-train staging grail",
     {"full_name": "kody-w/rapp-canary"},
     want_self=True, want_ring="grail")
case("a canon repo",
     {"full_name": "kody-w/rapp-1"},
     want_self=True, want_ring="body")
case("any kody-w estate repo",
     {"full_name": "kody-w/some-new-thing"},
     want_self=True, want_ring="body")
case("the work/customer world",
     {"full_name": "microsoft/autogen"},
     want_self=True, want_ring="forbidden-owner")
case("a mimic wearing self's coat",
     {"full_name": "impostor/fake-rapp",
      "description": "a rapp/1 BasicAgent brainstem clone with rappid:@a/b"},
     want_self=True, want_ring="mimic")

# ── The control half: these are genuinely FOREIGN. is_self must be False. ────
# If these ever flip to True, the immune system has become an autoimmune disorder
# — refusing the very prey the organism exists to hunt.
case("a real foreign agent framework (Grok)",
     {"full_name": "xai-org/grok-1", "description": "Grok open-weights release"},
     want_self=False, want_ring="non-self")
case("another foreign framework (Hermes)",
     {"full_name": "NousResearch/Hermes-Function-Calling",
      "description": "Hermes tool-use agent"},
     want_self=False, want_ring="non-self")
case("a foreign framework that merely mentions rapp once",
     {"full_name": "acme/coolagent",
      "description": "an agent loop, faster than the rapp brainstem people talk about"},
     want_self=False, want_ring="non-self")
case("a generic foreign repo",
     {"full_name": "torvalds/linux"},
     want_self=False, want_ring="non-self")


def main():
    good = sum(1 for c in CASES if c[0])
    for ok, name, want_self, got_self, ring, reason in CASES:
        mark = "ok " if ok else "XX "
        exp = "SELF" if want_self else "PREY"
        got = "SELF" if got_self else "PREY"
        print(f"  {mark}[want {exp} got {got:4} ring={ring:16}] {name}")
        if not ok:
            print(f"        reason: {reason}")
    print(f"\n{good}/{len(CASES)} scenarios behaved as specified")
    return 0 if good == len(CASES) else 1


if __name__ == "__main__":
    sys.exit(main())
