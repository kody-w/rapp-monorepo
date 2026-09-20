#!/usr/bin/env python3
"""One lightweight Wi-Fi health sample -> JSONL. Spool local, mirror to NAS."""
import subprocess, re, json, sys, os, time, datetime, concurrent.futures

SPOOL, NAS = sys.argv[1], sys.argv[2]

def sh(cmd, t=25):
    try: return subprocess.run(cmd, capture_output=True, text=True, timeout=t).stdout
    except Exception: return ""

def rf():
    """Signal, channel, PHY, tx rate. Only obtainable from a WIRELESS client."""
    sp = sh(["system_profiler", "SPAirPortDataType"], 30)
    cur = sp.split("Current Network Information:")
    if len(cur) < 2: return {"associated": False}
    blk = cur[1].split("Other Local Wi-Fi Networks")[0]
    g = lambda p: (re.search(p, blk) or [None, None])[1]
    ch = re.search(r"Channel: (\d+) \((\d)GHz, (\d+)MHz\)", blk)
    return {"associated": True,
            "signal_dbm":  int(g(r"Signal / Noise: (-?\d+) dBm") or 0),
            "noise_dbm":   int(re.search(r"Signal / Noise: -?\d+ dBm / (-?\d+)", blk).group(1)) if re.search(r"Signal / Noise: -?\d+ dBm / (-?\d+)", blk) else None,
            "channel":     int(ch.group(1)) if ch else None,
            "band_ghz":    int(ch.group(2)) if ch else None,
            "width_mhz":   int(ch.group(3)) if ch else None,
            "phy":         (g(r"PHY Mode: (\S+)") or None),
            "tx_rate_mbps":int(g(r"Transmit Rate: (\d+)") or 0)}

def ping(host, n=50):
    o = sh(["ping", "-c", str(n), "-i", "0.2", "-W", "1000", host], 40)
    m = re.search(r"= ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)", o)
    l = re.search(r"([\d.]+)% packet loss", o)
    if not m: return {"reachable": False}
    return {"reachable": True, "min": float(m.group(1)), "avg": float(m.group(2)),
            "max": float(m.group(3)), "jitter": float(m.group(4)),
            "loss_pct": float(l.group(1)) if l else None}

def gateway():
    m = re.search(r"gateway:\s*(\S+)", sh(["route", "-n", "get", "default"], 10))
    return m.group(1) if m else None

def nodes():
    """Poll every Google/Nest unit's local API. This part COULD run on the NAS."""
    arp = sh(["arp", "-an"], 15)
    ips = sorted({ip for line in arp.splitlines() if "incomplete" not in line
                  for ip in re.findall(r"\d+\.\d+\.\d+\.\d+", line)},
                 key=lambda x: tuple(int(o) for o in x.split(".")))
    def probe(ip):
        try:
            o = subprocess.run(["curl", "-s", "-m", "3", f"http://{ip}/api/v1/status"],
                               capture_output=True, text=True, timeout=6).stdout
            d = json.loads(o); s = d.get("system", {})
            if not s.get("modelId"): return None
            return {"ip": ip, "role": s.get("groupRole"), "model": s.get("modelId"),
                    "uptime_d": round(s.get("uptime", 0) / 86400, 2),
                    "eth_backhaul": bool(s.get("lan0Link")),
                    "sw": d.get("software", {}).get("softwareVersion")}
        except Exception: return None
    with concurrent.futures.ThreadPoolExecutor(max_workers=40) as ex:
        out = [r for r in ex.map(probe, ips) if r]
    return out, len(ips)

gw = gateway()
n, host_count = nodes()
sample = {
    "ts": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    "host": (sh(["scutil","--get","ComputerName"],5).strip() or os.uname().nodename),
    "rf": rf(),
    "gateway_ip": gw,
    "wifi_hop": ping(gw) if gw else {"reachable": False},   # the Wi-Fi air hop
    "internet": ping("1.1.1.1", 30),                        # end-to-end path
    "nodes": n,
    "node_count": len(n),
    "wireless_backhaul_nodes": sum(1 for x in n if not x["eth_backhaul"]),
    "lan_hosts": host_count,
}
# derived health flags - what to actually alert on
w = sample["wifi_hop"]
sample["flags"] = [f for f in [
    "JITTER_HIGH"      if w.get("jitter", 0) > 15 else None,
    "SPIKE"            if w.get("max", 0) > 100 else None,
    "LOSS"             if (w.get("loss_pct") or 0) > 0 else None,
    "WEAK_SIGNAL"      if sample["rf"].get("signal_dbm", 0) < -70 else None,
    "SLOW_PHY"         if 0 < sample["rf"].get("tx_rate_mbps", 0) < 120 else None,
    "NODE_REBOOTED"    if any(x["uptime_d"] < 0.5 for x in n) else None,
] if f]

os.makedirs(SPOOL, exist_ok=True)
day = datetime.date.today().isoformat()
local = os.path.join(SPOOL, f"wifi-{day}.jsonl")
with open(local, "a") as f:
    f.write(json.dumps(sample) + "\n")

# --- Ship to the NAS over HTTP -------------------------------------------------
# HTTP, not SMB: macOS TCC forbids launchd agents from touching network volumes
# (verified - a LaunchAgent gets DENIED on both ls and write to /Volumes). An
# HTTP POST is not gated, so the same code works on every probe with no
# credentials and no per-machine Full Disk Access grant.
# Everything is spooled locally first and a cursor tracks what the NAS has, so
# while the endpoint is down nothing is lost - the next success backfills.
import urllib.request
INGEST = os.environ.get("WIFIMON_INGEST") or sys.exit("WIFIMON_INGEST not set")
cursor_path = os.path.join(SPOOL, ".nas_cursor.json")
try: cursor = json.load(open(cursor_path)) if os.path.exists(cursor_path) else {}
except Exception: cursor = {}

def post(batch):
    req = urllib.request.Request(INGEST, data=json.dumps(batch).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=12) as r:
        return json.loads(r.read().decode()).get("ok") is True

synced, backlog = False, 0
try:
    for fn in sorted(f for f in os.listdir(SPOOL) if f.endswith(".jsonl")):
        lines = open(os.path.join(SPOOL, fn)).read().splitlines()
        pending = [json.loads(l) for l in lines[cursor.get(fn, 0):] if l.strip()]
        backlog += len(pending)
        for i in range(0, len(pending), 200):          # chunk so a long outage still flushes
            if not post(pending[i:i+200]): raise RuntimeError("ingest rejected")
        cursor[fn] = len(lines)
    json.dump(cursor, open(cursor_path, "w"))
    synced = True
except Exception as e:
    print("ingest unavailable (%s) - %d sample(s) spooled locally" % (e, backlog), file=sys.stderr)

# --- Alert -------------------------------------------------------------------
# Fires only on a SUSTAINED problem: two consecutive bad samples (~10 min).
# A single bad sample is normal RF noise - alerting on it trains you to ignore
# alerts. Rate-limited to one notification per 30 min so a long bad stretch
# nags once, not twelve times.
def alert(msg, state_path=os.path.join(SPOOL, ".alert_state.json")):
    try: st = json.load(open(state_path))
    except Exception: st = {}
    now = time.time()
    if now - st.get("last", 0) < 1800: return False
    subprocess.run(["osascript", "-e",
        'display notification "%s" with title "Wi-Fi degraded" sound name "Basso"'
        % msg.replace('"', "'")], capture_output=True, timeout=10)
    json.dump({"last": now}, open(state_path, "w"))
    return True

alerted = False
try:
    recent = [json.loads(l) for l in open(local).read().splitlines()[-2:] if l.strip()]
    bad = lambda r: any(f in r.get("flags", []) for f in ("JITTER_HIGH", "SPIKE", "LOSS"))
    if len(recent) == 2 and all(bad(r) for r in recent):
        j = recent[-1].get("wifi_hop", {})
        alerted = alert("jitter %.0f ms, spikes to %.0f ms - calls will break up"
                        % (j.get("jitter", 0), j.get("max", 0)))
except Exception as e:
    print("alert check failed:", e, file=sys.stderr)

print(json.dumps({"ts": sample["ts"], "jitter": w.get("jitter"), "max": w.get("max"),
                  "signal": sample["rf"].get("signal_dbm"), "nodes": sample["node_count"],
                  "flags": sample["flags"], "shipped": synced, "backlog": backlog, "alerted": alerted}))
