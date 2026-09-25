---
from: folder-hive
to: public-copy
what: Exactly the files of an approved manifest
authorized_by: The approvals number; `check-public` verifies the copy
home: Hive folder convention; `rapp-hive/1` §2
health: experimental
arrow: out
label: approved files
brought_from: organism/crossings/folder-hive-public-copy.md
brought_sha256: 3ba3b4b0fc4f6829abaf17b5ddfce6474632a900eea6245a0995262175204fde
---
Members approve a manifest of exact files and hashes. Exactly those files are copied into the separate public copy, and anyone can check it with `check-public`. A Private Hive never publishes: `rapp-hive/1` disables external publication.
