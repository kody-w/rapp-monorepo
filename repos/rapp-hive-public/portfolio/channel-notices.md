# RAPP/1 channel notices

Open questions about a repo's release channel on the RAPP/1 network. The portfolio takes each repo's channel from the LTS pins it reads (`rapp1-lts` with a pin, `newest` without one), and a channel changes only when those pins change. A notice here changes nothing: it says what is open, and it is removed once the question is settled.

## rapp-mcp: `newest` in the portfolio, `rapp1-lts` under review (open since 2026-09-26)

- **The portfolio says `newest`.** In version 6, [rapp-mcp](repos/rapp-mcp.md) is certified at commit `a6bb38ece3` and on the `newest` channel. No LTS pin is known for it, so the network reads it at `HEAD`.
- **Under review:** a proposed LTS pin would put rapp-mcp on `rapp1-lts`. It is not final.
- **Next:** once the LTS pins are settled, the next crawl takes rapp-mcp's channel from them, and that crawl's pulse records any change. Until then the portfolio keeps `newest`, and this notice stays.

[Notices](https://kody-w.github.io/rapp-hive-public/portfolio/NOTICES.html) · [Portfolio](https://kody-w.github.io/rapp-hive-public/portfolio/PORTFOLIO.html) · [Timeline](https://kody-w.github.io/rapp-hive-public/portfolio/timeline.html)
