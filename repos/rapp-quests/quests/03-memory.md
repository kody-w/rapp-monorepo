# Quest 03 — Memory

**Goal:** a brainstem that remembers you tomorrow.

## 1. Tell it something

> "Remember that my favorite editor is vim and I demo on Tuesdays."

Watch for `AGENT CALLED MANAGEMEMORY` — the fact just landed in
`.brainstem_data/` on your disk, nowhere else.

## 2. Prove persistence

Click **Clear** (wipes the conversation), then ask:

> "What do you know about me?"

The ContextMemory agent injects your stored facts into the system prompt on
every request — the model "just knows".

## 3. Where it lives

```bash
ls ~/.brainstem/src/rapp_brainstem/.brainstem_data/
```

Local JSON. Yours. Back it up encrypted with
[rapp-vault](https://github.com/kody-w/rapp-vault) — one command, end-to-end
encrypted, wipe-proof.
