---
name: Public copy
column: out
beside: 3
order: 1
role: A separate, reviewed repository holding exactly the approved files, plus `PUBLISHED.md`
home: The Hive folder convention; DOGG rules of `rapp-hive/1` §2
health: experimental
lines:
  - exactly the approved files
  - PUBLISHED.md · check-public
brought_from: organism/parts/public-copy.md
brought_sha256: 1508cdf9cb4c50bb99034849664899540227441de6ad1ee520607af5890460d0
---
A public copy is a separate repository. It holds exactly the files the members approved, plus `PUBLISHED.md`.

- Anyone can run `check-public` to verify it.
- The Hive itself never becomes public.
