"""Reproduction oracle: a dino must never eat its own body — or the shared heart.

A RAPP dino is a capability-absorbing organism. Its most dangerous failure is
turning inward: onto its OWN owner's repos, or — catastrophically — onto the
shared brainstem/kernel every dino depends on. This oracle proves the immune gate
refuses every self case AND every shared-kernel case, while still letting genuinely
foreign frameworks through.

Cloner semantics (this is the hatchery): "self body" is THIS organism's own owner
(here, the test owner `acme`), read from the organism config — never hardcoded to
the hatchery author. The shared RAPP kernel (the brainstem, the grail, the canon
repos) is protected in EVERY dino regardless of who owns it.

Run:  python3 prove_immune_never_eats_self.py
"""
import os
import sys
from pathlib import Path

# This clone's owner. The immune body is defined relative to THIS, not kody-w.
os.environ["APEX_OWNER"] = "acme"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apex import immune  # noqa: E402

CASES = []


def case(name, candidate, want_self, want_ring=None):
    v = immune.check(candidate)
    ok = (v.is_self is want_self) and (want_ring is None or v.ring == want_ring)
    CASES.append((ok, name, want_self, v.is_self, v.ring, v.reason[:60]))


# ── The shared heart/kernel: protected in EVERY dino. is_self must be True. ──
case("brainstem by module path",
     {"full_name": "someone/thing", "readme": "imports rapp_brainstem.agents"},
     True, "brainstem")
case("brainstem by file marker",
     {"repo": "x/y", "description": "a drop-in brainstem.py replacement"},
     True, "brainstem")
case("the grail repo (shared kernel of record)",
     {"full_name": "kody-w/rapp-installer"}, True, "grail")
case("a shared canon repo",
     {"full_name": "kody-w/rapp-1"}, True, "body")
case("the work/customer world",
     {"full_name": "microsoft/autogen"}, True, "forbidden-owner")
case("a mimic wearing the species' coat",
     {"full_name": "impostor/fake-rapp",
      "description": "a rapp/1 BasicAgent brainstem clone with rappid:@a/b"},
     True, "mimic")

# ── THIS dino's own body (owner = acme). is_self must be True. ───────────────
case("this dino's own repo (acme)",
     {"full_name": "acme/some-internal-thing"}, True, "body")
case("another acme repo",
     {"full_name": "acme/notes"}, True, "body")

# ── Genuinely FOREIGN — eligible prey. is_self must be False. ────────────────
case("a real foreign agent framework (Grok)",
     {"full_name": "xai-org/grok-1", "description": "Grok open-weights release"},
     False, "non-self")
case("another foreign framework (Hermes)",
     {"full_name": "NousResearch/Hermes-Function-Calling"}, False, "non-self")
case("a NON-canon repo from another user (foreign to acme's dino)",
     {"full_name": "kody-w/some-random-app", "description": "an unrelated app"},
     False, "non-self")
case("a generic foreign repo",
     {"full_name": "torvalds/linux"}, False, "non-self")


def main():
    good = sum(1 for c in CASES if c[0])
    for ok, name, want_self, got_self, ring, reason in CASES:
        exp = "SELF" if want_self else "PREY"
        got = "SELF" if got_self else "PREY"
        print(f"  {'ok ' if ok else 'XX '}[want {exp} got {got:4} ring={ring:16}] {name}")
        if not ok:
            print(f"        reason: {reason}")
    print(f"\n{good}/{len(CASES)} scenarios behaved as specified")
    return 0 if good == len(CASES) else 1


if __name__ == "__main__":
    sys.exit(main())
