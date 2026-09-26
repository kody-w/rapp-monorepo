# `rapp1_network/pins.py`

The known LTS pins: the long-term-support commits RAPP/1 already names in public, used until the estate publishes its LTS pins file (passed with --lts-pins / RAPP1_LTS_PINS). Each pin is {commit, version?}: `version` is the label when the pin is a tag; otherwise the label is the commit's first seven characters. Public facts only.

Source: `rapp1_network/pins.py` (rapp1-network 0.1.6). SHA-256 of the source below: `4790b4f20a847a0619ba95f952fb6b147f7bc858a7dada9dc18751c4268e4e48` (1176 bytes). Every pulse this release cuts records it in `payload.generator` as `rapp1_network/pins.py`. Copy it out with the extractor in [../README.md](../README.md); code in a Hive is data, never run from the Hive.

{% raw %}
`````python
"""The known LTS pins: the long-term-support commits RAPP/1 already names in public, used until the estate publishes
its LTS pins file (passed with --lts-pins / RAPP1_LTS_PINS). Each pin is {commit, version?}: `version` is the label
when the pin is a tag; otherwise the label is the commit's first seven characters. Public facts only."""

KNOWN_PINS = {
    # kody-w/rapp-1 at the canon pin: every rapp_check run of the network uses this commit (constants.CANON_RAPP1).
    "rapp-1": {"commit": "591e014ad39e223b00ab343ae26e5d9a867ebeee"},
    # kody-w/rapp-installer at the tag brainstem-v0.6.9: the LTS kernel that kody-w/RAPP's KERNEL_PIN.json pins on
    # its channel "lts" (the newest kernel tag, brainstem-v0.6.16, is newer by design).
    "rapp-installer": {"commit": "bded0e1d5044d293f465e3850758f4b012d95078", "version": "brainstem-v0.6.9"},
    # kody-w/rapp-work at 29ead23: the rapp-hive/1 reference that the estate's kit pins.
    "rapp-work": {"commit": "29ead23b21645f8d7682ee00414930ffa9ce0ca6"},
    # kody-w/rapp-map at 4c8ba6b: the base registry (seq 2) that the estate's kit pins.
    "rapp-map": {"commit": "4c8ba6bbe73125cc980d0c3b38c59c99e4b231c0"},
}
`````
{% endraw %}
