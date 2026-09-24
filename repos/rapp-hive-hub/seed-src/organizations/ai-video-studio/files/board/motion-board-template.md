# Motion board: <production>

Written in plan mode before anything is built. The Showrunner approves this
file by its sha256; after approval, changes need a new approval.

## Header

- Production: <slug>
- Source: <clip or episode @ commit>, windows <from-to, from-to>
- Output: 1080x1920, 30 fps, <duration> s
- Brand kit: <name>
- Hook (0 to 3 s): <the line and the overlay that carries it>

## Cuts

| # | Source from | Source to | Timeline from | Why |
|---|---|---|---|---|
| 1 | 0.30 | 16.39 | 0.00 | <reason> |

## Beats

One row per overlay. Times are on the output timeline. Every technical
statement cites a claim key, or it does not go on screen.

| Beat | From | To | Zone | Effect | On-screen words | Claim | Notes |
|---|---|---|---|---|---|---|---|
| hook | 0.00 | 3.00 | top | hook-card | <words> | - | <placement> |
| b1 | 3.20 | 7.80 | lower | ui-panel | <words> | F01-L02 | <reference image> |

Effects come from the catalogue in guides/effects.md: hook-card, ui-panel,
typing-window, layer-scan, punch-in, lower-third, stat-pop, end-card.

## Captions

- Style: <kit caption style>
- Default zone: caption zone. Moves: <beat -> zone, when an overlay owns the space>

## Open questions for the Showrunner

- <anything the board could not decide>
