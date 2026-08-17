<div align="center">

# ✦ RAPPDEX

**Open the RAPP map wherever you are.**

`mapp` · one map, one opener, every surface

[Open the dex →](https://kody-w.github.io/rapp-mapp/)

</div>

---

```bash
curl -fsSL https://raw.githubusercontent.com/kody-w/rapp-mapp/main/mapp -o mapp && chmod +x mapp

./mapp                    # the dex, in this terminal
./mapp twin               # look something up
./mapp --layer membrane   # everything on one layer
./mapp --words            # the Nine Words and the membrane
./mapp --open             # open it in a browser
./mapp --json             # pipe it somewhere
```

Run it from a clone and it reads the map beside it. Run it from anywhere else
and it fetches the published one. Either way the same dex opens — which is what
makes it universal.

## It is a map, not a registry

It confers no trust, establishes no owner acceptance, and **must not** be
consumed as a RAPP/1 §13 authenticated registry. The protocol authority is
[`kody-w/rapp-1`](https://github.com/kody-w/rapp-1); the governance authority is
[`kody-w/RAPP/CONSTITUTION.md`](https://github.com/kody-w/RAPP/blob/main/CONSTITUTION.md).
Where this map and either authority disagree, **the authority wins and this map
is the defect**.

## Why it supersedes `rapp-map`

Two drifts at once, and the second is what made the original unusable.

**It drifted toward authority it never had.** Its `ecosystem-spec.json` carries
`disposition: quarantined-candidate`, `accepted_as_rapp1_registry: false`, and
the instruction to *refuse this document as an authenticated RAPP/1 registry*.

**It drifted in vocabulary.** Measured across its own files:

| word | old map | should be |
|---|---:|---|
| `hatch` | 544 | eggs only (Art. L) — an organism is **planted** |
| `plant` | 277 | the verb for an organism (Lexicon word 3) |
| `membrane` | 5 | word 5 — the split *every* organism has |
| `DOG` | 4 | the bones walking |

A map whose words disagree with the Lexicon cannot route anyone correctly.

**Superseding is not deleting.** `rapp-map`'s committed evidence stays exactly
where it is; this is a new surface, not a rewrite of an old one.

## The words it uses

From [the Lexicon](https://github.com/kody-w/RAPP/blob/main/LEXICON.md) — the Nine Words:

- An **organism** is a planted being (word 3). The verb is **plant**. *Hatch* belongs to eggs.
- The **membrane** splits every organism exactly once (word 5): **bones** public, **vault** private.
- The **DOG** is the bones walking. The **GOD** is bones + vault — the whole that *contains* the DOG.
- A **twin** is not an organism (Art. XLIX); it is a persistent AI presence.
- A **rappid** is identity (word 4). A name is never identity — only a hash is.

`tests/vocab-check.py` fetches the Lexicon from the authority and fails if this
map's words stop agreeing with it, or if any mapped surface 404s. A map that
points at a repo that does not exist is the exact defect Article LVI.9 records.

```bash
python3 tests/vocab-check.py
```

## Open gaps, recorded rather than hidden

The Article LVI surfaces are absent from `rapp-spine`'s crawl graph. They were
deliberately **not** self-registered: writing into a quarantined registry and
calling it alignment would be the same false-authority claim that retired
`rapp-frame-net`. A §13 entry needs estate-owner acceptance and signing
authority. Until then this is **canon that is not yet routable** — true, and not
yet findable by a crawl.
