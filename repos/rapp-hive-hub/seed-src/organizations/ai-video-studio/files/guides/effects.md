# Effect catalogue

Each effect is one HyperFrames sub-composition (an overlay) placed in one
kit zone for one board beat. All of them follow the same rules:

- **Seek-safe**: one paused GSAP timeline registered on
  `window.__timelines["<id>"]`; state changes use `tl.set` or tweens at fixed
  times, never callbacks, timers, `Math.random` or `Date`. A full-length
  anchor tween (`tl.to({}, { duration: D }, 0)`) makes the timeline span the
  beat.
- **On brand**: colours and fonts come from the kit's CSS variables only.
- **Offline fonts**: every family you name needs a local `@font-face` (the kit's
  fonts in `assets/fonts/`), and fallbacks stay generic (`serif`, `sans-serif`,
  `monospace`). The HyperFrames CLI downloads any named family that has no
  local `@font-face` from Google Fonts at render time.
- **Placed**: the overlay's root element carries `data-zone="<zone>"` and is
  positioned inside that zone's box. Never the face zone or the platform-safe
  areas.
- **Readable**: arrive in 0.35 to 0.6 s, hold at least 1.2 s per short line,
  leave faster than you came.

| Effect | Use it for | Zone | Typical length |
|---|---|---|---|
| hook-card | the first line: kicker plus hook | top | 2.5 to 3.5 s |
| ui-panel | a real interface or response, rows settling in | lower | 3 to 6 s |
| typing-window | a request, command or chat typed at speaking pace | lower | 4 to 8 s |
| layer-scan | revealing how a design or screen is built | lower or top | 3 to 5 s |
| punch-in | emphasis on the speaker (a transform on the video, not an overlay) | video | 0.4 to 1.2 s |
| lower-third | who is speaking, or a source credit | lower | 2.5 to 4 s |
| stat-pop | one number that matters | left or right | 1.5 to 2.5 s |
| end-card | the payoff line and where to watch more | top and lower | 2 to 3 s |

## hook-card

Kicker (editorial font, muted) fades up; the hook (display font) rises 24 px
into place with `power3.out`; a thin signal rule draws under it. Exit is a
0.25 s fade. Keep the hook under eight words.

## ui-panel

A dark panel (ink or panel colour, hairline border, 24 to 36 px radius)
slides up 40 px and fades in. Rows arrive at the moments they are spoken;
each row's check mark scales from 0.6 to 1 and settles. A status pill (pulse
colour) lands last with a short glow. Build rows from data at the top of the
script so the copy is easy to change.

## typing-window

A window with three title-bar dots slides into empty space. Each line is a
set of character spans; typing is a sequence of `tl.set(span, { opacity: 1 })`
calls at fixed times, so any frame can be rendered alone. Pace: start at the
spoken cue, about 18 to 30 characters per second. A block cursor sits after
the last visible character (toggle it with `tl.set` at half-second steps).
Highlight tokens (for example header names) by switching their class to the
signal colour when spoken.

## layer-scan

A horizontal scan line (signal, 2 px, soft glow) sweeps top to bottom. As it
crosses each layer, a 2 px outline box draws around that layer (animate
`clip-path` or stroke dash offset). After the sweep, the layers separate by
8 to 16 px in a slow, eased swipe and settle.

## punch-in

Not an overlay: scale the video wrapper from 1 to 1.06 to 1.12 over 0.4 to
0.8 s with `power2.out`, hold, and ease back. Keep the face inside the face
zone at the peak scale. Use at most once every ten seconds.

## lower-third

Name or credit on a panel strip in the lower zone: strip wipes in from the
left (`clip-path: inset()`), text fades up 0.1 s later.

## stat-pop

One number in display type in a gutter, counting up only if the count itself
is true to the source; otherwise it simply pops in (scale 0.9 to 1).

## end-card

The payoff line in the top zone and a short "watch the full episode" line in
the lower zone; no logos over the face. Holds to the last frame.

## Board row

```
| b2 | 12.40 | 19.80 | lower | typing-window | GET /chat HTTP/1.1 ... | F02-L02 | refs/chat-window.svg |
```
