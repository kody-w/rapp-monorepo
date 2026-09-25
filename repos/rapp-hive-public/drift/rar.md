---
repo: kody-w/RAR
commit: 30fe6b59c71afa2905ee4c4b2445d9fac643e511
checked_with: kody-w/rapp-1 rapp_check.py at 591e014
verdict: DRIFT
brought_from: estate-sweep/rar.md
brought_sha256: 20450ac0f8c0e22d9a33987169d9801c9e684025c37f2634a29abcc9739ecdd2
---

# RAR: DRIFT

Swept at commit `30fe6b59c7` with rapp-1's own linter, outside the Hive. The raw output is `rar.json` in the same sweep folder; its SHA-256 is `a9b0d3583b30c89a05aafc7f3f2a84a479193db4548e407d046c8662544ebc04`.

## Findings (3)

- `.` · verification unavailable · bounded frame discovery JSON budget exhausted (unverified)
- `stacks/microsoft-365-team/microsoft-365-team.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: ZIP local and central UTF-8 flags must match exactly)
- `stacks/neighborhood-starter/neighborhood-starter.egg` · §9 egg · not a conformant rapp/1-egg (schema=?; parse: ZIP local and central UTF-8 flags must match exactly)

## Declared pins

- none found
