# RAPP Docs

> RAPP Docs is the documentation home for the RAPP platform — the Brainstem engine, the Rings release train, Twins, and the SDK.

Canonical reference for the RAPP ecosystem.

---

Part of the **RAPP** platform — the Rapid Agent Prototype Platform.
Explore the ecosystem: [Installer](https://github.com/kody-w/rapp-installer) ·
[Flight Deck](https://github.com/kody-w/rapp-flight-deck) ·
[Rings](https://github.com/kody-w/rapp-rings) ·
[Twin](https://github.com/kody-w/rapp-twin)

## Contents

| | |
|---|---|
| **[The agent contract](docs/agent-contract.md)** | `rapp-agent/1.0` — one file, a manifest, and capabilities that are verified rather than trusted |
| **[Enterprise](docs/enterprise.md)** | governing the kernel without forking it: strains, the six checks, rings, and elevation as a credential |
| **[Credentials](docs/credentials.md)** | why an agent may *use* a secret but never *see* one, and the two-key model that makes it governable |
| **[Conformance](docs/conformance.md)** | why every RAPP repo ships a gate that proves its own README against its own code |
| **[Marks](docs/marks.md)** | open code, owned names — what is claimed, what is deliberately not, and why integration is the license |

## The ecosystem

| Repo | What it is |
|---|---|
| [rapp-1](https://github.com/kody-w/rapp-1) | the protocol suite — identity, canonicalization, the frame, the egg |
| [rapp-installer](https://github.com/kody-w/rapp-installer) | the grail brainstem everyone runs |
| [openrappter](https://github.com/kody-w/openrappter) | a full organism built on RAPP |
| [rapp-light](https://github.com/kody-w/rapp-light) | the enterprise strain — governance without a fork |
| [rapp-keyring](https://github.com/kody-w/rapp-keyring) | the credential broker — use without sight |
| [rapp-flight-deck](https://github.com/kody-w/rapp-flight-deck) | install any pre-release ring from one page |

## Status

Early, and actively being built out. Interfaces will move.

Where a document describes a property, that property has a conformance check or
a named test in the repo that implements it. Where it does not, the document
says so.

## License

MIT — see [LICENSE](LICENSE).

---

<sub>RAPP is a trademark of Wildhaven Homes LLC. Code is MIT licensed; the license does not grant rights to the name. [Trademark notice](TRADEMARK.md)</sub>
