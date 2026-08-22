# rapp-monorepo

**Every public RAPP repository, in one place, captured in a single pass.**

Clone this one repo and you have the whole estate as it stood at the last
snapshot — no drift between the pieces, because they were all taken together
and each one records the exact commit it came from.

```bash
git clone --depth 1 https://github.com/kody-w/rapp-monorepo.git
```

Then read [`INDEX.md`](INDEX.md) for the table of contents, or
[`MANIFEST.json`](MANIFEST.json) if you want it machine-readable.

---

## Why this exists

The RAPP estate is spread across ~190 public repositories. Reading it one
repo at a time means every piece you hold is from a different moment, and the
seams between them drift while you work. This repo removes that problem in
the only way that actually works: capture everything at once, write down what
you captured, and refresh it on a schedule.

The test it is built to pass: *one download, no network afterwards, no
drift.*

---

## What is in here

- `repos/<name>/` — the working tree of each public RAPP repository at HEAD
- `MANIFEST.json` — per repo: the commit sha, the upstream commit date, the
  capture time, file and byte counts, and everything omitted
- `INDEX.md` — the same thing as a table you can read

Membership is a **name pattern**, resolved at run time: a public,
non-archived repo whose name starts with `rapp`, `rappter`, `openrappter`,
`RAR`, `twin`, `brainstem` or `wildhaven` is a member. Nothing is listed by
hand, so a new repo joins by existing and a repo that goes private leaves on
the next run — including having its directory deleted from this snapshot.

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
result. To run it yourself:

```bash
export RAPP_GATE_RULES='{"content":["..."],"paths":["..."]}'   # or ./.gate-rules
python3 prove_gate.py
python3 prove_aggregate.py
python3 aggregate.py --dry-run     # enumerate members, write nothing
python3 aggregate.py               # capture
```

---

## Honest limits

- A snapshot is **as of** its timestamp. `MANIFEST.json` says when; nothing
  here claims to be live.
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
aggregation tooling itself (`aggregate.py`, `ip_gate.py`) is MIT.
