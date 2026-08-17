# Credentials — two keys, two owners

Give a program a credential and the risk is that the program misuses it. That
risk is old, and the industry has good answers: scope it, rotate it, audit it.

Give an **AI agent** a credential and something new happens. The moment the
agent *reads* the value, it is in the model's context window. It is transmitted
to a model provider. It lands in a transcript. It may be retained, and it may be
reproduced later into a file, a log, or a pull request.

None of that requires malice. It is the ordinary, correct operation of the
system. But the outcome is indistinguishable from disclosure, and neither
scoping nor rotation prevents it — because the leak happens at the moment of
*reading*, the one operation every traditional secret manager treats as safe.

**Traditional secret managers assume retrieval is the safe half and storage is
the risky half. For agents, that is inverted.**

## Use without sight

The primary interface is not "give me the secret." It is **"run this command
with the secret injected."**

```bash
rapp-keyring run --grant azure/storage-key -- ./deploy.sh
```

The value lands in the child's environment. It is never returned to the caller.
Everything the child prints is scanned on the way out, including re-encoded
forms — base64, hex, URL-encoded, JSON-escaped — because a leak rarely arrives
verbatim:

```console
$ rapp-keyring run --grant azure/storage-key -- sh -c 'echo "key is $AZURE_STORAGE_KEY"'
key is «redacted:azure/storage-key»
```

Reading a secret in the clear is still possible when a human genuinely needs it,
but it is a separate, policy-gated action requiring an explicit acknowledgement,
and it is recorded as a *sighted read* — a distinct event, precisely so it can be
asked about.

## The two keys

Inside an enterprise deployment, one broker is not enough:

```
   the machine  ──  RAPP Keyring  ──▸  which PROCESS may hold this secret
                                       owned by the user, on the device

   the estate   ──  the strain    ──▸  which AGENT may cause it to be used
                                       owned by the administrator, in sealed policy
```

Neither is sufficient alone. Keyring cannot see inside the brainstem — every
agent there is one caller, one process — so it cannot tell the deploy agent from
the note-taking agent. The strain can, because it identifies agents by the
sha256 of their bytes.

And the strain must never hold a value, because a policy manifest is a file that
gets copied, mailed, committed and screenshotted. The day it contains a secret
is the day the control becomes the leak.

**The strain holds grants; Keyring holds values.**

## The identity check does double duty

A grant is recorded against a sha256, so an agent cannot acquire a credential by
being edited after approval:

```console
$ strainctl cred check deploy_agent.py azure/storage-key
  DENY   deploy_agent.py → azure/storage-key
         deploy_agent.py has changed since it was approved — its grants
         do not apply until it is re-approved
```

## What is enforced, and what is only recorded

**Enforced.** The set of secrets reachable from a machine under a strain is
bounded by the manifest, and the bound is sealed. A manifest whose seal does not
verify grants nothing. A refused credential means the command never runs at all.

**Recorded, not enforced.** *Which* approved agent claimed to be acting, within
one brainstem process. Separating agents by process would need OS support the
design deliberately does not require. Likewise, a broker's caller identity is
derived from process ancestry — anything running as your user can claim to be
anything.

Policy therefore makes over-reach **visible, auditable and inconvenient**. It is
not a boundary against a local adversary, and it does not pretend to be.

## Where it lives

- [kody-w/rapp-keyring](https://github.com/kody-w/rapp-keyring) — the broker.
  Stdlib only, zero network, tamper-evident audit, 12 conformance checks.
- [kody-w/rapp-light](https://github.com/kody-w/rapp-light) — the estate half,
  as check 6 of an enterprise strain.
