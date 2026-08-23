# rapp-monorepo

**The complete declared public RAPP organism, assembled in one place at one
moment under a machine-recorded scope boundary.**

Clone this one repo and you have the whole estate as it stood at the last
snapshot — no drift between the pieces, because they were all taken together
and each one records the exact commit it came from.

```bash
git clone --depth 1 https://github.com/kody-w/rapp-monorepo.git
```

Start with [`ARCHITECTURE.md`](ARCHITECTURE.md) for the whole-organism model,
[`SDK.md`](SDK.md) for the standard SDK, [`INDEX.md`](INDEX.md) for the
captured anatomy, or [`MANIFEST.json`](MANIFEST.json) for the machine-readable
specimen.

---

## Why this exists

RAPP is not one application or one repository. It is a federated organism of
protocols, runtimes, registries, stateful worlds, distribution channels,
operator surfaces, and observability systems. Reading those organs one repo at
a time means every piece you hold is from a different moment, and the seams
between them drift while you work. This repository supplies the missing
whole-body view: capture the defined public estate at once, pin every organ to
its upstream commit, and refresh the specimen on a schedule.

The test it is built to pass: *one download, no network afterwards, no
drift.*

This snapshot is evidence, not authority. It does not replace the source
repositories, the RAPP/1 protocol authority, a registry trust root, or a
running brainstem.

---

## What is in here

- `repos/<name>/` — the working tree of each public RAPP repository at HEAD
- `MANIFEST.json` — per repo: the commit sha, the upstream commit date, the
  capture time, file and byte counts, a staged-tree SHA-256, and everything
  deliberately omitted
- `INDEX.md` — the same thing as a table you can read
- `ORGANISM.json` — the machine-readable estate scope and deliberate
  exclusions, body-system taxonomy, authority boundaries, Map/Spine projection
  evidence, relationships, and known conflicts
- `rapp_sdk/` — the installable RAPP/1 protocol and whole-organism SDK
- `architecture/rapp-organism.excalidraw` — the editable full-body diagram

Candidate membership is the exact **name pattern** recorded in
`ORGANISM.json`, resolved at run time: a public, non-archived repo whose name
starts with `rapp`, `rappter`, `openrappter`, `twin`, `brainstem` or
`wildhaven` enters the candidate set; `RAR` itself is also included, but
`RAR-*` names are not. The machine-readable
`estate_scope.deliberate_exclusions` is then applied. At this snapshot, the
predicate selected 199 repositories and two deliberate exclusions produced
the 197-organ specimen:

- `kody-w/rapp-monorepo` — excluded to prevent recursive self-capture;
- `kody-w/rapp-shape-aibast` — excluded because it rehearses delivery into an
  external AIBAST library layout and is not a RAPP organism organ.

A new matching repo joins automatically unless a reviewed exclusion record
names it with a reason. A repo that goes private leaves on the next run,
including having its directory deleted from this snapshot.

## Standard SDK

The root SDK turns the specimen into a safe, typed development surface without
importing or executing captured code:

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/rapp-sdk --root "$PWD" status
.venv/bin/rapp-sdk --root "$PWD" alignment
```

It provides strict RAPP/1 canonicalization, hashes, identities, frames, eggs,
detached JWS, signed registry verification, persistent head/registry state,
the exact `/chat` client, organism inventory, and no-follow specimen access.
`kody-w/rapp-1` is the normative protocol source. The `RAPP` public product is
retired, while its target status record remains current evidence with a
drifted structural pin. Map and Spine are modeled separately so none can
silently redefine the standard.

Full authenticated conformance remains false until the estate owner publishes
the signed section-13 registry and distributes its self-certifying anchor out
of band. The SDK reports that blocker rather than manufacturing trust. See
[`SDK.md`](SDK.md) for the API and conformance matrix.

## What is deliberately NOT in here

**History.** Every member is captured at HEAD. This is a snapshot of the
estate, not a backup of its git. Each row in the manifest carries the commit
sha, so anything here can be traced back and re-cloned in full.

**Anything private.** This mirror only ever reads PUBLIC repositories, and
visibility is checked at run time rather than trusted from a list. On top of
that, every single file passes a gate before it is written — see below.

**Large files**, over the per-file limit (2MB by default). A copy you can
actually carry is worth more than a complete one you cannot. Every skipped
file is named in `INDEX.md`.

---

## The gate

A mirror of everything would also mirror a mistake — into a second public
location, with its own history, where undoing it is harder than at the
source. So `ip_gate.py` screens every file on the way in, and it is built on
three rules:

1. **Withhold, never rewrite.** A flagged file is left out whole and named,
   rather than edited. This mirror's promise is *what you have is what
   upstream has*; a quietly rewritten file breaks that in the one place a
   reader would never think to check. Partial redaction is also how sensitive
   content survives — you fix the sentence you thought of and ship the
   paragraph you did not.
2. **Name the rule, never the match.** The manifest says which rule withheld
   a file. It does not quote the text, because a report that quotes a finding
   republishes it.
3. **Fail closed.** The screening rules are injected at run time (a CI
   secret, or an untracked local file) and are never committed — a committed
   list of the exact strings being suppressed is a better search index than
   the content it suppresses. If the rules are missing, aggregation
   **refuses to run**. A gate that is not configured screens nothing while
   reporting success, which is worse than no gate at all: it launders
   unscreened content through a step that looks like diligence.

The structural rules — never publish a `.env`, a private key, a
`local.settings.json`, anything shaped like a token — ship in the open on
purpose. Those describe shapes, not secrets, and having them here means a
fresh clone is safe before anything is configured.

---

## Refreshing it

`.github/workflows/aggregate.yml` runs the capture daily and commits the
result. Before committing, it raw-stages only `repos/`, `MANIFEST.json`, and
`INDEX.md`, then proves that every staged path, mode, byte count, and blob
matches the manifest's `rapp-monorepo-staged-tree/1.0` integrity profile. It
also regenerates `INDEX.md` from the manifest and compares exact bytes. This
prevents a copied repository's `.gitignore` or `.gitattributes` from silently
changing the published snapshot.

To run it yourself:

```bash
export RAPP_GATE_RULES='{"content":["..."],"paths":["..."]}'   # or ./.gate-rules
python3 prove_gate.py
python3 prove_aggregate.py
python3 prove_snapshot.py
python3 aggregate.py --dry-run     # enumerate members, write nothing
python3 aggregate.py               # capture
python3 verify_snapshot.py --stage # stage and prove the publishable tree
```

---

## Honest limits

- A snapshot is **as of** its timestamp. `MANIFEST.json` says when; nothing
  here claims to be live.
- "Complete" means complete under `ORGANISM.json`'s candidate membership rule
  and explicit exclusions; an exclusion is never a silent omission.
- Withheld and skipped files are listed, but the listing is the only evidence
  of them — this repo cannot show you what it decided not to carry.
- The gate screens the files it is given. It cannot screen a repository that
  failed to clone, and any member not captured is named in `INDEX.md` rather
  than quietly missing.
- Some members are themselves mirrors of others. Where two copies disagree,
  the manifest's per-repo commit shas are what let you tell which is which.

## License

Each `repos/<name>/` directory keeps whatever license its source repository
ships. Nothing here relicenses anything — check the individual repo. The
aggregation tooling itself (`aggregate.py`, `ip_gate.py`) is MIT. The root SDK
is separately covered by [`SDK_LICENSE`](SDK_LICENSE).
