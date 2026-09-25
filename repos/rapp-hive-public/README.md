# The RAPP Hive: public copy

This is the public copy of the **RAPP Hive**: the RAPP project run as a Hive. It is experimental. Everything here was approved inside the Hive and copied out exactly, and `PUBLISHED.md` lists every file with its hash.

- `map/`: the organism, layers 0 to 6 bottom to top, the crossings, journeys, glossary and the text graph.
- `gaps/`: the gap register, one file per gap.
- `drift/`: one verdict per public estate repo, from rapp-1's own `rapp_check.py`.
- `canon/`: canonical pin files, each stamped with where it came from and its hash.

Check it yourself with the Hive agent from `kody-w/rapp-model-hive` (branch `experimental/hive-md`):

    python agents/hive_agent.py check-public <this folder>

The organism's source of truth is `organism/` in `kody-w/rapp-work` (branch `experimental/rapp-work-constitution`).
