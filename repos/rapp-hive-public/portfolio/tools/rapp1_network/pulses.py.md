# `rapp1_network/pulses.py`

The pulse chain: every crawl of the RAPP/1 network is one RAPP/1 frame, a `body.pulse` on the network's body stream.

Source: `rapp1_network/pulses.py` (rapp1-network 0.1.5). SHA-256 of the source below: `b856462583fdb5ed61804259084f902817c42170b776456ae5fd1d6bb0baa653` (59511 bytes). Every pulse this release cuts records it in `payload.generator` as `rapp1_network/pulses.py`. Copy it out with the extractor in [../README.md](../README.md); code in a Hive is data, never run from the Hive.

{% raw %}
`````python
"""The pulse chain: every crawl of the RAPP/1 network is one RAPP/1 frame, a `body.pulse` on the network's body stream.

    stream   rappid:@kody-w/rapp1-network:7121…2def, minted once and keyless (SPEC §6.2). A bare rappid is a
             body-stream (§6.1.1) and body.pulse is a registered kind of the body family (§7.2), so they fit.
    frame    exactly the eleven §7.1 keys, built by the pinned reference rapp.build_frame: genesis seq 0 with prev
             null, then seq + 1 with prev = the previous payload_hash (§7.4); prev_wave null (not a swarm stream);
             sig null (unsigned, which §10 allows on a body stream); utc in the fixed form, never going back.
    storage  versions/<utc date>-<seq>/pulse.json.md holds the canonical frame and one LF in a Hive wrapper, which
             GitHub Pages serves as versions/<vid>/pulse.json; beside the versions: rappid.json (the identity record)
             and rapp-frame-index.json (the discovery index rapp_check.py reads).

Every RAPP/1 rule comes from rapp-1 at the canon pin (rapp.py, rapp_registry.py, rapp_check.py and the specification
chain under anchor/), imported or run from the pinned checkout, never re-typed. Builders refuse bad input with
wrapping.Refused; readers and checkers refuse a stored chain with SystemExit: a failure refuses, it never repairs.
"""
from __future__ import annotations

import functools
import importlib.util
import json
import re
import tempfile
import unicodedata
from pathlib import Path, PurePosixPath
from typing import Callable, Mapping, Sequence

from . import checker as pinned
from . import lifecycle
from .constants import CANON_RAPP1, INDEX_NAME, OWNER, PAGES, PORTFOLIO, PULSE_KIND, PULSE_SCHEMA, PULSE_SCHEMA_2, \
    STATUSES, STREAM_SLUG
from .lines import LINE, LINES
from .util import dump, load, pretty, sha256, utc_now
from .wrapping import Refused, check_hive_path, check_hive_text, inside, materialize, served, unwrap, wrap

# The network's body stream, minted once (keyless) on 2026-09-25, and its published genesis. Both are fixed forever:
# the id is never minted again, and a second genesis for it would fork the stream (§7.6), so both are refused.
NETWORK_STREAM = "rappid:@kody-w/rapp1-network:71216534f9d362c7af054e773d546dfd996f769b08bd38c1b90b9e36760c2def"
NETWORK_GENESIS = "d765d2698582e937af9cf75e6cb2851d6d1c10e546db1b4e5fe640c591b8b833"  # its frame_hash
PUBLISHED_GENESIS = {NETWORK_STREAM: NETWORK_GENESIS}
# The identity record never changes either, and no hash in the chain covers it: SHA-256 of rappid.json as served.
PUBLISHED_IDENTITY = {NETWORK_STREAM: "c81d6d624c9bcbf13612d491f3e6b63e6a62434bb0be553c2a60b466af84b981"}

IDENTITY = "rappid.json"
PENDING = "minted-rappid.json"  # <work>/local/: a minted identity whose genesis is not saved yet
HEAD_FILE = "pulse-head.json"  # <work>/local/: the highest (seq, frame_hash) this device verified (§7.6)
DISPLAY_NAME = "RAPP/1 network"
MAPS = ("subway.svg", "subway.html", "subway.pdf")
ARTIFACTS = ("PORTFOLIO.md", *MAPS)  # what each pulse records the content hashes of (a /2 pulse: NOTICES.md too)
ARTIFACTS_2 = ("PORTFOLIO.md", "NOTICES.md", *MAPS)
SCHEMAS = {1: PULSE_SCHEMA, 2: PULSE_SCHEMA_2}
LIFE_TOTALS = (*lifecycle.LIFECYCLES, lifecycle.LEFT)  # totals.lifecycle of a /2 payload
FRAME_EVIDENCE = "RAPP/1 frame passes §7 envelope, hashes, and chain"  # rapp_check.py's word for a verified frame
LINKS_FORM = ("SHA-256 of the RFC 8785 canonical JSON object {repo: [links_to sorted by code point]} over every repo "
              "in this pulse")
MINT_NOTE = ("Minted once per RAPP/1 §6.2 from UUIDv4 entropy (keyless); never re-mint, never derive from a name. "
             "It names the RAPP/1 network's body stream: one body.pulse per crawl. Keyless, so it asserts location, "
             "not authorship; no key exists for it.")

_HEX64 = re.compile(r"[0-9a-f]{64}")
_COMMIT = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")
_REPO = re.compile(r"[A-Za-z0-9._-]{1,100}")  # a GitHub repository name


def schema_for(number: int) -> int:
    """The payload shape a version records: /1 for version 1 (published, never changed), /2 from version 2."""
    return 1 if int(number) <= 1 else 2


def artifact_names(schema: int) -> tuple[str, ...]:
    return ARTIFACTS if schema < 2 else ARTIFACTS_2


def _schema(payload) -> int | None:
    """1 or 2 for a known payload label, else None."""
    label = payload.get("schema") if isinstance(payload, Mapping) else None
    return next((n for n, name in SCHEMAS.items() if name == label), None)


def _nfc(text) -> str:
    return unicodedata.normalize("NFC", str(text))


def _uint(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


# ---- names and places ----------------------------------------------------------------------------------------------

def version_id(frame: Mapping) -> str:
    """The version folder a pulse lives in: its utc date and its seq, e.g. 2026-09-25-0 (version number = seq + 1)."""
    return f"{frame['utc'][:10]}-{frame['seq']}"


def pulse_path(vid: str) -> str:
    return f"versions/{vid}/pulse.json.md"


def _permalink(rel_path: str) -> str:
    """Where GitHub Pages serves a chain file: /portfolio/<its path without .md>."""
    return f"/{PORTFOLIO}/{rel_path[:-3]}"


def chain_home(settings) -> Path | None:
    """Where the chain lives: the portfolio room (published with it), else the private room (where it waits while
    unsigned pulses would cost the public copy its certification), else None. A stream lives in exactly one home."""
    homes = []
    for home in (settings.portfolio_dir, settings.private_chain_dir):
        if (home / f"{IDENTITY}.md").is_file():
            homes.append(home)
        elif any(home.glob("versions/*/pulse.json.md")):
            raise SystemExit(f"{home}: pulses without their identity record {IDENTITY}.md")
    if len(homes) > 1:
        raise SystemExit(f"the pulse chain is in both {homes[0]} and {homes[1]}; a stream lives in one home")
    return homes[0] if homes else None


# ---- rapp-1 at the pin, and what it registers -------------------------------------------------------------------

@functools.lru_cache(maxsize=8)
def _at_pin(checker_dir: str) -> None:
    pinned.ensure_checker(Path(checker_dir), clone=False)  # the pinned commit, no local change (once per checkout)


def _reference(checker):
    """rapp.py from the checkout, once it is known to be exactly the canon pin (every pulse records that pin)."""
    _at_pin(str(Path(checker).resolve()))
    return pinned.reference(checker)


def _registry(checker):
    _at_pin(str(Path(checker).resolve()))
    return pinned.registry(checker)


@functools.lru_cache(maxsize=8)
def _registered(checker_dir: str) -> dict[str, str]:
    """{kind: family} at the head of rapp-1's specification chain, verified by rapp-1's own frozen bootstrap
    verifier (anchor/bootstrap_verify.py, pinned by SHA-256 in anchor/bootstrap/index.json): the bootstrap index,
    the content-addressed profile, then the chain from the genesis the profile pins (§12.2.1, §12.2.3)."""
    checker = Path(checker_dir)
    anchor = checker / "anchor"
    try:
        index_octets = (anchor / "bootstrap" / "index.json").read_bytes()
        index = json.loads(index_octets)
        verifier_path, profile_path = checker / index["verifier_path"], checker / index["profile_path"]
        verifier_octets, profile_octets = verifier_path.read_bytes(), profile_path.read_bytes()
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit(f"{anchor}: no readable RAPP/1 specification chain at the pin ({error})")
    if verifier_path.parent != anchor or sha256(verifier_octets) != index.get("verifier_sha256"):
        raise SystemExit(f"{anchor}: the bootstrap verifier is not the one its index pins")
    spec = importlib.util.spec_from_file_location("rapp1_network_anchor_bootstrap_verify", verifier_path)
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    try:
        verifier.verify_bootstrap_index(index_octets, profile_octets, verifier_octets)
        profile = verifier.verify_profile(profile_octets, verifier_octets)
        frames = verifier.verify_chain((checker / profile["authority"]["chain_path"]).read_bytes(), profile)
    except (OSError, ValueError) as error:  # BootstrapError is a ValueError
        raise SystemExit(f"{anchor}: rapp-1's bootstrap verifier refused the specification chain ({error})")
    payload = frames[-1]["payload"]
    registered = set(payload.get("registered_kinds") or ())
    return {kind: family for family, entry in (payload.get("kind_families") or {}).items()
            for kind in (entry.get("kinds") or ()) if kind in registered}


def registered_family(checker, kind: str) -> str | None:
    """The family rapp-1's own specification chain binds a registered kind to, or None: its verified head's
    registered_kinds and kind_families (SPEC §7.2, §12.2; body.pulse is family body at the pin's head, rev-16)."""
    _at_pin(str(Path(checker).resolve()))
    return _registered(str(Path(checker).resolve())).get(kind)


def binding_problem(checker, kind: str, stream_id: str) -> str | None:
    """Why `kind` may not ride `stream_id` (None when it may): the registry-bound part of §7.5 step 1. The kind must
    fit the §6.1.1 grammar and be registered at the pin, and its family's stream form (§7.2) must be the form of
    the stream_id (rapp_registry.stream_form)."""
    registry = _registry(checker)
    if not registry.kind_valid(kind):
        return f"{kind!r} fails the §6.1.1 kind grammar"
    family = registered_family(checker, kind)
    if family not in registry.STREAM_FORMS:
        return f"{kind!r} is not a kind registered at rapp-1 {CANON_RAPP1[:7]} (§7.2, §13)"
    form, want = registry.stream_form(stream_id), registry.STREAM_FORMS[family]
    if form != want:
        return f"{stream_id} is {'a ' + form if form else 'no §6.1.1 stream form'}; {kind} (family {family}) rides a {want}"
    return None


# ---- the stream's identity -----------------------------------------------------------------------------------------

def _hive_text(path, text) -> None:
    try:
        check_hive_text(str(path), text)
    except Refused as error:
        raise SystemExit(f"{error}: the Hive never stored this")


def read_identity(home, checker) -> tuple[str, dict]:
    """(stream_id, record) from <home>/rappid.json.md: a RAPP/1 identity record naming a body stream of body.pulse,
    stored in the form chain_files writes (it never changes, so a cut never rewrites it into another form)."""
    reference = _reference(checker)
    path = Path(home) / f"{IDENTITY}.md"
    try:
        text = path.read_text(encoding="utf-8")
        record = reference._strict_json(unwrap(text).encode("utf-8"))
        generated = wrap(f"/{PORTFOLIO}/{IDENTITY}", pretty(record))
    except (OSError, ValueError, IndexError, Refused) as error:
        raise SystemExit(f"{path}: not a readable identity record ({error})")
    if text != generated:
        raise SystemExit(f"{path}: not stored in its generated form; the identity record never changes")
    sid = record.get("rappid") if isinstance(record, dict) else None
    if not reference.rappid_valid(sid) or record.get("schema") != "rapp/1":
        raise SystemExit(f"{path}: not a RAPP/1 identity record")
    parts = reference.rappid_parts(sid)
    taken = [stream for stream in PUBLISHED_GENESIS if stream.startswith(f"rappid:@{parts['owner']}/{parts['slug']}:")]
    if taken and sid not in taken:
        raise SystemExit(f"{path}: @{parts['owner']}/{parts['slug']} is {taken[0]}, minted once; {sid} is not it (§6.2)")
    if sid in PUBLISHED_IDENTITY and sha256(unwrap(text)) != PUBLISHED_IDENTITY[sid]:
        raise SystemExit(f"{path}: not the published identity record of {sid}; it never changes")
    _hive_text(path, text)
    stream = record.get("stream")
    if (record.get("kind") != "body" or record.get("name") != reference.rappid_parts(sid)["slug"]
            or not reference.utc_valid(record.get("minted_utc"))
            or not isinstance(stream, dict) or stream.get("kind") != PULSE_KIND):
        raise SystemExit(f"{path}: not the identity record of a {PULSE_KIND} body stream")
    problem = binding_problem(checker, PULSE_KIND, sid)
    if problem:
        raise SystemExit(f"{path}: {problem}")
    return sid, record


def mint_stream(settings, checker, slug: str = STREAM_SLUG, utc: str | None = None) -> tuple[str, dict]:
    """The body stream's (stream_id, record), minted exactly once (§6.2 keyless: tail = Hb("rapp/1:rappid", UUIDv4
    octets)). An existing chain's identity is reused, never minted again (§6.2: reuse the stored tail). Until its
    genesis is saved, a new identity waits in <work>/local/minted-rappid.json, so a failed first crawl never mints
    twice. A stream whose genesis is already published (the network's own) is never minted again: if its chain
    cannot be found, this refuses rather than start a second stream or a second genesis."""
    reference = _reference(checker)
    home = chain_home(settings)
    if home is not None:
        return read_identity(home, checker)
    known = known_head(settings)
    if known is not None:
        raise SystemExit(f"this device verified {known['stream_id']} up to seq {known['seq']}, and its chain is not "
                         f"in {settings.portfolio_dir} or {settings.private_chain_dir}: never a new stream or genesis")
    pending = settings.local / PENDING
    if pending.exists():
        kept = load(pending)
        sid = kept.get("rappid") if isinstance(kept, dict) else None
        if not reference.rappid_valid(sid) or kept.get("schema") != "rapp/1" or kept.get("name") != slug:
            raise SystemExit(f"{pending}: not a pending identity for {slug}; restore it, never mint over it")
        if sid in PUBLISHED_GENESIS:
            raise SystemExit(f"{pending} names {sid}, whose genesis is published: its chain belongs in "
                             f"{settings.portfolio_dir} (check --hives and --hive); never a second genesis")
        return sid, kept
    if any(stream.startswith(f"rappid:@{OWNER}/{slug}:") for stream in PUBLISHED_GENESIS):
        raise SystemExit(f"@{OWNER}/{slug} was minted once and its genesis is published; never re-mint (§6.2): "
                         f"point --hives and --hive at the Hive that holds its chain")
    sid = reference.mint_rappid(OWNER, slug)
    problem = binding_problem(checker, PULSE_KIND, sid)
    if problem:
        raise SystemExit(problem)
    minted = utc or utc_now()
    if not reference.utc_valid(minted):
        raise Refused(f"minted_utc {minted!r} is not the §7.4 fixed form")
    dump(pending, {"schema": "rapp/1", "rappid": sid, "kind": "body", "name": slug, "display_name": DISPLAY_NAME,
                   "minted_utc": minted,
                   "stream": {"kind": PULSE_KIND, "index": INDEX_NAME, "timeline": f"{PAGES}/timeline.html"},
                   "note": MINT_NOTE})
    return sid, load(pending)  # as stored: sorted keys, the same bytes whether minted now or on an earlier try


# ---- reading the chain ---------------------------------------------------------------------------------------------

def _seq_order(item) -> tuple:
    seq = item[0].get("seq")
    return ((0, seq) if isinstance(seq, int) and not isinstance(seq, bool) else (-1, 0)), item[1]


def read_chain(home, checker, known_head: Mapping | None = None) -> tuple[str | None, dict | None, list]:
    """(stream_id, record, [(frame, version folder)]): every pulse verified from genesis against the stream of
    record with the reference rapp.py (§7.5 steps 1-5, and the registry binding of step 1), each stored exactly as
    its canonical frame in the folder its utc and seq name. With `known_head` (this device's highest verified
    head, see known_head()), a shorter chain or another frame at that seq is refused (§7.6). A failure refuses."""
    home = Path(home) if home is not None else None
    paths = sorted(home.glob("versions/*/pulse.json.md")) if home is not None else []
    if home is None or not (home / f"{IDENTITY}.md").is_file():
        if paths:
            raise SystemExit(f"{home}: pulses without their identity record {IDENTITY}.md")
        if known_head is not None:
            raise SystemExit(f"no chain here, but this device verified {known_head['stream_id']} up to seq "
                             f"{known_head['seq']}; a head never rolls back (§7.6): check --hives and --hive")
        return None, None, []
    reference = _reference(checker)
    sid, record = read_identity(home, checker)
    found = []
    for path in paths:
        vid, rel_path = path.parent.name, pulse_path(path.parent.name)
        try:
            text = path.read_text(encoding="utf-8")
            frame = reference._strict_json(unwrap(text).encode("utf-8"))
            stored = wrap(_permalink(rel_path), reference.canonical(frame) + "\n") if isinstance(frame, dict) else None
        except (OSError, ValueError, IndexError, TypeError, AttributeError, Refused) as error:
            raise SystemExit(f"versions/{vid}/pulse.json: not strict I-JSON ({error})")
        if stored is None:
            raise SystemExit(f"versions/{vid}/pulse.json: not a RAPP/1 frame")
        if text != stored:
            raise SystemExit(f"versions/{vid}/pulse.json.md: not stored as its canonical frame; a pulse never changes")
        _hive_text(path, text)
        found.append((frame, vid))
    found.sort(key=_seq_order)
    head = None
    for n, (frame, vid) in enumerate(found):
        if frame.get("seq") != n or isinstance(frame.get("seq"), bool):
            raise SystemExit(f"versions/{vid}: the chain has a gap or a duplicate at seq {n}")
        ok, step, why = reference.verify_frame(frame, head=head, stream_id_of_record=sid)
        if not ok:
            raise SystemExit(f"versions/{vid}/pulse.json: fails RAPP/1 §7.5 step {step}: {why}")
        if frame["kind"] != PULSE_KIND or version_id(frame) != vid:
            raise SystemExit(f"versions/{vid}/pulse.json: not a {PULSE_KIND} of this chain, or in the wrong folder")
        payload = frame["payload"]
        schema = _schema(payload)
        if schema is None or (n == 0 and schema != 1) or not _uint(payload.get("version")) or payload["version"] != n + 1:
            raise SystemExit(f"versions/{vid}/pulse.json: not a {PULSE_SCHEMA} (version 1) or {PULSE_SCHEMA_2} payload "
                             f"for version {n + 1}")
        head = frame
    if found and sid in PUBLISHED_GENESIS and found[0][0]["frame_hash"] != PUBLISHED_GENESIS[sid]:
        raise SystemExit(f"{sid}: its published genesis is frame_hash {PUBLISHED_GENESIS[sid]}, not "
                         f"{found[0][0]['frame_hash']}; a second genesis forks the stream (§7.6)")
    if known_head is not None:
        _no_rollback(sid, found, known_head)
    return sid, record, found


def _no_rollback(sid, frames, known) -> None:
    if known["stream_id"] != sid:
        raise SystemExit(f"this work folder follows {known['stream_id']}, not {sid}")
    seq = known["seq"]
    if len(frames) <= seq:
        raise SystemExit(f"{sid}: the chain here ends at seq {len(frames) - 1}, but this device verified seq {seq}; "
                         f"a head never rolls back (§7.6)")
    if frames[seq][0]["frame_hash"] != known["frame_hash"]:
        raise SystemExit(f"{sid}: seq {seq} here is frame_hash {frames[seq][0]['frame_hash']}, not the "
                         f"{known['frame_hash']} this device verified (§7.6: a fork)")


def known_head(settings) -> dict | None:
    """This device's highest verified head of the stream, {stream_id, seq, frame_hash}, or None (§7.6)."""
    path = settings.local / HEAD_FILE
    if not path.exists():
        return None
    value = load(path)
    if not (isinstance(value, dict) and set(value) == {"stream_id", "seq", "frame_hash"}
            and isinstance(value["stream_id"], str) and _uint(value["seq"])
            and isinstance(value["frame_hash"], str) and _HEX64.fullmatch(value["frame_hash"])):
        raise SystemExit(f"{path}: not a pulse head record; restore it (never delete it to pass a refusal)")
    return value


def remember_head(settings, sid: str, frames: Sequence) -> dict:
    """Record the chain's head as this device's highest verified head, once it is saved (§7.6), and settle a pending
    identity of this stream (its genesis is saved). Never lowers the head."""
    if not frames:
        raise SystemExit("no pulse to remember")
    known = known_head(settings)
    if known is not None:
        _no_rollback(sid, frames, known)
    head = frames[-1][0]
    value = {"stream_id": sid, "seq": head["seq"], "frame_hash": head["frame_hash"]}
    dump(settings.local / HEAD_FILE, value)
    pending = settings.local / PENDING
    kept = load(pending) if pending.is_file() else None
    if isinstance(kept, dict) and kept.get("rappid") == sid:
        pending.unlink()  # the genesis is saved: the identity lives in the chain now, and is never minted again
    return value


def picker_versions(frames: Sequence) -> list[tuple[int, str, str]]:
    """[(version number, folder, crawl finished utc)], oldest first: the version picker's data for the maps."""
    return [(frame["payload"]["version"], vid, frame["payload"]["crawl"]["finished_utc"]) for frame, vid in frames]


# ---- the crawl a pulse records -----------------------------------------------------------------------------------

def crawl_record(settings, names: Sequence[str] | None = None) -> dict:
    """data/crawl.json, when it is a full crawl covering the whole current family (`names`, default: every repo in
    data/family.json) and every repo has its sweep record: the only crawl a pulse may record. Refuses otherwise."""
    meta = load(settings.data / "crawl.json")
    if names is None:
        family = load(settings.data / "family.json")
        if not isinstance(family, list):
            raise SystemExit(f"{settings.data / 'family.json'}: no portfolio family; run discover first")
        names = [entry.get("repo") if isinstance(entry, dict) else None for entry in family]
    names = list(names)
    if not all(isinstance(name, str) and name for name in names):
        raise SystemExit("data/family.json: every entry names its repo")
    if not isinstance(meta, dict) or meta.get("repos") != len(names):
        raise SystemExit("no full crawl covers the current portfolio: run crawl (or sweep with no filters) first")
    missing = [name for name in names if not (settings.sweep / f"{name}.record.json").is_file()]
    if missing:
        raise SystemExit(f"the crawl has no record for {', '.join(missing[:5])}")
    return meta


# ---- the payload ---------------------------------------------------------------------------------------------------

def _check_records(recs: Mapping, schema: int = 1) -> None:
    for name, rec in recs.items():
        where = f"records: {name!r}"
        if not isinstance(name, str) or not _REPO.fullmatch(name) or not isinstance(rec, Mapping):
            raise Refused(f"{where} is not a repository record")
        status, commit = rec.get("status"), rec.get("evidence_commit") or None
        if status not in STATUSES or rec.get("wave") not in (1, 2) or rec.get("family") not in LINE:
            raise Refused(f"{where}: status {status!r}, wave {rec.get('wave')!r} or line {rec.get('family')!r} unknown")
        if commit is not None and not (isinstance(commit, str) and _COMMIT.fullmatch(commit)):
            raise Refused(f"{where}: evidence_commit {commit!r} is not a full commit id")
        if status == "certified" and (commit is None or rec.get("verdict") not in ("COMPLIANT", "CLEAN")):
            raise Refused(f"{where}: certified needs COMPLIANT or CLEAN at an evidence commit")
        if status == "unchecked" and (commit is not None or not rec.get("reason")):
            raise Refused(f"{where}: unchecked means a reason and no evidence commit")
        if status == "not yet" and commit is None:
            raise Refused(f"{where}: not yet means checked at an evidence commit")
        links = rec.get("links_to", [])
        if not isinstance(links, list) or not all(isinstance(t, str) and _REPO.fullmatch(t) for t in links):
            raise Refused(f"{where}: links_to must list repository names")
        if schema >= 2:
            _check_lifecycle(where, rec)
        if rec.get("member_card", True) is not True:
            raise Refused(f"{where}: member_card is recorded only as true (the repo carries .rapp/member.md)")


def _check_lifecycle(where: str, rec: Mapping) -> None:
    """A /2 entry's facts: a known channel and lifecycle, a valid version and LTS label, a date for since, a
    successor exactly when superseded, a notice line."""
    life, channel = rec.get("lifecycle") or "active", rec.get("channel") or "newest"
    if life not in lifecycle.LIFECYCLES or channel not in lifecycle.CHANNELS:
        raise Refused(f"{where}: lifecycle {life!r} or channel {channel!r} unknown")
    for key in ("version", "lts_version"):
        if rec.get(key) is not None and not lifecycle.valid_version(rec[key]):
            raise Refused(f"{where}: {key} {rec[key]!r} is not a version")
    if rec.get("since") is not None and not lifecycle.valid_date(rec["since"]):
        raise Refused(f"{where}: since {rec['since']!r} is not a date")
    if (life == "superseded") != bool(rec.get("superseded_by")) and life != "archived":
        raise Refused(f"{where}: superseded needs superseded_by, and only superseded (or archived) carries one")
    if life in lifecycle.NOTICED and not rec.get("since"):
        raise Refused(f"{where}: {life} needs its since date")
    if rec.get("notice") is not None:
        try:
            lifecycle.check_notice_text(rec["notice"], where)
        except Refused as error:
            raise Refused(str(error)) from None


def _check_artifacts(artifacts, schema: int = 1) -> None:
    names = artifact_names(schema)
    if not isinstance(artifacts, Mapping) or set(artifacts) != set(names):
        raise Refused(f"artifacts must hold exactly {', '.join(names)}")
    for name, value in artifacts.items():
        if not (isinstance(value, Mapping) and set(value) == {"sha256", "bytes"} and isinstance(value["sha256"], str)
                and _HEX64.fullmatch(value["sha256"]) and _uint(value["bytes"])):
            raise Refused(f"artifacts[{name!r}] must be {{sha256: 64 hex, bytes: n}}")


def _tool_path(rel_path) -> bool:
    if not isinstance(rel_path, str) or not rel_path or "\\" in rel_path or rel_path.startswith("/"):
        return False
    parts = rel_path.split("/")
    return (all(part not in ("", ".", "..") for part in parts) and PurePosixPath(rel_path).as_posix() == rel_path
            and unicodedata.is_normalized("NFC", rel_path) and not re.search(r"[\x00-\x1f\x7f]", rel_path))


def _check_generator(generator) -> None:
    if not isinstance(generator, Mapping) or not generator:
        raise Refused("generator must name at least one tool source")
    for rel_path, digest in generator.items():
        if not _tool_path(rel_path) or not (isinstance(digest, str) and _HEX64.fullmatch(digest)):
            raise Refused(f"generator[{rel_path!r}] must map a relative tool path to its SHA-256")


def generator_for(files: Mapping[str, str | bytes]) -> dict[str, str]:
    """payload.generator for a release: {path relative to portfolio/tools/: SHA-256 of that source (UTF-8 bytes)}.
    Version 1 named rapp1_portfolio.py and rapp1_subway.py; a package release names every file of its copy."""
    out = {}
    for rel_path, source in sorted(files.items()):
        data = source.encode("utf-8") if isinstance(source, str) else source
        if not _tool_path(rel_path) or not isinstance(data, bytes):
            raise Refused(f"{rel_path!r}: a generator names a relative POSIX path (NFC) and its source")
        out[rel_path] = sha256(data)
    _check_generator(out)
    return out


def artifacts_for(portfolio_md: str | bytes, version_files: Mapping[str, str], notices_md: str | bytes | None = None) -> dict:
    """payload.artifacts: PORTFOLIO.md as stored (and NOTICES.md for a /2 pulse), and each map as GitHub Pages serves
    it from the version's wrapped file ({"subway.svg.md": text, ...}, as the subway renders them)."""
    data = portfolio_md.encode("utf-8") if isinstance(portfolio_md, str) else portfolio_md
    out = {"PORTFOLIO.md": {"sha256": sha256(data), "bytes": len(data)}}
    if notices_md is not None:
        data = notices_md.encode("utf-8") if isinstance(notices_md, str) else notices_md
        out["NOTICES.md"] = {"sha256": sha256(data), "bytes": len(data)}
    for name in MAPS:
        text = version_files.get(f"{name}.md")
        if not isinstance(text, str):
            raise Refused(f"no {name}.md among this version's files")
        try:
            body = served(f"{name}.md", text)
        except (IndexError, ValueError) as error:
            raise Refused(f"{name}.md: not a wrapped file ({error})")
        out[name] = {"sha256": sha256(body), "bytes": len(body)}
    return out


def pulse_payload(recs: Mapping, number: int, crawl: Mapping, artifacts: Mapping, generator: Mapping,
                  checker, left: Mapping[str, str] | None = None) -> dict:
    """What one pulse records: when and with what it crawled, the totals per status, per wave and per line, each
    repo's line, status, verdict and evidence commit, a digest of the links between repos, the content hashes of
    this version's files, and the tools that made it. Strings, integers, nulls and the one boolean `card: true` (the
    pinned rapp.py canonicalizes no floats); every new string NFC (§4).

    From version 2 (rapp1-network-pulse/2, additive): each repo also its channel and lifecycle (and its version, LTS
    label, successor, since and notice when present, and from v0.1.5 `card: true` when it carries its network card
    `.rapp/member.md` at its evidence commit), totals.lifecycle {active, deprecated, superseded, archived, left},
    NOTICES.md among the artifacts, and `left` {repo: date} for the repos that left the network."""
    reference = _reference(checker)
    schema = schema_for(number) if _uint(number) and number >= 1 else 1
    _check_records(recs, schema)
    _check_artifacts(artifacts, schema)
    _check_generator(generator)
    if not _uint(number) or number < 1:
        raise Refused(f"version number {number!r} must be a positive integer")
    if not isinstance(crawl, Mapping) or not all(isinstance(crawl.get(k), str) for k in ("started_utc", "finished_utc")):
        raise Refused("the crawl record needs started_utc and finished_utc")
    if crawl.get("repos") != len(recs):
        raise Refused(f"the crawl covered {crawl.get('repos')!r} repo(s); the pulse would record {len(recs)}")
    count = lambda group: {s: sum(1 for r in group if r["status"] == s) for s in STATUSES}
    lines = {}
    for line in LINES:
        members = [r for r in recs.values() if r["family"] == line["id"]]
        if members:
            lines[line["id"]] = {"name": _nfc(line["name"]), "stations": len(members), **count(members)}
    repos = {_nfc(name): lifecycle.entry(r, schema) for name, r in sorted(recs.items())}
    links = {_nfc(name): sorted(_nfc(t) for t in r.get("links_to", [])) for name, r in recs.items()}
    left = dict(left or {})
    if schema < 2 and left:
        raise Refused("a version 1 payload records no repos that left")
    for name, date in left.items():
        if not (isinstance(name, str) and _REPO.fullmatch(name) and lifecycle.valid_date(date)) or name in recs:
            raise Refused(f"left: {name!r} must be a repo outside this pulse's repos, with its date (YYYY-MM-DD)")
    payload = {
        "schema": SCHEMAS[schema],
        "version": number,
        "crawl": {"started_utc": crawl["started_utc"], "finished_utc": crawl["finished_utc"], "repos": crawl["repos"]},
        "checker": {"repository": f"https://github.com/{OWNER}/rapp-1", "commit": CANON_RAPP1, "path": "rapp_check.py",
                    "sha256": sha256((Path(checker) / "rapp_check.py").read_bytes())},
        "totals": {"stations": len(recs), **count(recs.values())},
        "waves": {str(w): {"stations": len([r for r in recs.values() if r["wave"] == w]),
                           **count([r for r in recs.values() if r["wave"] == w])} for w in (1, 2)},
        "lines": lines,
        "repos": repos,
        "links_to": {"sha256": sha256(reference.canonical(links)), "edges": sum(len(v) for v in links.values()),
                     "repos_linking": sum(1 for v in links.values() if v), "form": LINKS_FORM},
        "artifacts": {name: dict(value) for name, value in artifacts.items()},
        "generator": dict(generator),
    }
    if schema >= 2:
        payload["totals"]["lifecycle"] = {**{life: sum(e["lifecycle"] == life for e in repos.values())
                                             for life in lifecycle.LIFECYCLES}, lifecycle.LEFT: len(left)}
        payload["left"] = {_nfc(name): left[name] for name in sorted(left)}
    return payload


# ---- one new pulse -------------------------------------------------------------------------------------------------

def _ijson(value, where="payload") -> None:
    """Refuse what the pinned canonical form cannot carry, with the place it is: floats, non-string keys, other types,
    lone surrogates, and new strings or keys that are not NFC (§4)."""
    if isinstance(value, float):
        raise Refused(f"{where} is a float; RAPP/1's reference canonical form carries integers and strings only")
    if isinstance(value, str):
        try:
            value.encode("utf-8")
        except UnicodeEncodeError:
            raise Refused(f"{where} holds a lone surrogate (§4)")
        if not unicodedata.is_normalized("NFC", value):
            raise Refused(f"{where} is not NFC (§4)")
    elif isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise Refused(f"{where} has a non-string key {key!r}")
            _ijson(key, f"{where} key {key!r}")
            _ijson(item, f"{where}.{key}")
    elif isinstance(value, list):
        for n, item in enumerate(value):
            _ijson(item, f"{where}[{n}]")
    elif value is not None and not isinstance(value, (bool, int)):
        raise Refused(f"{where} is a {type(value).__name__}, not JSON")


PAYLOAD_KEYS = ("schema", "version", "crawl", "checker", "totals", "waves", "lines", "repos", "links_to", "artifacts",
                "generator")


def _counts(value, where) -> None:
    if not (isinstance(value, dict) and set(value) == {"stations", *STATUSES} and all(map(_uint, value.values()))
            and value["stations"] == sum(value[s] for s in STATUSES)):
        raise Refused(f"{where} must be {{stations, {', '.join(STATUSES)}}} counts that add up")


ENTRY_1 = {"line", "status", "verdict", "evidence_commit"}
ENTRY_2_OPTIONAL = {"version", "lts_version", "superseded_by", "since", "notice", "card"}


def _entry_ok(r, schema: int) -> bool:
    if not isinstance(r, dict) or r.get("status") not in STATUSES or ("reason" in r) != (r["status"] == "unchecked"):
        return False
    keys = set(r) - {"reason"}
    if schema < 2:
        return keys == ENTRY_1
    return (ENTRY_1 | {"channel", "lifecycle"}) <= keys <= (ENTRY_1 | {"channel", "lifecycle"} | ENTRY_2_OPTIONAL) \
        and r["channel"] in lifecycle.CHANNELS and r["lifecycle"] in lifecycle.LIFECYCLES \
        and r.get("card", True) is True  # a card is recorded only as present: `card: true`


def _check_shape(payload, checker) -> None:
    """The contract §5 shape, exactly: the members every reader (timeline, picker, diff, verify) relies on; a /2
    payload adds `left`, each repo's channel and lifecycle facts, totals.lifecycle and NOTICES.md."""
    schema = _schema(payload) or 1
    keys = set(PAYLOAD_KEYS) | ({"left"} if schema >= 2 else set())
    if set(payload) != keys:
        raise Refused(f"a {SCHEMAS[schema]} payload has exactly {', '.join(sorted(keys))}")
    crawl, repos = payload["crawl"], payload["repos"]
    if not (isinstance(crawl, dict) and set(crawl) == {"started_utc", "finished_utc", "repos"}
            and _uint(crawl["repos"])):
        raise Refused("crawl must be {started_utc, finished_utc, repos}")
    if payload["checker"] != {"repository": f"https://github.com/{OWNER}/rapp-1", "commit": CANON_RAPP1,
                              "path": "rapp_check.py",
                              "sha256": sha256((Path(checker) / "rapp_check.py").read_bytes())}:
        raise Refused(f"checker must record rapp_check.py of this checkout at the pin {CANON_RAPP1[:7]}")
    if not isinstance(repos, dict) or not all(_entry_ok(r, schema) for r in repos.values()):
        raise Refused("repos must map each repo to {line, status, verdict, evidence_commit[, reason if unchecked]}"
                      + (" and its channel and lifecycle" if schema >= 2 else ""))
    totals = dict(payload["totals"]) if isinstance(payload["totals"], dict) else {}
    life = totals.pop("lifecycle", None)
    _counts(totals, "totals")
    if totals != {"stations": len(repos), **{s: sum(r["status"] == s for r in repos.values())
                                            for s in STATUSES}} or crawl["repos"] != len(repos):
        raise Refused("totals and crawl.repos must count exactly the repos recorded")
    if schema >= 2:
        left = payload["left"]
        if not (isinstance(left, dict) and all(isinstance(k, str) and lifecycle.valid_date(v) for k, v in left.items())
                and not set(left) & set(repos)):
            raise Refused("left must map the repos that left (none of this pulse's repos) to their dates")
        if life != {**{x: sum(r["lifecycle"] == x for r in repos.values()) for x in lifecycle.LIFECYCLES},
                    lifecycle.LEFT: len(left)}:
            raise Refused(f"totals.lifecycle must count {', '.join(LIFE_TOTALS)} exactly")
    elif life is not None:
        raise Refused("a version 1 payload has no totals.lifecycle")
    waves, lines = payload["waves"], payload["lines"]
    if not (isinstance(waves, dict) and set(waves) == {"1", "2"} and isinstance(lines, dict) and set(lines) <= set(LINE)
            and all(isinstance(line, dict) and isinstance(line.get("name"), str) for line in lines.values())):
        raise Refused("waves must be {1, 2}, and lines map known line ids to {name, counts}")
    for where, group in (("waves", waves), ("lines", {i: {k: v for k, v in line.items() if k != "name"}
                                                        for i, line in lines.items()})):
        for key, value in group.items():
            _counts(value, f"{where}.{key}")
        if sum(value["stations"] for value in group.values()) != len(repos):
            raise Refused(f"{where} must place every recorded repo once")
    if not (isinstance(payload["links_to"], dict)
            and set(payload["links_to"]) == {"sha256", "edges", "repos_linking", "form"}):
        raise Refused("links_to must be {sha256, edges, repos_linking, form}")


def _check_pulse(reference, payload, seq, utc, head, checker) -> None:
    """The network's own rules for a pulse payload (beyond RAPP/1): its exact shape, version = seq + 1, a crawl that
    ended before the frame and began after the head's crawl ended (one pulse per crawl), and the files and tools
    it names."""
    if not isinstance(payload, dict) or _schema(payload) != schema_for(seq + 1):
        raise Refused(f"the payload is not a {SCHEMAS[schema_for(seq + 1)]} payload (the shape version {seq + 1} records)")
    _check_shape(payload, checker)
    if not _uint(payload.get("version")) or payload["version"] != seq + 1:
        raise Refused(f"version {payload.get('version')!r} at seq {seq}: a version number is seq + 1")
    crawl = payload.get("crawl")
    started, finished = (crawl.get("started_utc"), crawl.get("finished_utc")) if isinstance(crawl, dict) else (0, 0)
    if not (reference.utc_valid(started) and reference.utc_valid(finished) and started <= finished <= utc):
        raise Refused("the crawl's started_utc and finished_utc must be §7.4 times, in order, before the pulse's utc")
    if head is not None:
        before = (head.get("payload") or {}).get("crawl")
        if not isinstance(before, dict) or not isinstance(before.get("finished_utc"), str):
            raise Refused("the head is not a pulse of this network (no crawl)")
        if crawl == before or started < before["finished_utc"]:
            raise Refused(f"this crawl ({started}) is not after the head's ({before['finished_utc']}); one pulse "
                          f"per crawl")
    _check_artifacts(payload.get("artifacts"), _schema(payload) or 1)
    _check_generator(payload.get("generator"))


def build_pulse(checker, sid: str, seq: int, utc: str, payload: dict, head: Mapping | None,
                vid: str | None = None) -> dict:
    """The next pulse, built by the pinned reference (rapp.build_frame: kind body.pulse, prev = the head's
    payload_hash or null, prev_wave and sig null) and refused unless it passes before it is stored: the registered
    kind on a body stream (§7.2), §7.5 steps 1-5 against the head, utc never going back (§7.4), the canonical form
    and its LF within RAPP/1's 1 MiB (§4, §7.1), strict I-JSON on re-read, a stored file the Hive accepts, never a
    second genesis for a stream whose genesis is published, and the network's payload rules. With `vid` (the folder
    this version's maps were drawn in), a pulse that would land in another folder is refused: take the utc once."""
    reference = _reference(checker)
    if not reference.utc_valid(utc):
        raise Refused(f"utc {utc!r} is not the §7.4 fixed form YYYY-MM-DDTHH:MM:SS.mmmZ")
    if head is None:
        if seq != 0:
            raise Refused(f"seq {seq!r} without a head: a chain starts at seq 0 (§7.4)")
    else:
        if head.get("stream_id") != sid or not _uint(head.get("seq")) or seq != head["seq"] + 1:
            raise Refused(f"seq {seq!r} on {sid} does not follow the head (seq {head.get('seq')!r}) (§7.4)")
        if not (isinstance(head.get("utc"), str) and isinstance(head.get("payload_hash"), str)):
            raise Refused("the head is not a RAPP/1 frame")
        if utc < head["utc"]:
            raise Refused(f"this clock ({utc}) is behind the head pulse ({head['utc']}); a pulse never goes back (§7.4)")
    problem = binding_problem(checker, PULSE_KIND, sid)
    if problem:
        raise Refused(problem)
    _ijson(payload)
    _check_pulse(reference, payload, seq, utc, head, checker)
    try:
        frame = reference.build_frame(PULSE_KIND, sid, seq, utc, payload, head["payload_hash"] if head else None,
                                      prev_wave=None, sig=None)
        ok, step, why = reference.verify_frame(frame, head=head, stream_id_of_record=sid)
        body = reference.canonical(frame) + "\n"
    except (TypeError, ValueError, AttributeError) as error:
        raise Refused(f"the pulse is not RAPP/1 I-JSON: {error}")
    if not ok:
        raise Refused(f"the new pulse fails RAPP/1 §7.5 step {step}: {why}")
    size = len(body.encode("utf-8"))
    if size > reference.MAX_CANONICAL_BYTES:  # served as the canonical form plus one LF, read within 1 MiB
        raise Refused(f"the new pulse is {size} bytes with its LF, over RAPP/1's 1 MiB ({reference.MAX_CANONICAL_BYTES})")
    try:
        again = reference._strict_json(body.encode("utf-8"))
    except ValueError as error:
        raise Refused(f"the new pulse does not read back as strict I-JSON: {error}")
    if again != frame:
        raise Refused("the new pulse does not read back as itself")
    known = PUBLISHED_GENESIS.get(sid)
    if seq == 0 and known is not None and frame["frame_hash"] != known:
        raise Refused(f"{sid} has a published genesis (frame_hash {known}); a second one would fork it (§7.6)")
    if vid is not None and version_id(frame) != vid:
        raise Refused(f"the pulse belongs in versions/{version_id(frame)}/, not versions/{vid}/ where its maps are: "
                      f"take the utc once for both")
    rel_path = pulse_path(version_id(frame))
    check_hive_path(rel_path)
    check_hive_text(rel_path, wrap(_permalink(rel_path), body))
    return frame


# ---- the chain as files ------------------------------------------------------------------------------------------

def frame_index(sid: str, frames: Sequence) -> dict:
    """The optional rapp-frame-index/1 discovery index rapp_check.py reads (it confers no trust): the stream, every
    frame's path relative to the index, and the head."""
    if not frames:
        raise Refused("a frame index names at least one frame")
    return {"schema": "rapp-frame-index/1", "stream_id": sid,
            "frames": [f"versions/{vid}/pulse.json" for _, vid in frames],
            "head": {"seq": frames[-1][0]["seq"], "frame_hash": frames[-1][0]["frame_hash"]}}


def chain_files(sid: str, record: Mapping, frames: Sequence, checker) -> dict[str, str]:
    """The chain as Hive files: the identity record, the discovery index and every pulse, each wrapped so GitHub
    Pages serves it as JSON at /portfolio/<path>."""
    reference = _reference(checker)
    if record.get("rappid") != sid:
        raise Refused(f"the identity record names {record.get('rappid')!r}, not {sid}")
    vids = [vid for _, vid in frames]
    if len(set(vids)) != len(vids) or any(f.get("stream_id") != sid or version_id(f) != vid for f, vid in frames):
        raise Refused("every pulse sits once in the folder its utc and seq name, on this stream")
    out = {f"{IDENTITY}.md": wrap(f"/{PORTFOLIO}/{IDENTITY}", pretty(record)),
           f"{INDEX_NAME}.md": wrap(f"/{PORTFOLIO}/{INDEX_NAME}", pretty(frame_index(sid, frames)))}
    for frame, vid in frames:
        out[pulse_path(vid)] = wrap(_permalink(pulse_path(vid)), reference.canonical(frame) + "\n")
    for rel_path, text in out.items():
        check_hive_path(rel_path)
        check_hive_text(rel_path, text)
    return out


# ---- rapp-1's own checker on the chain and on the public copy -------------------------------------------------------

def check_chain(chain: Mapping[str, str], checker) -> dict:
    """rapp-1's own rapp_check.py on the chain alone, as GitHub Pages serves it: COMPLIANT, every pulse passing, no
    finding at all. Refuses otherwise."""
    _at_pin(str(Path(checker).resolve()))
    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch) / "chain"
        try:
            materialize(chain, root)
        except Refused as error:
            raise SystemExit(f"the chain holds a file Pages would serve outside it: {error}")
        result = pinned.rapp_check(root, checker)
    frames = [e for e in result.get("evidence", []) if e.get("ok") == FRAME_EVIDENCE]
    pulses = sum(1 for name in chain if name.endswith("pulse.json.md"))
    if result.get("verdict") != "COMPLIANT" or result.get("findings") or len(frames) != pulses:
        raise SystemExit(f"rapp_check.py refused the chain: {result.get('verdict')}, "
                         f"{len(result.get('findings') or [])} finding(s): "
                         f"{json.dumps(result.get('findings'), ensure_ascii=False)[:600]}")
    return {"verdict": result["verdict"], "frames": len(frames), "evidence": len(result.get("evidence", []))}


def _chain_file(rel_path: str) -> bool:
    """A chain file of the portfolio, as a path in the published room (shared/organism/)."""
    return (rel_path in (f"{PORTFOLIO}/{IDENTITY}.md", f"{PORTFOLIO}/{INDEX_NAME}.md")
            or re.fullmatch(f"{PORTFOLIO}/versions/[^/]+/pulse\\.json\\.md", rel_path) is not None)


def _certify(stored: Mapping[str, bytes], checker) -> tuple[dict, int]:
    """({files, served} facts, frames the served copy verified) for one would-be public copy."""
    out = {}
    with tempfile.TemporaryDirectory() as scratch:
        literal, pages = Path(scratch) / "literal", Path(scratch) / "served"
        literal.mkdir()
        pages.mkdir()
        texts = {}
        try:
            for rel_path, data in stored.items():
                inside(literal, rel_path).parent.mkdir(parents=True, exist_ok=True)
                inside(literal, rel_path).write_bytes(data)
                try:
                    texts[rel_path] = data.decode("utf-8")
                except UnicodeDecodeError:  # not text: Pages serves it as it is
                    inside(pages, rel_path).parent.mkdir(parents=True, exist_ok=True)
                    inside(pages, rel_path).write_bytes(data)
            materialize(texts, pages)
        except Refused as error:
            raise SystemExit(f"the would-be public copy holds a file Pages would serve outside it: {error}")
        results = {name: pinned.rapp_check(root, checker) for name, root in (("files", literal), ("served", pages))}
    for name, result in results.items():
        out[name] = {"verdict": result.get("verdict"), "findings": len(result.get("findings") or []),
                     "evidence": len(result.get("evidence") or []),
                     "certified": result.get("verdict") in ("COMPLIANT", "CLEAN") and not result.get("findings")}
    return out, sum(1 for e in results["served"].get("evidence") or [] if e.get("ok") == FRAME_EVIDENCE)


def certify_public(room_root, checker, chain: Mapping[str, str] | None = None) -> dict:
    """rapp_check.py on the would-be public copy (the published room, shared/organism/), twice: its files as stored
    (a Hive holds only markdown, so no RAPP artifact is visible there) and as GitHub Pages serves them (every wrapper
    unwrapped at its permalink, so every pulse is a JSON frame): {files|served: {verdict, findings, evidence,
    certified}}, certified meaning COMPLIANT or CLEAN with no finding.

    With `chain` (chain_files()), the room is certified with exactly those chain files under portfolio/ (whatever
    chain files it holds now are left out), and again without any: the facts add `pulses` (in the chain),
    `verified` (the pulses the served copy verified) and `without` (the {files, served} facts without the chain),
    which placement() needs to tell whether the pulses themselves would cost the certification."""
    room_root = Path(room_root)
    if not room_root.is_dir():
        raise SystemExit(f"{room_root}: no room to certify")
    _at_pin(str(Path(checker).resolve()))
    stored = {p.relative_to(room_root).as_posix(): p.read_bytes() for p in sorted(room_root.rglob("*"))
              if p.is_file() and ".git" not in p.relative_to(room_root).parts}
    if chain is None:
        return _certify(stored, checker)[0]
    without = {rel_path: data for rel_path, data in stored.items() if not _chain_file(rel_path)}
    facts, verified = _certify({**without, **{f"{PORTFOLIO}/{rel_path}": text.encode("utf-8")
                                              for rel_path, text in chain.items()}}, checker)
    return {**facts, "pulses": sum(1 for rel_path in chain if rel_path.endswith("pulse.json.md")),
            "verified": verified, "without": _certify(without, checker)[0]}


def placement(certify: Mapping) -> str:
    """Where the pulses live, from certify_public(room, checker, chain) facts:

    - "public" when rapp_check.py certifies the would-be public copy with the chain in it, as stored and as served,
      and the served copy verifies every pulse;
    - "private" when it certifies the copy only without the chain: the pulses themselves would cost the public copy
      its certification, so the chain files wait in the private room (shared/network-pulses/) and the timeline
      says so;
    - otherwise it refuses: the copy fails even without the pulses, and moving them would fix nothing.

    Facts without `without` (certify_public(room, checker) on a room the caller vouches holds the chain) give
    "public" when both copies are certified, else "private"."""
    def certified(facts) -> bool:
        return isinstance(facts, Mapping) and all(isinstance(facts.get(copy), Mapping)
                                                  and facts[copy].get("certified") is True
                                                  for copy in ("files", "served"))
    if "without" not in certify:
        return "public" if certified(certify) else "private"
    if certified(certify) and _uint(certify.get("pulses")) and certify.get("verified") == certify["pulses"]:
        return "public"
    if certified(certify["without"]):
        return "private"
    raise SystemExit("rapp_check.py does not certify the would-be public copy even without the pulses: fix the copy "
                     "first (moving the pulses to the private room would not restore its certification)")


# ---- reading the chain back ----------------------------------------------------------------------------------------

def pulse_changes(prev: Mapping, cur: Mapping) -> dict:
    """What changed from one pulse to the next, /1 or /2 (lifecycle.changes): status, lifecycle (with the notice),
    version and channel changes, member cards added or removed, repos added and left, how many others went, and how
    many moved commit."""
    return lifecycle.changes(prev["payload"], cur["payload"])


def pulse_diff(prev: Mapping, cur: Mapping) -> tuple[list, list, list, int]:
    """(status changes [(repo, before, after)], new repos, removed repos, repos at a new evidence commit), for /1
    and /2 pulses alike (a removed repo is any repo of the earlier pulse that the later one does not record as a
    station, including the ones that left; pulse_changes tells them apart)."""
    a, b = prev["payload"]["repos"], cur["payload"]["repos"]
    order = lambda name: (name.lower(), name)
    both = sorted(a.keys() & b.keys(), key=order)
    changes = [(n, a[n]["status"], b[n]["status"]) for n in both if a[n]["status"] != b[n]["status"]]
    moved = sum(1 for n in both if a[n].get("evidence_commit") != b[n].get("evidence_commit"))
    return changes, sorted(b.keys() - a.keys(), key=order), sorted(a.keys() - b.keys(), key=order), moved


def _stored(folder: Path, rel_path: str) -> str | None:
    path = folder / rel_path
    try:
        return path.read_text(encoding="utf-8") if path.is_file() else None
    except (OSError, ValueError):
        return None


def _artifact_body(name: str, path: Path) -> bytes | None:
    """The bytes a pulse hashed: PORTFOLIO.md (and NOTICES.md) as stored, a map as GitHub Pages serves its wrapper;
    None if absent."""
    try:
        return (path.read_bytes() if name in ("PORTFOLIO.md", "NOTICES.md")
                else served(path.name, path.read_text(encoding="utf-8")))
    except (OSError, ValueError, IndexError):
        return None


def verify(folder, checker, say: Callable[[str], None] = print, maps=None, known_head: Mapping | None = None,
           stream: str = NETWORK_STREAM) -> int:
    """Every pulse in a portfolio folder (the Hive room, a public copy or its portfolio/, or the private room with
    `maps` = the portfolio folder that holds the version maps): the chain from genesis (read_chain), its files as
    generated (identity record, discovery index), rapp_check.py on the chain, and each version's files against the
    hashes its pulse recorded (PORTFOLIO.md and the stable maps for the head; an older version's PORTFOLIO.md lives in
    the history of the copy it was published in). Any stream but `stream` (the network's) is refused. Prints each
    problem and a summary; 0 means no problems."""
    folder = Path(folder).expanduser().resolve()
    folder = folder / PORTFOLIO if (folder / PORTFOLIO / f"{IDENTITY}.md").is_file() else folder
    sid, record, frames = read_chain(folder, checker, known_head=known_head)
    if not frames:
        raise SystemExit(f"{folder}: no pulse chain here")
    if sid != stream:
        raise SystemExit(f"{folder}: the chain of {sid}, not of {stream}")
    maps = Path(maps).expanduser().resolve() if maps is not None else folder
    maps = maps / PORTFOLIO if (maps / PORTFOLIO / "PORTFOLIO.md").is_file() else maps
    try:
        want = chain_files(sid, record, frames, checker)
    except Refused as error:
        raise SystemExit(f"{folder}: a chain the Hive could not store ({error})")
    problems, stored = [], {rel_path: _stored(folder, rel_path) for rel_path in want}
    index = f"{INDEX_NAME}.md"
    if stored[index] is None:
        problems.append(f"{INDEX_NAME} is missing")
    elif stored[index] != want[index]:
        try:
            named = json.loads(unwrap(stored[index])) == frame_index(sid, frames)
        except (ValueError, IndexError):
            named = False
        problems.append(f"{INDEX_NAME} " + ("is not in its generated form" if named else
                                             "does not name exactly these frames and this head"))
    if stored[f"{IDENTITY}.md"] != want[f"{IDENTITY}.md"]:
        problems.append(f"{IDENTITY} is not in its generated form")
    try:  # the chain as generated from its verified frames: a stored file in another form is a problem above
        checked = check_chain({rel_path: want[rel_path] for rel_path, text in stored.items() if text is not None},
                              checker)
        verdict = f"rapp_check {checked['verdict']} ({checked['frames']} frame(s))"
    except SystemExit as refusal:
        problems.append(str(refusal))
        verdict = "rapp_check refused the chain"
    head = frames[-1][0]
    for frame, vid in frames:
        artifacts, names = frame["payload"].get("artifacts"), artifact_names(_schema(frame["payload"]) or 1)
        if not isinstance(artifacts, dict) or set(artifacts) != set(names):
            problems.append(f"versions/{vid}: its pulse records {sorted(artifacts or ())}, not {', '.join(names)}")
            continue
        pages = ("PORTFOLIO.md", "NOTICES.md")  # the head's, as stored; an older version's live in the history
        places = [(name, maps / name if name in pages else maps / "versions" / vid / f"{name}.md")
                  for name in names if name not in pages or frame is head]
        if frame is head:
            places += [(name, maps / f"{name}.md") for name in MAPS if name != "subway.html"]  # the stable copies
        for name, path in places:
            body, recorded = _artifact_body(name, path), artifacts[name]
            where, version = path.relative_to(maps).as_posix(), frame["payload"]["version"]
            if body is None:
                problems.append(f"{where}: missing (the version {version} pulse records its {name})")
            elif (not isinstance(recorded, dict) or sha256(body) != recorded.get("sha256")
                  or len(body) != recorded.get("bytes")):
                problems.append(f"{where}: differs from the {name} the version {version} pulse records")
    for problem in problems:
        say(f"problem: {problem}")
    say(f"stream {sid}: {len(frames)} pulse(s) verified from genesis (§7.5 steps 1-5); {verdict}; head version "
        f"{head['payload']['version']} payload_hash {head['payload_hash']}; "
        f"{'no problems' if not problems else f'{len(problems)} problem(s)'}")
    return 1 if problems else 0
`````
{% endraw %}
