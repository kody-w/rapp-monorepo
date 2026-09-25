---
name: Hive copy
layer: 4
order: 2
role: Your copy of each Hive; its `members/<you>/` is shared, and every member can read it
home: The Hive agent's private state (`<hive>/.git/rapp-hive/`)
health: experimental
lines:
  - your copy of each Hive
  - your space is shared
  - one key per device
brought_from: organism/parts/hive-copy.md
brought_sha256: 801e08cfd197e70d6fd3f0f8790a48b24815efbee7c0bbe1f2faffe448bc5268
---
Your Hive copy is your checkout of a Hive. Its `members/<you>/` folder is yours to write, and it is shared: every member can read it.

- Your device holds one key for this Hive, and it signs your commits.
- Your device verifies every change before it checks anything out.
