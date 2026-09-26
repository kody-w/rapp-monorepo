# The RAPP Hive: public copy

<!-- rapp1:network-header:start -->
[![RAPP/1](https://kody-w.github.io/rapp-hive-public/portfolio/badges/rapp-hive-public.svg)](https://github.com/kody-w/rapp-hive-public/blob/main/portfolio/repos/rapp-hive-public.md) · **New to RAPP?** [Start here: get your Brainstem →](https://github.com/kody-w/rapp-installer#start-here)
<!-- rapp1:network-header:end -->

This is the public copy of the **RAPP Hive**: the RAPP project run as a Hive. It is experimental. Everything here was approved inside the Hive and copied out exactly, and `PUBLISHED.md` lists every file with its hash.

- `map/`: the organism, layers 0 to 6 bottom to top, the crossings, journeys, glossary and the text graph.
- `gaps/`: the gap register, one file per gap.
- `drift/`: one verdict per public estate repo, from rapp-1's own `rapp_check.py`.
- `canon/`: canonical pin files, each stamped with where it came from and its hash.
- `portfolio/`: every public RAPP repo's earned RAPP/1 status, one file per repo in `repos/`, the whole table in `PORTFOLIO.md`, the badges each repo's README shows, and the subway map of the network (https://kody-w.github.io/rapp-hive-public/portfolio/subway.html, poster: https://kody-w.github.io/rapp-hive-public/portfolio/subway.pdf). Every crawl is one RAPP/1 `body.pulse` frame; each version's maps stay under `versions/`, and the timeline (https://kody-w.github.io/rapp-hive-public/portfolio/timeline.html) lists them all. GitHub Pages serves them.

Check it yourself with the Hive agent from `kody-w/rapp-model-hive` (branch `experimental/hive-md`):

    python agents/hive_agent.py check-public <this folder>

The organism's source of truth is `organism/` in `kody-w/rapp-work` (branch `experimental/rapp-work-constitution`).
