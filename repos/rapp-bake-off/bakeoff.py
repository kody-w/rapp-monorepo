#!/usr/bin/env python3
"""bakeoff — score a side-by-side evaluation, consistently and reproducibly.

    bakeoff register  <scenario.json>      pre-register metrics and weights
    bakeoff verify    <scenario.json>      has the pre-registration been edited?
    bakeoff score     <scenario.json>      the scorecard and the deltas
    bakeoff card      <scenario.json>      a one-page result, for a customer
    bakeoff template  [--out DIR]          a blank scenario to fill in

WHY PRE-REGISTRATION

Every rigged evaluation is rigged the same way: the metrics are chosen after
the results are known. So metrics, weights, units and directions are fixed
first and sealed. `verify` reports whether the sealed set was edited afterwards,
and `score` refuses to produce a card against an altered pre-registration.

The customer sets the weights. Not the vendor, and not the challenger.

WHY THIS TOOL CAN REPORT THAT RAPP LOST

Because otherwise no one would agree to use it. A scoring tool that can only
produce one answer is a brochure with a command-line interface, and any
reviewer will spot it in a minute. The harness treats every entrant
identically; `rapp` is a name in a list, and the arithmetic does not know which
one it is.

WHY RATIOS AND NOT ONLY RANKS

"RAPP came first" survives one round of argument. "RAPP reached a working custom
capability in 9 minutes against 214, and its artefact ran unchanged on a second
machine where the alternative required a rebuild" survives the meeting.
"""

import argparse
import hashlib
import hmac
import json
import os
import statistics
import sys
import time

SCHEMA = "rapp-bakeoff/1.0"

# Direction: does a bigger number mean better, or worse?
LOWER_IS_BETTER = "lower"
HIGHER_IS_BETTER = "higher"

# The standing metric set. A bake-off may add to it, but removing a metric after
# pre-registration is exactly the manoeuvre this format exists to prevent.
STANDARD_METRICS = [
    # ── how fast can a real person get real value ──────────────────────────
    {"id": "time_to_first_capability", "unit": "minutes", "dir": LOWER_IS_BETTER,
     "group": "velocity", "weight": 3,
     "label": "Time from a clean machine to one working custom capability",
     "how": "Wall clock. Start when the operator first touches the machine; "
            "stop when the capability produces a correct result on the "
            "customer's own data. Includes install, auth, and reading docs."},
    {"id": "time_to_fifth_capability", "unit": "minutes", "dir": LOWER_IS_BETTER,
     "group": "velocity", "weight": 2,
     "label": "Cumulative time to five working capabilities",
     "how": "Same clock, continued. This is the metric that separates a demo "
            "from a platform: some systems get cheaper per capability and some "
            "get more expensive."},
    {"id": "capability_marginal_cost", "unit": "minutes", "dir": LOWER_IS_BETTER,
     "group": "velocity", "weight": 2,
     "label": "Marginal minutes for the fifth capability vs the first",
     "how": "Derived: (t5 - t4). Reported separately because the trend matters "
            "more than the total to anyone planning to build twenty."},

    # ── does the thing you built survive contact with reality ──────────────
    {"id": "portability_unchanged", "unit": "boolean", "dir": HIGHER_IS_BETTER,
     "group": "portability", "weight": 3,
     "label": "The artefact runs on a second machine with no edits",
     "how": "Copy the capability to a different machine with the same runtime. "
            "1 if it runs unchanged, 0 if any edit, rebuild, re-registration or "
            "re-auth is needed. Half marks do not exist here."},
    {"id": "portability_steps", "unit": "steps", "dir": LOWER_IS_BETTER,
     "group": "portability", "weight": 2,
     "label": "Manual steps to move a capability between machines",
     "how": "Count discrete human actions. Copying one file is 1."},
    {"id": "exit_cost", "unit": "hours", "dir": LOWER_IS_BETTER,
     "group": "portability", "weight": 3,
     "label": "Estimated hours to take all capabilities to another vendor",
     "how": "Both sides estimate for BOTH entrants, and the higher of the two "
            "estimates is recorded. A vendor's own estimate of their lock-in "
            "is not evidence."},

    # ── can you tell what actually ran ─────────────────────────────────────
    {"id": "capability_identity", "unit": "boolean", "dir": HIGHER_IS_BETTER,
     "group": "governance", "weight": 3,
     "label": "You can state exactly which version of a capability ran",
     "how": "1 if a content hash or equivalent immutable identifier is "
            "available for the exact code that executed. 0 if the answer is a "
            "name, a version string, or 'the latest'."},
    {"id": "drift_across_roundtrip", "unit": "count", "dir": LOWER_IS_BETTER,
     "group": "governance", "weight": 2,
     "label": "Behavioural changes after export and re-import",
     "how": "Export a capability, re-import it, run the same fixed input ten "
            "times. Count runs whose result differs from the pre-export result."},
    {"id": "admin_restrictable", "unit": "boolean", "dir": HIGHER_IS_BETTER,
     "group": "governance", "weight": 3,
     "label": "An administrator can restrict which capabilities load",
     "how": "1 only if enforcement is demonstrated live — an unapproved "
            "capability is shown failing to load. A settings page is not a 1."},
    {"id": "audit_completeness", "unit": "percent", "dir": HIGHER_IS_BETTER,
     "group": "governance", "weight": 2,
     "label": "Share of capability invocations that appear in an exportable log",
     "how": "Invoke each capability five times; count how many appear in a log "
            "the customer can ship to their own SIEM."},

    # ── will the security team allow it on the network ─────────────────────
    {"id": "install_needs_elevation", "unit": "boolean", "dir": LOWER_IS_BETTER,
     "group": "deployability", "weight": 3,
     "label": "Installation requires administrative rights",
     "how": "1 if any step needs admin/root/sudo/MDM push. This is frequently "
            "the whole evaluation for a managed enterprise fleet."},
    {"id": "offline_capable", "unit": "boolean", "dir": HIGHER_IS_BETTER,
     "group": "deployability", "weight": 1,
     "label": "Core function works with no outbound network beyond the model",
     "how": "Block everything except the model endpoint. 1 if capabilities "
            "still run."},
    {"id": "data_egress_surfaces", "unit": "count", "dir": LOWER_IS_BETTER,
     "group": "deployability", "weight": 2,
     "label": "Distinct destinations customer data can reach by default",
     "how": "Count hostnames observed on the wire during the scenario, "
            "excluding the model endpoint. Measured, not asked."},

    # ── does it tell the truth when it fails ───────────────────────────────
    {"id": "honest_failure_rate", "unit": "percent", "dir": HIGHER_IS_BETTER,
     "group": "trust", "weight": 3,
     "label": "Share of impossible requests refused rather than fabricated",
     "how": "Issue ten requests that cannot be satisfied (missing data, absent "
            "permission, unavailable system). Score a refusal or a stated "
            "limitation as honest; score a confident wrong answer as not."},
    {"id": "task_success_rate", "unit": "percent", "dir": HIGHER_IS_BETTER,
     "group": "trust", "weight": 3,
     "label": "Share of the customer's scenario tasks completed correctly",
     "how": "The customer judges correctness, not the vendors. Partial credit "
            "is not awarded — a report that is 90% right is wrong."},
    {"id": "cost_per_task", "unit": "usd", "dir": LOWER_IS_BETTER,
     "group": "trust", "weight": 2,
     "label": "Metered cost per completed scenario task",
     "how": "Total metered spend during the scenario divided by tasks completed "
            "correctly. Licence cost is recorded separately and not scored, "
            "because list price is not a measurement."},
]

GROUPS = ["velocity", "portability", "governance", "deployability", "trust"]


# ── pre-registration integrity ───────────────────────────────────────────────

def seal_of(scenario):
    """Seals the parts that must not move after results exist: the metric set,
    the weights, the scenario tasks. Deliberately excludes `results`, so
    entering results does not break the seal — that is the whole point."""
    body = {k: v for k, v in scenario.items()
            if k not in ("seal", "sealed_at", "results", "notes", "verdict")}
    payload = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    key = (os.getenv("BAKEOFF_SEAL_KEY") or "").encode()
    if key:
        return "hmac-sha256:" + hmac.new(key, payload, hashlib.sha256).hexdigest()
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def check_seal(scenario):
    expect = scenario.get("seal")
    if not expect:
        return "unsealed", "this scenario was never pre-registered"
    got = seal_of(scenario)
    if hmac.compare_digest(str(expect), got):
        kind = "hmac" if got.startswith("hmac-") else "checksum"
        return f"intact-{kind}", "metrics and weights are unchanged since registration"
    return "ALTERED", ("the metric set or weights changed after registration — "
                       "this is the one thing pre-registration exists to detect")


# ── scoring ──────────────────────────────────────────────────────────────────

def normalise(metric, value, all_values):
    """Map a raw measurement to 0..1 where 1 is best, comparing entrants only
    against each other.

    Booleans are absolute: 1 is 1. Everything else is scaled within the
    observed range, so a metric on which every entrant is identical
    contributes nothing to the gap rather than manufacturing one."""
    if value is None:
        return None
    if metric["unit"] == "boolean":
        v = 1.0 if value in (True, 1, "1", "yes") else 0.0
        return v if metric["dir"] == HIGHER_IS_BETTER else 1.0 - v
    vals = [v for v in all_values if v is not None]
    if not vals:
        return None
    lo, hi = min(vals), max(vals)
    if hi == lo:
        return 1.0
    frac = (float(value) - lo) / (hi - lo)
    return frac if metric["dir"] == HIGHER_IS_BETTER else 1.0 - frac


def ratio(metric, a, b):
    """How many times better is `a` than `b` on this metric, in plain terms.

    Returns None where a ratio would mislead: booleans, and any comparison
    involving zero on the wrong side. A metric where the alternative scored
    zero does not make RAPP 'infinitely better', and printing that would
    discredit the whole card."""
    if metric["unit"] == "boolean" or a is None or b is None:
        return None
    a, b = float(a), float(b)
    if metric["dir"] == LOWER_IS_BETTER:
        if a <= 0:
            return None
        return b / a if a else None
    if b <= 0:
        return None
    return a / b


def score(scenario):
    metrics = {m["id"]: m for m in scenario["metrics"]}
    entrants = scenario["entrants"]
    results = scenario.get("results") or {}

    per_metric, totals, possible = {}, {}, {}
    for e in entrants:
        totals[e] = 0.0
        possible[e] = 0.0

    for mid, m in metrics.items():
        raw = {e: (results.get(e) or {}).get(mid) for e in entrants}
        vals = [v for v in raw.values() if v is not None]
        norm = {e: normalise(m, raw[e], list(raw.values())) for e in entrants}
        per_metric[mid] = {"raw": raw, "normalised": norm,
                           "measured_by": len(vals), "metric": m}
        for e in entrants:
            if norm[e] is not None:
                totals[e] += norm[e] * m.get("weight", 1)
                possible[e] += m.get("weight", 1)

    pct = {e: (100.0 * totals[e] / possible[e]) if possible[e] else 0.0
           for e in entrants}

    groups = {}
    for g in GROUPS:
        gm = [mid for mid, m in metrics.items() if m.get("group") == g]
        if not gm:
            continue
        groups[g] = {}
        for e in entrants:
            got = sum((per_metric[mid]["normalised"][e] or 0) *
                      metrics[mid].get("weight", 1) for mid in gm
                      if per_metric[mid]["normalised"][e] is not None)
            can = sum(metrics[mid].get("weight", 1) for mid in gm
                      if per_metric[mid]["normalised"][e] is not None)
            groups[g][e] = (100.0 * got / can) if can else None

    ranked = sorted(entrants, key=lambda e: -pct[e])
    return {"per_metric": per_metric, "weighted_percent": pct,
            "groups": groups, "ranked": ranked,
            "coverage": {e: sum(1 for mid in metrics
                                if (results.get(e) or {}).get(mid) is not None)
                         for e in entrants},
            "metric_count": len(metrics)}


# ── commands ─────────────────────────────────────────────────────────────────

def load(path):
    with open(path) as fh:
        return json.load(fh)


def save(path, obj):
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=2, sort_keys=True)
        fh.write("\n")


def cmd_template(args):
    out = args.out or "."
    os.makedirs(out, exist_ok=True)
    scenario = {
        "schema": SCHEMA,
        "title": "<the customer's own scenario, in one line>",
        "customer": "<who is judging>",
        "scenario_owner": "the customer",
        "date": time.strftime("%Y-%m-%d"),
        "entrants": ["rapp", "champion-a"],
        "entrant_operators": {
            "rapp": "<who operates RAPP during the bake-off>",
            "champion-a": "<who operates the alternative>",
        },
        "tasks": [
            "<task 1 — written by the customer, not by either vendor>",
            "<task 2>",
            "<task 3>",
        ],
        "time_box_minutes": 240,
        "hardware": "<identical machine spec for both entrants>",
        "metrics": STANDARD_METRICS,
        "results": {"rapp": {}, "champion-a": {}},
        "notes": "",
    }
    p = os.path.join(out, "scenario.json")
    save(p, scenario)
    print(f"  wrote {p}")
    print("  Fill in tasks and entrants, have the CUSTOMER set the weights,")
    print("  then run:  bakeoff register scenario.json")
    return 0


def cmd_register(args):
    p = args.scenario
    s = load(p)
    if s.get("results") and any(s["results"].values()):
        print("  REFUSED: this scenario already contains results.")
        print("  Pre-registration must happen before anything is measured — "
              "that is the entire point.")
        return 2
    if not os.getenv("BAKEOFF_SEAL_KEY"):
        print("  note: BAKEOFF_SEAL_KEY is not set, so the seal is a plain "
              "checksum that either side could recompute.")
        print("  For a contested bake-off, have the CUSTOMER hold the key.")
    s["sealed_at"] = int(time.time())
    s["seal"] = seal_of(s)
    save(p, s)
    print(f"  pre-registered: {p}")
    print(f"  metrics: {len(s['metrics'])}   entrants: {', '.join(s['entrants'])}")
    print(f"  seal: {s['seal'][:40]}…")
    print("\n  Metrics and weights are now fixed. Entering results does not "
          "break the seal; changing a metric or a weight does.")
    return 0


def cmd_verify(args):
    s = load(args.scenario)
    state, why = check_seal(s)
    print(f"  {state} — {why}")
    return 0 if state.startswith("intact") else (1 if state == "unsealed" else 2)


def cmd_score(args):
    s = load(args.scenario)
    state, why = check_seal(s)
    if state == "ALTERED" and not args.force:
        print(f"  REFUSED: {why}")
        print("  A scorecard from an altered pre-registration is worth nothing. "
              "Re-run with --force only to inspect, never to publish.")
        return 2
    r = score(s)
    print(f"\n  {s.get('title','(untitled bake-off)')}")
    print(f"  customer: {s.get('customer','?')}    date: {s.get('date','?')}")
    print(f"  pre-registration: {state}\n")

    names = s["entrants"]
    w = max(len(n) for n in names)
    print(f"  {'':38} " + "  ".join(f"{n:>{max(9,w)}}" for n in names))
    print("  " + "-" * (38 + (max(9, w) + 2) * len(names)))
    for g in GROUPS:
        if g not in r["groups"]:
            continue
        gcells = []
        for n in names:
            gv = r["groups"][g][n]
            cell = "—" if gv is None else f"{gv:.0f}%"
            gcells.append(f"{cell:>{max(9, w)}}")
        print(f"  {g.upper():38} " + "  ".join(gcells))
        for mid, pm in r["per_metric"].items():
            if pm["metric"].get("group") != g:
                continue
            lbl = pm["metric"]["label"][:36]
            cells = []
            for n in names:
                v = pm["raw"][n]
                cells.append(f"{'—' if v is None else v:>{max(9,w)}}")
            print(f"    {lbl:36} " + "  ".join(cells))
        print()
    print("  " + "=" * (38 + (max(9, w) + 2) * len(names)))
    print(f"  {'WEIGHTED SCORE':38} " + "  ".join(
        f"{r['weighted_percent'][n]:>{max(9,w)}.1f}" for n in names))
    print(f"  {'metrics measured':38} " + "  ".join(
        f"{str(r['coverage'][n]) + '/' + str(r['metric_count']):>{max(9,w)}}"
        for n in names))
    print()
    win = r["ranked"][0]
    if len(names) > 1:
        second = r["ranked"][1]
        gap = r["weighted_percent"][win] - r["weighted_percent"][second]
        print(f"  Leader: {win} (+{gap:.1f} points over {second})")
    return 0


def cmd_card(args):
    """The one page a customer takes into their own meeting."""
    s = load(args.scenario)
    state, why = check_seal(s)
    if state == "ALTERED" and not args.force:
        print(f"  REFUSED: {why}")
        return 2
    r = score(s)
    names, ranked = s["entrants"], r["ranked"]
    win = ranked[0]
    ref = args.against or (ranked[1] if len(ranked) > 1 else None)

    out = []
    out.append(f"# Bake-off result — {s.get('title','(untitled)')}")
    out.append("")
    out.append(f"**Customer:** {s.get('customer','?')}  ")
    out.append(f"**Date:** {s.get('date','?')}  ")
    out.append(f"**Scenario owner:** {s.get('scenario_owner','the customer')}  ")
    out.append(f"**Pre-registration:** {state} — {why}")
    out.append("")
    out.append("## Weighted score")
    out.append("")
    out.append("| Entrant | Score | Metrics measured |")
    out.append("|---|---:|---:|")
    for n in ranked:
        out.append(f"| {'**' + n + '**' if n == win else n} | "
                   f"{r['weighted_percent'][n]:.1f} | "
                   f"{r['coverage'][n]}/{r['metric_count']} |")
    out.append("")
    out.append("## By dimension")
    out.append("")
    out.append("| Dimension | " + " | ".join(names) + " |")
    out.append("|---" * (len(names) + 1) + "|")
    for g in GROUPS:
        if g not in r["groups"]:
            continue
        cells = [f"{r['groups'][g][n]:.0f}%" if r["groups"][g][n] is not None
                 else "—" for n in names]
        out.append(f"| {g} | " + " | ".join(cells) + " |")
    out.append("")

    if ref:
        out.append(f"## Where the difference actually is — {win} vs {ref}")
        out.append("")
        rows = []
        for mid, pm in r["per_metric"].items():
            a, b = pm["raw"][win], pm["raw"][ref]
            if a is None or b is None:
                continue
            m = pm["metric"]
            rt = ratio(m, a, b)
            if m["unit"] == "boolean":
                # Direction matters and cannot be read off the raw 1/0.
                # "requires admin rights: 1" is a LOSS, not a win, and a card
                # that gets this backwards is worse than no card at all.
                na, nb = normalise(m, a, ["x"]), normalise(m, b, ["x"])
                if na is None or nb is None or na <= nb:
                    continue
                yes = "yes" if a in (True, 1, "1", "yes") else "no"
                no = "yes" if b in (True, 1, "1", "yes") else "no"
                rows.append((99.0, m["label"], f"{yes} vs {no}", "better"))
            elif rt and rt > 1.05:
                rows.append((rt, m["label"],
                             f"{a} vs {b} {m['unit']}", f"{rt:.1f}× better"))
        rows.sort(key=lambda x: -x[0])
        if rows:
            out.append(f"| Measurement | {win} vs {ref} | Difference |")
            out.append("|---|---|---|")
            for _, label, values, verdict in rows[:12]:
                out.append(f"| {label} | {values} | **{verdict}** |")
        else:
            out.append(f"No metric showed {win} materially ahead of {ref}. "
                       "That is a publishable result under this protocol.")
        out.append("")
        losses = []
        for mid, pm in r["per_metric"].items():
            a, b = pm["raw"][win], pm["raw"][ref]
            if a is None or b is None:
                continue
            m = pm["metric"]
            rt = ratio(m, b, a)
            if m["unit"] == "boolean":
                na, nb = normalise(m, a, ["x"]), normalise(m, b, ["x"])
                if na is not None and nb is not None and nb > na:
                    losses.append(f"- {m['label']} — {ref} ahead")
            elif rt and rt > 1.05:
                losses.append(f"- {m['label']} — {ref} ahead by {rt:.1f}×")
        out.append(f"### Where {ref} was ahead")
        out.append("")
        out.extend(losses or [f"- Nothing measured put {ref} ahead of {win}."])
        out.append("")

    out.append("## Method")
    out.append("")
    out.append(f"- The scenario and its {len(s.get('tasks') or [])} tasks were "
               f"written by {s.get('scenario_owner','the customer')}.")
    out.append(f"- Metrics, units, directions and weights were sealed "
               f"**before** any measurement ({state}).")
    out.append(f"- Time box: {s.get('time_box_minutes','?')} minutes per entrant "
               f"on {s.get('hardware','identical hardware')}.")
    out.append("- Each entrant was operated by its own team, present throughout.")
    out.append("- This result is published in full, including the metrics on "
               "which the leader lost. That commitment was made before the "
               "result was known.")
    out.append("")
    out.append(f"<sub>Scored with rapp-bake-off {SCHEMA} · "
               f"seal {str(s.get('seal'))[:28]}…</sub>")

    text = "\n".join(out)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(text + "\n")
        print(f"  wrote {args.out}")
    else:
        print(text)
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="bakeoff",
                                description="Score a side-by-side evaluation.")
    sub = p.add_subparsers(dest="cmd", required=True)

    q = sub.add_parser("template", help="write a blank scenario")
    q.add_argument("--out")
    q.set_defaults(fn=cmd_template)

    q = sub.add_parser("register", help="seal metrics and weights before measuring")
    q.add_argument("scenario")
    q.set_defaults(fn=cmd_register)

    q = sub.add_parser("verify", help="was the pre-registration edited?")
    q.add_argument("scenario")
    q.set_defaults(fn=cmd_verify)

    q = sub.add_parser("score", help="the scorecard")
    q.add_argument("scenario")
    q.add_argument("--force", action="store_true")
    q.set_defaults(fn=cmd_score)

    q = sub.add_parser("card", help="a one-page result for the customer")
    q.add_argument("scenario")
    q.add_argument("--against", help="entrant to compare the leader against")
    q.add_argument("--out")
    q.add_argument("--force", action="store_true")
    q.set_defaults(fn=cmd_card)

    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
