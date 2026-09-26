# Tools

The standard-library Python tools that made this portfolio, as data: a Hive holds only markdown, so each source file is one `.md` file with the source in a fenced block and its SHA-256 above it. Code in a Hive is never run from the Hive; copy it out first.

- **Version 1** (pulse 0) was made by the two single-file tools `rapp1_portfolio.py` and `rapp1_subway.py`, kept here unchanged ([rapp1_portfolio.py.md](rapp1_portfolio.py.md), [rapp1_subway.py.md](rapp1_subway.py.md)); version 1's pulse names their SHA-256 in `payload.generator`.
- **Version 2** was made by an earlier release of the package: its release copy is in this public copy's history at commit [`b92a97c`](https://github.com/kody-w/rapp-hive-public/tree/b92a97c7ca91663cc33f74cad1de9f2d38f7e0d3/portfolio/tools) (its RELEASE.md names the release), and each pulse names every file's SHA-256 in `payload.generator`.
- **Version 3** was made by an earlier release of the package: its release copy is in this public copy's history at commit [`b684d17`](https://github.com/kody-w/rapp-hive-public/tree/b684d17b84f525a541dabcce25d89e5771b8f73b/portfolio/tools) (its RELEASE.md names the release), and each pulse names every file's SHA-256 in `payload.generator`.
- **Version 4** was made by an earlier release of the package: its release copy is in this public copy's history at commit [`7702790`](https://github.com/kody-w/rapp-hive-public/tree/7702790c58a8e024437ae91619db7e76f16ad9e8/portfolio/tools) (its RELEASE.md names the release), and each pulse names every file's SHA-256 in `payload.generator`.
- **Version 5** was made by an earlier release of the package: its release copy is in this public copy's history at commit [`eafa6de`](https://github.com/kody-w/rapp-hive-public/tree/eafa6de7e04a3d536c21976c1d85e845a499cd7b/portfolio/tools) (its RELEASE.md names the release), and each pulse names every file's SHA-256 in `payload.generator`.
- **Version 6** was made by an earlier release of the package: its release copy is in this public copy's history at commit [`c72cdea`](https://github.com/kody-w/rapp-hive-public/tree/c72cdea41b9f469a9b1d1dd4c8910cdecf37089c/portfolio/tools) (its RELEASE.md names the release), and each pulse names every file's SHA-256 in `payload.generator`.
- **Version 7 onwards** are made by the package `rapp1_network` (rapp1-network 0.1.6), every source file of it in `rapp1_network/`: [RELEASE.md](RELEASE.md) links each file and lists its SHA-256 and size, the release and its commit, and the `generator` each of its pulses records.

Rebuild the package from the markdown, check every file against its hash and RELEASE.md, and verify the published chain with it (run this in a clone of `kody-w/rapp-hive-public`, inside `portfolio/tools/`; it needs git and Python 3.12, writes the package to `release/`, and clones `kody-w/rapp-1` at the canon pin into `release/checker/rapp-1` unless `RAPP1_CHECKER` names a checkout at the pin):

```bash
python3 - <<'PY'
import hashlib, json, os, pathlib, re, subprocess, sys
fence, tick, out = chr(96) * 5, chr(96), pathlib.Path('release')
release = pathlib.Path('RELEASE.md').read_text(encoding='utf-8')
listed = json.loads(release.split(tick * 3 + 'json\n', 1)[1].split(tick * 3, 1)[0])
found = {}
for md in sorted(pathlib.Path('rapp1_network').glob('*.md')):
    text = md.read_text(encoding='utf-8')
    data = text.split(fence + 'python\n', 1)[1].rsplit(fence + '\n', 1)[0].encode('utf-8')
    path = re.search(r'^Source: .(rapp1_network/[^/ ]+?). ', text, re.M).group(1)
    want, size = re.search(r'SHA-256 of the source below: .([0-9a-f]{64}). .([0-9]+) bytes.', text).groups()
    assert hashlib.sha256(data).hexdigest() == want == listed.get(path) and len(data) == int(size), md.name
    assert path not in found, path
    found[path] = data
assert sorted(found) == sorted(listed), 'the markdown files are not exactly the files RELEASE.md lists'
for path, data in found.items():
    (out / path).parent.mkdir(parents=True, exist_ok=True)
    (out / path).write_bytes(data)
    print('ok', path, listed[path])
env = {**os.environ, 'PYTHONPATH': str(out.resolve())}
sys.exit(subprocess.run([sys.executable, '-B', '-m', 'rapp1_network', 'verify', '..', '--work', str(out)], env=env).returncode)
PY
```

`python -m rapp1_network verify ..` checks every pulse from the published genesis (RAPP/1 §7.5 steps 1-5 with rapp-1's reference `rapp.py`), rapp-1's own `rapp_check.py` on the chain, and each version's maps against the hashes its pulse recorded.

Crawl again and cut the next version (needs git, a signed-in `gh`, Chrome, and a Hive with `hive_agent.py` from `kody-w/rapp-model-hive`):

```bash
PYTHONPATH=release python3 -B -m rapp1_network crawl --work <work folder> --hive-agent <path to hive_agent.py> [--denylist <private scanner>]
```

Version 1's two files, copied out and checked the way version 1's README said:

```bash
python3 - <<'PY'
import hashlib, pathlib, re
fence = chr(96) * 5
for md in sorted(pathlib.Path('.').glob('*.py.md')):
    text = md.read_text(encoding='utf-8')
    source = text.split(fence + 'python\n', 1)[1].rsplit(fence + '\n', 1)[0]
    want = re.search(r'SHA-256 of the source below: .([0-9a-f]+).', text).group(1)
    assert hashlib.sha256(source.encode('utf-8')).hexdigest() == want, md.name
    pathlib.Path(md.name[:-3]).write_text(source, encoding='utf-8')
    print('ok', md.name[:-3], want)
PY
```
