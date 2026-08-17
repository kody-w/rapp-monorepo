#!/usr/bin/env python3
"""personpower.py — compute a RAPP Personpower (rpp) rating.

    python3 personpower.py --checks checks.json --engine-seconds 19.1
    python3 personpower.py --person-seconds 1200 --engine-seconds 19.1

checks.json: [{"type": "<key from spec/rates.json>", "count": N}, ...]
T_person = sum(rate[type] * count) + record_result per check (unless the
checklist already includes record_result entries).

P (pp) = T_person / T_engine. State the workload with the number.
"""

import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent


def t_person_from_checks(checks_path, rates_path):
    rates_doc = json.loads(pathlib.Path(rates_path).read_text("utf-8"))
    rates = rates_doc["rates"]
    checks = json.loads(pathlib.Path(checks_path).read_text("utf-8"))
    total, n = 0.0, 0
    has_record = any(c.get("type") == "record_result" for c in checks)
    for c in checks:
        t = c.get("type")
        if t not in rates:
            raise SystemExit("unknown check type %r — see spec/rates.json" % t)
        count = int(c.get("count", 1))
        total += rates[t] * count
        if t != "record_result":
            n += count
    if not has_record:
        total += rates["record_result"] * n
    return total, rates_doc["version"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checks", help="checks.json path")
    ap.add_argument("--person-seconds", type=float,
                    help="measured T_person (overrides --checks)")
    ap.add_argument("--engine-seconds", type=float, required=True)
    ap.add_argument("--rates", default=str(HERE / "spec" / "rates.json"))
    a = ap.parse_args()
    if a.person_seconds:
        tp, ver = a.person_seconds, "measured"
    elif a.checks:
        tp, ver = t_person_from_checks(a.checks, a.rates)
    else:
        ap.error("need --checks or --person-seconds")
    if a.engine_seconds <= 0:
        raise SystemExit("engine ran in no time? measure it (rule 4: no fake pulls)")
    print(json.dumps({
        "T_person_s": round(tp, 1),
        "T_engine_s": a.engine_seconds,
        "rpp": round(tp / a.engine_seconds, 1),
        "rates": ver,
        "note": "state the workload with the number (rule 5)",
    }, indent=2))


if __name__ == "__main__":
    sys.exit(main())
