# House kit (vertical frame)

The studio's default look for 1080x1920 shorts. `tokens.json` is the
machine-readable twin of this page and wins if the two disagree. Load it by
name in every production so prompts never re-describe the look.

## Type

Inter 700 for hooks and captions, Inter 400 for labels, EB Garamond 400 for
the small editorial kicker, JetBrains Mono for anything typed. All three are
OFL-licensed: download them from their official sources into the production's
`assets/fonts/` with their licence files.

## Colour

| Token | Hex | Use |
|---|---|---|
| ink | #0B0B0F | dark panels, caption shadow |
| paper | #F7F5F0 | caption text, light windows |
| signal | #5B4BFF | the active caption word, highlights |
| pulse | #00D1B2 | success states (101, done), one accent per beat |
| warn | #FF5A36 | the one thing that went wrong; never decorative |
| muted | #9A98A6 | secondary labels |
| panel / line | #16161D / #2A2A35 | dark card fill and hairline |

## Zones (x, y, w, h in pixels)

| Zone | Box | Use |
|---|---|---|
| face | 240, 300, 600, 700 | keep-out: nothing covers the face (or the source card) |
| top | 60, 80, 960, 200 | hook card, kicker |
| caption | 90, 1040, 840, 200 | captions by default |
| lower | 60, 1250, 870, 380 | panels, typing windows, lower thirds |
| left / right | 40 or 860, 330, 180, 550 | small badges only |

Platform-safe: no words below y 1640 and none in the right rail (x 950 and
up, y 900 to 1640), where the short-video platforms draw their own UI.

## Captions

One to four words per phrase, no punctuation, sentence case, at most two
lines, one phrase at a time, the spoken word highlighted in signal.

## Motion

Arrive with purpose (power3.out, 0.35 to 0.6 s), settle, hold at least 1.2 s
per short line, leave faster (power2.in). No bounces, spins, elastic moves or
rainbow gradients.
