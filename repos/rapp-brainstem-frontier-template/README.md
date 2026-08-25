# RAPP Brainstem Frontier — Template

**The grail Electron template.** This is the reference starting point the whole
ecosystem can point at: grab it, and any repo becomes a Frontier estate: the grail
Brainstem by reference, the Frontier Electron shell by reference, ambient mode
on the mic, and a **rapplication skin** — your own UI injected OVER the
factory chat, never instead of it.

```bash
# the whole package — grail Brainstem + this template + Frontier shell — in one pull:
curl -sSfL https://raw.githubusercontent.com/kody-w/rapp-brainstem-frontier-template/main/scripts/bootstrap.sh | bash
```

Or piece by piece from a checkout:

```bash
./scripts/start.sh          # installs the Brainstem if absent, launches Frontier
./scripts/install-skin.sh   # lands rapp_ui/example-skin into the running kernel
./scripts/revert-skin.sh    # removes it — the factory chat was never touched
```

## What you get

- **The grail Brainstem, by reference.** `start.sh` installs it with the public
  one-liner if `~/.brainstem` is absent. Grail code is never vendored here.
- **The Frontier shell, by reference.** The rappid flavor
  ([`kody-w/aibast-agents-library`](https://github.com/kody-w/aibast-agents-library),
  branch `feat/rappid-first-ui`, `beta/`) — one mode besides chat: **ambient
  mode**, built on voice mode (continuous conversation, spoken replies, a live
  screen + webcam frame on every message, senses that only downgrade).
- **A skin, not a fork of the chat.** Your UI lives in `rapp_ui/<skin-id>/`
  and installs into the kernel's `.brainstem_data/rapp_ui/<skin-id>/`. The
  factory grail chat grows a small **rapplications dock**; opening your skin
  overlays it in an iframe served from `/rapp_ui/<skin-id>/`. Close the
  overlay — or delete the directory — and the factory chat is exactly as it
  was. A broken skin can never take the chat down with it.

## The skin contract

```
rapp_ui/<skin-id>/
  index.html        # your UI — served same-origin at /rapp_ui/<skin-id>/
  .manifest.json    # { "name": "...", "rappid": "...", "agent_filename": "..." }
  ...assets         # anything else your UI needs, same directory only
```

- The kernel serves ONLY `.brainstem_data/rapp_ui/` — path-traversal is
  refused, and nothing else in the tree is ever exposed.
- Your skin speaks to the same kernel the factory chat uses: `POST /chat`
  (`{user_input, session_id?}`) for conversation, `POST /agents/invoke`
  (`{agent, args}`) to call an agent it names directly — the cartridge
  protocol, deterministic, no router in between.
- Theme freely: the skin is a whole page in an iframe, so a "theme" is just a
  skin whose UI happens to look like the chat.

## The rules (rapplication rules apply)

1. **Never overwrite the factory chat.** The skin overlays; the grail
   underneath must always be revertible by closing or deleting the skin.
2. **Grail and Frontier ride by reference** — install scripts and checkouts,
   never vendored copies of either.
3. **No secrets in the skin.** Skins are shareable by design; keys and
   customer data never enter `rapp_ui/`.
4. **One directory.** Everything the skin needs lives in its own
   `rapp_ui/<skin-id>/` — no reaching into the kernel tree.
5. **Prototype posture.** A template estate is a workbench, not a customer
   system; productionization is a separate, governed step.
