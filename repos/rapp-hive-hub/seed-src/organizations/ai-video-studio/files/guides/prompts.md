# Prompt library

The studio's own prompts, written to be spoken as well as typed. Replace the
angle brackets. Every prompt assumes the production folder is open and the
kit is loaded by name.

## What makes an effect prompt work

- **Anchor it to the words.** Quote the spoken cue that starts the effect
  ("when the speaker says 'asks to upgrade'") instead of guessing seconds;
  the transcript turns the quote into exact timing.
- **Name the reference.** Point at the reference image file for the look.
- **Say how it moves.** Two or three motion words (slides in, settles, types
  at speaking pace) beat a paragraph of adjectives.
- **Fence the frame.** Never the face, clear of the frame edges and the
  platform UI, one overlay per zone.
- **Nothing extra.** Say what must not be added or changed.

## 1. Intake (to your AI)

> New short. Source is <clip path, or episode and window>. Audience is
> <who>, platform is <where>, about <n> seconds. The hook is <line or idea>.
> Use the <name> kit. Do not publish anything. Write the brief and tell me the
> plan in two lines.

## 2. Base creative direction (applies to every short)

> Add motion graphics, text overlays and captions to this clip. Keep it
> modern, clean and editorial. Captions are short phrases with no
> punctuation, one to four words. Never cover the speaker's face; place every
> element in empty space on purpose and say where it goes. One idea per
> overlay. Use only the kit's colours, fonts and zones.

## 3. Motion board (plan mode: write, do not build)

> Plan mode. Read transcript/words.json with its timestamps and the brief.
> Write motion-board.md: the hook in the first three seconds, which lines to
> cut (start and end in silence), then one row per overlay with output start
> and end, zone, effect from guides/effects.md, the exact on-screen words, the
> claim key for anything technical, and the reference image it follows. Say
> where captions move while an overlay owns their zone. End with open
> questions. Do not create or edit any composition yet.

Before approving, ask for more detail on any beat that is vague (exact words,
exact cue, exact zone); approve only a board you could build from.

## 4. Effects (attach the reference image every time)

- **Animated UI panel**: "Recreate the attached panel as an overlay in the
  lower zone. Rows arrive one by one as they are spoken, each check mark
  settles with a short ease, and the status pill lands last. Hold it until
  <time>."
- **Live-typing window**: "Put a window like the attached one in the empty
  space of the lower zone. Type these lines at speaking pace, starting when
  the speaker says '<word>': <lines>. Blinking cursor while typing; highlight
  <tokens> in the signal colour as they are spoken."
- **Layer scan**: "Take the attached design and reveal it as layers: a scan
  line sweeps down, a thin box draws around each layer as it is found, then
  the layers separate slightly in a slow swipe. About <n> seconds."
- **Hook card**: "Top zone, first three seconds: a kicker line in the
  editorial font, then the hook in display type, arriving with purpose and
  holding long enough to read."
- **Punch-in**: "At <time>, push in to <scale> over <duration> on the speaker
  for emphasis, then settle back. Keep the face centred in the face zone."

## 5. Captions

> Build captions from words.json with the kit's caption rules. Keep every
> word, in order, no punctuation, one to four words per phrase, highlight the
> spoken word. Move captions to <zone> while <beat> is on screen.

## 6. Iteration (short and specific)

- "Move the panel up 40 pixels; it crowds the captions."
- "The typing is ahead of the voice; start it at <time> and slow it by 20 %."
- "Hold the 101 row half a second longer before it leaves."
- "The hook is hard to read on this frame; add the kit's ink panel behind it."
- "Swap the kicker to: <words>. Nothing else changes."

## 7. Review

> Run the QC checklist. For each row give pass or fail with the evidence.
> Snapshot every board beat, tile them into a contact sheet, and compare each
> frame with the approved board: words, zone, face clear, fonts loaded,
> nothing cut off, platform-safe areas clear.

## Speaking prompts

Dictation works well for all of the above. Say the zone and the time
explicitly ("lower zone, from twelve point five seconds"), name effects by
their catalogue names, and end with what must not change. Your AI reads
the request back in two lines before acting.
