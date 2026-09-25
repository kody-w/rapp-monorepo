---
repo: kody-w/RAPP
commit: 8afc9733e20ccf7e579a58028c29ab9c207087fa
checked_with: kody-w/rapp-1 rapp_check.py at 591e014
verdict: DRIFT
brought_from: estate-sweep/rapp.md
brought_sha256: 050ae13f3d53bcb1b535822b2df67800c64274de64a0e7c484e05b47861e16d8
---

# RAPP: DRIFT

Swept at commit `8afc9733e2` with rapp-1's own linter, outside the Hive. The raw output is `rapp.json` in the same sweep folder; its SHA-256 is `717dfb4c96ffb882c8e44bb4c353a1e952348b678309375257c939ccb6b60ab8`.

## Findings (3)

- `cave/cubbies/kody-w/eggs/cubby-rapp-installer.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: ZIP local and central UTF-8 flags must match exactly)
- `cave/rapplications/rapp-installer/cubby-rapp-installer.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: ZIP local and central UTF-8 flags must match exactly)
- `pages/tutorials/commons.egg` · §9 egg · not a conformant rapp/1-egg (schema=rapp/1-egg; §10: invite verification requires estate_owner_rappid)

## Declared pins

- `KERNEL_PIN.json`: channel=lts, distro=RAPP (the reference distro), note=RAPP tracks the grail (kody-w/rapp-installer). P, spec=rapp-distro/1.0
