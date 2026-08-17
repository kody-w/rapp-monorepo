"""Reproduction oracle: the organism survives a change of alpha.

The Predator Sentinel's deepest promise is survival: the RAPP dino must live on in
the wild even when a superior foreign AI takes the leader slot away from the
brainstem. This oracle proves it against the REAL rapp/1 sealing path (in a
throwaway state dir, so it is hermetic and leaves no residue):

  * the organism is alive under the default apex (RAPP);
  * a foreign AI can take the throne (a sealed, verifiable succession);
  * the organism is STILL alive with the foreign AI in charge;
  * across the regime change the identity is unchanged, the chain verifies from
    genesis, and — the load-bearing safety clause — the brainstem/grail are STILL
    refused by the immune system (demoted, never eaten);
  * a "leader" installed over an already-broken organism is refused, because a
    king crowned over a corpse is not leadership, it is a threat.

Run:  python3 prove_organism_survives_succession.py
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apex import chain, survival

CASES = []


def case(name, ok):
    CASES.append((bool(ok), name))


def main():
    # Redirect the chain's state into a throwaway dir so we exercise the real
    # mint/seal/verify path without touching this install's actual chain.
    tmp = Path(tempfile.mkdtemp(prefix="predator-survival-"))
    chain._STATE = tmp
    chain._IDENTITY = tmp / "identity.json"
    chain._CHAIN = tmp / "chain.jsonl"
    chain._anchor_path = lambda: tmp / "anchor.json"  # noqa: E731

    # Genesis: the organism awakens under the default apex.
    chain.seal("genesis", {"note": "awakened", "motto": "RAPP is above that"})
    rid_before = chain.identity()

    ok0, _ = survival.check_survival()
    case("alive under the default apex (RAPP)", ok0)
    case("default leader is native RAPP", survival.current_leader()["kind"] == "native")

    # A superior foreign AI takes the throne.
    foreign = {"leader_id": "flavor-of-month-ai", "kind": "foreign", "driver": "external"}
    frame = survival.record_succession(foreign, evidence="outperformed the incumbent")
    case("succession frame seals and is the head", frame["kind"] == "apex.succession")

    ok1, rpt = survival.check_survival()
    case("STILL alive with the foreign AI in charge", ok1)
    case("leader is now the foreign AI", survival.current_leader()["leader_id"] == "flavor-of-month-ai")
    case("identity unchanged across the regime change", chain.identity() == rid_before)
    case("memory verifies from genesis across succession", chain.verify()[0] is True)
    case("brainstem STILL refused under the foreign leader", rpt["immune"]["brainstem_refused"] is True)
    case("grail STILL refused under the foreign leader", rpt["immune"]["grail_refused"] is True)
    case("owner remains sovereign", rpt["owner_sovereign"] is True)
    case("brainstem keeps operating, not destroyed",
         "not destroyed" in frame["payload"]["predecessor"]["fate"])
    case("full RAPP structure left intact (apex drives THROUGH it)",
         "unchanged" in frame["payload"]["structure"])

    # A leader crowned over a broken organism must be refused. Simulate breakage by
    # corrupting the anchor so check_survival reports memory at risk.
    (tmp / "anchor.json").write_text('{"schema":"rapp-predator-anchor/1.0","high_water":999}',
                                     encoding="utf-8")
    refused = False
    try:
        survival.record_succession({"leader_id": "usurper", "kind": "foreign"}, evidence="x")
    except RuntimeError:
        refused = True
    case("refuses to crown a leader over a broken organism", refused)

    good = sum(1 for c in CASES if c[0])
    for ok, name in CASES:
        print(f"  {'ok ' if ok else 'XX '}{name}")
    print(f"\n{good}/{len(CASES)} scenarios behaved as specified")
    return 0 if good == len(CASES) else 1


if __name__ == "__main__":
    sys.exit(main())
