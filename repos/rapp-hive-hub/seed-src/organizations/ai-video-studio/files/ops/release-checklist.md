# Release checklist

The Release Desk prepares; the owner publishes. Nothing in this list uploads,
posts or schedules anything.

1. Render the approved project commit from a clean checkout with the pinned
   HyperFrames CLI. Record the CLI version.
2. Confirm the master with `ffprobe`: 1080x1920, H.264, AAC, 30 fps, duration
   inside the case limits.
3. Export `captions.srt` with `node tools/caption-phraser.mjs ... --srt`. The
   SRT keeps the punctuation-free phrases exactly as shown on screen.
4. Export `cover.png` from the approved cover beat (a HyperFrames snapshot).
5. Draft `post.md`: title under 60 characters, a two-line caption, three to
   five hashtags. Claims in the copy follow the same carryover rule as
   on-screen text.
6. Write `PROVENANCE.json`: script and claim ledger sha256, corpus sha256,
   board and approval sha256, project commit, CLI version, and bytes plus
   sha256 for every file in the package.
7. Hand the package to the Showrunner for the owner's release decision.
