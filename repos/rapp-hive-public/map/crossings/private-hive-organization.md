---
from: private-hive
to: organization
what: A signed Hive vector (`work.vector`) naming the accepted checkpoint
authorized_by: The organization's signer, after verifying the checkpoint under `rapp-hive/1`
home: Canonical `rapp-work/1` §§2, 4
health: specified (G16)
arrow: down
label: "work.vector: the accepted Hive checkpoint"
brought_from: organism/crossings/private-hive-organization.md
brought_sha256: aea7b94b786b5e0769307d2c4322822ccfba1ed5b26599bbe1353784df0596ff
---
An organization binds exactly one Private Hive by its `hive_rappid`. Each signed `work.vector` records which authenticated Hive checkpoint it accepted, and it keeps that as a high-water mark: a lower sequence is rollback, and different hashes at one sequence are a fork. No estate has activated this yet (G16).
