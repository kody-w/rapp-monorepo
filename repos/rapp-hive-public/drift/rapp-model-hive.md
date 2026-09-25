---
repo: kody-w/rapp-model-hive
commit: 83e039f58486afb529b1036087c03e9808a564ca
checked_with: kody-w/rapp-1 rapp_check.py at 591e014
verdict: DRIFT
brought_from: estate-sweep/rapp-model-hive.md
brought_sha256: 3cb9c6a8cc0072ff25d7a98dcefe6980f0e5daa6111f45a0a868dc50ff9cdd85
---

# rapp-model-hive: DRIFT

Swept at commit `83e039f584` with rapp-1's own linter, outside the Hive. The raw output is `rapp-model-hive.json` in the same sweep folder; its SHA-256 is `ca04ebc2e0f233ca9ab0e76d56c67ac2340e36fd718f8b351d1174ae55f303e4`.

## Findings (35)

- `model/hive/streams/avery-laptop.hive.121f71337e33/00000000.json` · §10 signature verification unavailable · detached signature was not checked because no trusted verifier/anchor was supplied (unverified)
- `model/hive/streams/avery-laptop.hive.121f71337e33/00000001.json` · §10 signature verification unavailable · detached signature was not checked because no trusted verifier/anchor was supplied (unverified)
- `model/hive/streams/avery-laptop.hive.121f71337e33/00000002.json` · §10 signature verification unavailable · detached signature was not checked because no trusted verifier/anchor was supplied (unverified)
- `model/hive/streams/avery-laptop.hive.121f71337e33/00000003.json` · §10 signature verification unavailable · detached signature was not checked because no trusted verifier/anchor was supplied (unverified)
- `model/hive/streams/avery-laptop.hive.121f71337e33/00000004.json` · §10 signature verification unavailable · detached signature was not checked because no trusted verifier/anchor was supplied (unverified)
- `model/hive/streams/avery-laptop.hive.121f71337e33/00000005.json` · §10 signature verification unavailable · detached signature was not checked because no trusted verifier/anchor was supplied (unverified)
- `model/hive/streams/avery-laptop.hive.121f71337e33/00000006.json` · §10 signature verification unavailable · detached signature was not checked because no trusted verifier/anchor was supplied (unverified)
- `model/hive/streams/avery-laptop.hive.121f71337e33/00000007.json` · §10 signature verification unavailable · detached signature was not checked because no trusted verifier/anchor was supplied (unverified)
- `model/hive/streams/avery-laptop.hive.121f71337e33/00000008.json` · §10 signature verification unavailable · detached signature was not checked because no trusted verifier/anchor was supplied (unverified)
- `model/hive/streams/avery-laptop.hive.121f71337e33/00000009.json` · §10 signature verification unavailable · detached signature was not checked because no trusted verifier/anchor was supplied (unverified)
- `model/hive/streams/avery-laptop.manifest.121f71337e33/00000000.json` · §10 signature verification unavailable · detached signature was not checked because no trusted verifier/anchor was supplied (unverified)
- `model/before/streams/avery-laptop.tasks.121f71337e33/00000000.json, model/hive/streams/avery-laptop.tasks.121f71337e33/00000000.json` · §7.6 duplicate position · stream rappid:@contoso/avery-laptop:121f71337e335720c65dc4f7b459c92aea6197460224401810721765fabea47b:tasks has 2 frames at seq 0
- … and 23 more in the raw output

## Declared pins

- none found
