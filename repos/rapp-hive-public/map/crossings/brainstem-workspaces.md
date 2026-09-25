---
from: brainstem
to: workspaces
what: Status, verify, discover, scaffold, update, migrate
authorized_by: "`plan_sha256`, applied explicitly"
home: "`rapp-work-sdk/1` §2"
health: in force for the SDK; the Brainstem integration is not built (G17)
arrow: both
label: SDK operations (not wired to the Brainstem yet, G17)
brought_from: organism/crossings/brainstem-workspaces.md
brought_sha256: 7a6c8971070e8a594564ee50be490be749b9a05478656c6ba0eca222306b769f
---
The RAPP Work SDK works on your private workspaces through six operations. The first three only read. The other three plan first, and apply only with the plan's exact hash. The SDK is in force, but the Brainstem does not call it yet: that is gap G17.
