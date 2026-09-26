# `rapp1_network/__main__.py`

`python -m rapp1_network <command>`: the command line (cli.py).

Source: `rapp1_network/__main__.py` (rapp1-network 0.1.6). SHA-256 of the source below: `ff528a493dcc20b88b404b21872ee8f98887698eb6c4a5a7f8f6927c834951ab` (122 bytes). Every pulse this release cuts records it in `payload.generator` as `rapp1_network/__main__.py`. Copy it out with the extractor in [../README.md](../README.md); code in a Hive is data, never run from the Hive.

{% raw %}
`````python
"""`python -m rapp1_network <command>`: the command line (cli.py)."""
import sys

from .cli import main

sys.exit(main())
`````
{% endraw %}
