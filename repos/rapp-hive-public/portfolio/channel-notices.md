# RAPP/1 channel notices

Questions and decisions about a repo's release channel on the RAPP/1 network. The portfolio takes each repo's channel from the LTS pins it reads (`rapp1-lts` with a pin, `newest` without one), and a channel changes only when those pins change. A notice here records the decision path; the next crawl's pulse records any channel change.

## rapp-mcp: resolved as `rapp1-lts` (decided 2026-09-26)

- **Decision:** WS-G (estate kit) ruled that `rapp-mcp` is `rapp1-lts`; the RAPP/1 LTS lock-in wins over the earlier portfolio `newest` row.
- **Portfolio source updated:** [rapp-mcp](repos/rapp-mcp.md) now carries the built-in LTS pin `cd22b1e964aabc6a71b8b401deb19d2de1f77086` and channel `rapp1-lts`.
- **Next:** the next real crawl/cut (v8) will show the channel change in the pulse timeline and report this decision.

[Notices](https://kody-w.github.io/rapp-hive-public/portfolio/NOTICES.html) · [Portfolio](https://kody-w.github.io/rapp-hive-public/portfolio/PORTFOLIO.html) · [Timeline](https://kody-w.github.io/rapp-hive-public/portfolio/timeline.html)
