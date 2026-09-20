# rapp-lab-kit

Always-on infrastructure for a RAPP estate: an **installer proving ground** and a
**network-health monitor**, both running on a NAS, both driven from this repo.

This repo is a **template**, not a live Hive. Hatching it creates a new identity
and its own `world_id`; it never joins you to the estate it was cut from
(`rapp-hive/1` section 13). Bring your own authority channel — a private repo you
control — and keep the NAS as a projection of it.

## Why a separate always-on box

`exec-proof` says an installer must be proven on a machine that did **not** build
it. A NAS container is that machine: clean x86_64 Linux, always on, not a Mac,
and — on a home network — it reaches `pypi.org` directly with no corporate pip
proxy. That makes it a truer stranger test than Docker on a dev laptop.

## Parts

| Path | What |
| --- | --- |
| `nas/rapp-lab/lab.sh` | Installer matrix: ubuntu24.04-bare / ubuntu24.04-py / debian12, in parallel, PASS only on `EXIT=0` **and** a live `/version` answer |
| `nas/web/wifimon/` | Ingest, API and dashboard for Wi-Fi/network health |
| `probe/collect.py` | One lightweight sample: RF, Wi-Fi-hop jitter, internet, mesh-node health |
| `bin/deploy.sh` | Project repo → NAS, then verify by hash |
| `bin/nas-lab.sh` | Drive the lab from a workstation |
| `bin/build-installer.sh` | Rebuild the probe installer from `collect.py` |

## Quickstart

```sh
cp config.example.sh config.sh && $EDITOR config.sh   # your locators
ssh-copy-id -i ~/.ssh/id_ed25519.pub "$NAS_USER@$NAS_HOST"
./bin/deploy.sh                                       # projects + verifies
./bin/nas-lab.sh https://example.org/install.sh mylabel
```

Add a probe to any Mac **that is on Wi-Fi**:

```sh
curl -fsSL http://<nas>/wifimon/install.sh | bash
```

## Two rules worth keeping

**Probes must be wireless.** A wired host cannot see RF signal, channel, airtime,
or the jitter at a desk. The NAS stores; it cannot measure. The installer refuses
quietly-useless installs by checking this.

**The monitor must not cause what it measures.** `collect.py` never runs a
saturating transfer — roughly 50 pings and a few HTTP GETs per sample.

## Hive

See [HIVE.md](HIVE.md). Archetype: `open-source-infrastructure-foundation` from
[kody-w/hive-hub](https://github.com/kody-w/hive-hub).

**Not yet a conformant section 13 template egg.** A conformant template is packed
and signed under the RAPP/1 egg specification with a distinct template RAPPID.
This is the source tree it would be packed from; the packing and signing step is
still to do. Said plainly so nobody mistakes a repo for a verified egg.
