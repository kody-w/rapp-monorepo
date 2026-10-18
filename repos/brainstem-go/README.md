# A Brainstem in Go

A Brainstem is the small program on your computer that runs your AI. This one is written in Go.

It was built by an AI (GPT-5.6 Sol) that never saw the original Brainstem's source. Its only guide was the
public test cases in [kody-w/rapp-1](https://github.com/kody-w/rapp-1/tree/main/conformance/grail). It took
about nine minutes and 623 lines. Then the shared test suite compared it with the original, check by check:

```
25 of 25 scenarios identical
```

That is the point: the Brainstem is defined by an open, testable contract, so anyone (or any AI) can build one
in any language and prove it behaves the same. [BUILD-REPORT.md](BUILD-REPORT.md) is the builder's own account,
including every difference it hit along the way and what it had to guess.

## Run the proof yourself

```bash
go build -o brainstem .
git clone https://github.com/kody-w/rapp-1
git clone https://github.com/kody-w/rapp-installer && git -C rapp-installer checkout 0e43ee580e78c150b1c59002456822d2e779388e
pip install -r rapp-installer/rapp_brainstem/requirements.txt
GRAIL_DIR=$PWD/rapp-installer/rapp_brainstem python3 rapp-1/conformance/grail/run.py --candidate "cmd:$PWD/brainstem"
```

Python agents run through `agent_shim.py`, so `python3` must be on the machine (or set `BRAINSTEM_PYTHON`).

## What it covers

The three doors the shared suite tests: `/health`, `/version` and `/chat`, including agents as tools, up to
three tool rounds and every input check. Sign-in, streaming, voice and the web page are not part of it.

MIT licensed.
