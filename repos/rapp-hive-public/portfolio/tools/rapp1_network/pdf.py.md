# `rapp1_network/pdf.py`

The poster PDF: headless Chrome prints the poster page, and the print is rewritten as 7-bit text.

Source: `rapp1_network/pdf.py` (rapp1-network 0.1.5). SHA-256 of the source below: `fecf69df6223dfde098bf04b94c787a60d2c6ccef4a6eb7f93c3e890b0704f76` (16539 bytes). Every pulse this release cuts records it in `payload.generator` as `rapp1_network/pdf.py`. Copy it out with the extractor in [../README.md](../README.md); code in a Hive is data, never run from the Hive.

{% raw %}
`````python
"""The poster PDF: headless Chrome prints the poster page, and the print is rewritten as 7-bit text.

A Hive holds only markdown, and GitHub Pages must serve the PDF exactly as it was printed, so `ascii_pdf` rewrites
Chrome's classic-xref PDF as printable ASCII: every stream becomes an ASCIIHex stream (its other filters kept), every
literal string holding other bytes becomes a hex string with the same bytes, and the dates and IDs are fixed so a
reprint on the same machine gives the same bytes. The page renders exactly as Chrome printed it.

    chrome(env=None)                                    the Chrome, Chromium or Edge executable, or None
    print_pdf(poster_html, date, permalink, chrome=None) the wrapped subway.pdf.md text (7-bit, one page)
    ascii_pdf(data, date)                               the 7-bit rewrite of a PDF Chrome wrote

`chrome` finds the browser on macOS, Linux and Windows (RAPP1_CHROME overrides it); `print_pdf` takes an injected
`chrome` command so tests can print with a fake. Standard library only.
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path, PureWindowsPath
from typing import Callable, Mapping, Sequence

from .constants import HIVE_MAX_BYTES
from .util import sha256, write_text
from .wrapping import Refused, wrap

WS, DELIM = b" \t\r\n\f\x00", b"()<>[]{}/%"


def _ws(d, i):
    while i < len(d):
        if d[i] in WS:
            i += 1
        elif d[i] == 0x25:
            while i < len(d) and d[i] not in b"\r\n":
                i += 1
        else:
            break
    return i


def _token(d, i):
    j = i
    while j < len(d) and d[j] not in WS and d[j] not in DELIM:
        j += 1
    return j


def _value(d, i):
    """The end of the PDF value that starts at i."""
    i = _ws(d, i)
    if d.startswith(b"<<", i):
        i += 2
        while True:
            i = _ws(d, i)
            if d.startswith(b">>", i):
                return i + 2
            i = _value(d, _value(d, i))
    c = d[i:i + 1]
    if c == b"[":
        i += 1
        while True:
            i = _ws(d, i)
            if d[i:i + 1] == b"]":
                return i + 1
            i = _value(d, i)
    if c == b"(":
        depth = 0
        while True:
            ch = d[i]
            if ch == 0x5C:
                i += 2
                continue
            depth += (ch == 0x28) - (ch == 0x29)
            i += 1
            if depth == 0:
                return i
    if c == b"<":
        return d.index(b">", i) + 1
    if c == b"/":
        return _token(d, i + 1)
    j = _token(d, i)
    if re.fullmatch(rb"\d+", d[i:j]):  # an indirect reference "n g R"
        k = _ws(d, j)
        k2 = _token(d, k)
        if re.fullmatch(rb"\d+", d[k:k2]):
            k3 = _ws(d, k2)
            if d[k3:k3 + 1] == b"R" and _token(d, k3) == k3 + 1:
                return k3 + 1
    return j


def _entries(d):
    """[(key, raw value)] of the dictionary d."""
    i, out = _ws(d, 0) + 2, []
    while True:
        i = _ws(d, i)
        if d.startswith(b">>", i):
            return out
        k = _value(d, i)
        v0 = _ws(d, k)
        v1 = _value(d, v0)
        out.append((d[i:k], d[v0:v1]))
        i = v1


def _ascii_strings(d):
    """Literal strings holding bytes outside printable ASCII become hex strings with the same bytes."""
    out, i = bytearray(), 0
    while i < len(d):
        ch = d[i]
        if ch == 0x28:
            j = _value(d, i)
            raw = d[i + 1:j - 1]
            if any(b > 0x7E or (b < 0x20 and b not in b"\n") for b in raw) or b"\r" in raw:
                s, k = bytearray(), 0
                while k < len(raw):  # undo the literal string's escapes
                    b = raw[k]
                    if b == 0x5C and k + 1 < len(raw):
                        n = raw[k + 1]
                        simple = {0x6E: 10, 0x72: 13, 0x74: 9, 0x62: 8, 0x66: 12, 0x28: 0x28, 0x29: 0x29, 0x5C: 0x5C}
                        if n in simple:
                            s.append(simple[n]); k += 2
                        elif 0x30 <= n <= 0x37:
                            m = re.match(rb"[0-7]{1,3}", raw[k + 1:k + 4]).group(0)
                            s.append(int(m, 8) & 0xFF); k += 1 + len(m)
                        elif n in b"\r\n":
                            k += 2 + (n == 13 and raw[k + 2:k + 3] == b"\n")
                        else:
                            s.append(n); k += 2
                    else:
                        s.append(b); k += 1
                out += b"<" + bytes(s).hex().upper().encode() + b">"
            else:
                out += d[i:j]
            i = j
        elif d.startswith(b"<<", i) or d.startswith(b">>", i):
            out += d[i:i + 2]
            i += 2
        elif ch == 0x3C:
            j = d.index(b">", i) + 1
            out += d[i:j]
            i = j
        else:
            out.append(ch)
            i += 1
    return bytes(out)


def ascii_pdf(data: bytes, date: str) -> bytes:
    """Rewrite Chrome's classic-xref PDF as 7-bit text, with fixed dates and IDs so a reprint gives the same bytes.
    A PDF it cannot read is refused (wrapping.Refused), never passed on half-rewritten."""
    try:
        return _ascii_pdf(data, date)
    except (ValueError, KeyError, IndexError, AttributeError, TypeError, zlib.error) as error:
        raise Refused(f"subway.pdf: Chrome's PDF could not be rewritten ({type(error).__name__}: {error})") from error


def _ascii_pdf(data, date):
    m = re.search(rb"startxref\s+(\d+)\s+%%EOF\s*$", data)
    if not m or not data.startswith(b"%PDF-"):
        raise Refused("subway.pdf: not a PDF Chrome wrote")
    at = int(m.group(1))
    if not data.startswith(b"xref", at):
        raise Refused("subway.pdf: its cross-reference is a stream; only classic tables are rewritten")
    offsets, i = {}, at + 4
    while True:
        i = _ws(data, i)
        if data.startswith(b"trailer", i):
            break
        head = re.match(rb"(\d+)\s+(\d+)", data[i:i + 40])
        first, count = int(head.group(1)), int(head.group(2))
        i += head.end()
        for n in range(count):
            i = _ws(data, i)
            entry = data[i:i + 18]
            if entry[17:18] == b"n":
                offsets[first + n] = int(entry[:10])
            i += 18
    t0 = _ws(data, i + 7)
    trailer = dict(_entries(data[t0:_value(data, t0)]))

    def obj(n):
        o = offsets[n]
        h = re.match(rb"\s*(\d+)\s+(\d+)\s+obj", data[o:o + 40])
        s = o + h.end()
        e = _value(data, s)
        return s, e

    def length_of(raw):
        ref = re.fullmatch(rb"(\d+)\s+(\d+)\s+R", raw.strip())
        if ref:
            s, e = obj(int(ref.group(1)))
            return int(data[s:e].strip())
        return int(raw)

    stamp = f"D:{date.replace('-', '')}000000Z".encode()
    iso = f"{date}T00:00:00Z".encode()
    bodies = {}
    for n in sorted(offsets):
        s, e = obj(n)
        k = _ws(data, e)
        value = data[s:e].strip()
        if data.startswith(b"stream", k):
            p = k + 6
            p += 2 if data[p:p + 2] == b"\r\n" else 1
            entries = _entries(value)
            keys = dict(entries)
            stream = data[p:p + length_of(keys[b"/Length"])]
            if not data[_ws(data, p + len(stream)):].startswith(b"endstream"):
                raise Refused(f"subway.pdf: object {n}'s stream length is wrong")
            filters = keys.get(b"/Filter", b"")
            if keys.get(b"/Type") == b"/Metadata" and filters in (b"", b"/FlateDecode"):
                xml = zlib.decompress(stream) if filters else stream
                xml = re.sub(rb"(<xmp:(?:CreateDate|ModifyDate|MetadataDate)>)[^<]*", rb"\g<1>" + iso, xml)
                xml = re.sub(rb"uuid:[0-9a-fA-F-]{36}", b"uuid:" + hashlib.md5(b"rapp1-subway", usedforsecurity=False).hexdigest().encode(), xml)
                stream, filters = xml, b""
            if filters == b"/FlateDecode" and b"/DecodeParms" not in keys:
                stream = zlib.compress(zlib.decompress(stream), 9)
            parms = keys.get(b"/DecodeParms")
            if filters.startswith(b"["):
                chain = b"[/ASCIIHexDecode " + filters[1:-1].strip() + b"]"
                parms = b"[null " + parms[1:-1].strip() + b"]" if parms and parms.startswith(b"[") else (
                    b"[null " + parms + b"]" if parms else None)
            elif filters:
                chain = b"[/ASCIIHexDecode " + filters + b"]"
                parms = b"[null " + parms + b"]" if parms else None
            else:
                chain = b"/ASCIIHexDecode"
            hexed = stream.hex().upper().encode()
            hexed = b"\n".join(hexed[j:j + 128] for j in range(0, len(hexed), 128)) + b">"
            kept = [(k2, _ascii_strings(v2)) for k2, v2 in entries if k2 not in (b"/Length", b"/Filter", b"/DecodeParms")]
            kept += [(b"/Filter", chain)] + ([(b"/DecodeParms", parms)] if parms else []) + [(b"/Length", str(len(hexed)).encode())]
            head = b"<<" + b" ".join(k2 + b" " + v2 for k2, v2 in kept) + b">>"
            bodies[n] = head + b"\nstream\n" + hexed + b"\nendstream"
        else:
            value = _ascii_strings(value)
            if value.startswith(b"<<") and re.search(rb"/(CreationDate|ModDate)\b", value):
                entries = [(k2, b"(" + stamp + b")" if k2 in (b"/CreationDate", b"/ModDate") else v2)
                           for k2, v2 in _entries(value)]
                value = b"<<" + b" ".join(k2 + b" " + v2 for k2, v2 in entries) + b">>"
            bodies[n] = value
    out = bytearray(b"%PDF-1.4\n%rapp1-subway 7-bit\n")
    where = {}
    for n in sorted(bodies):
        where[n] = len(out)
        out += f"{n} 0 obj\n".encode() + bodies[n] + b"\nendobj\n"
    size = max(bodies) + 1
    ident = hashlib.md5(bytes(out), usedforsecurity=False).hexdigest().upper().encode()
    xref = bytearray(f"xref\n0 {size}\n".encode() + b"0000000000 65535 f \n")
    for n in range(1, size):
        xref += (f"{where[n]:010d} 00000 n \n" if n in where else "0000000000 00000 f \n").encode()
    tail = [(b"/Size", str(size).encode()), (b"/Root", trailer[b"/Root"])]
    if b"/Info" in trailer:
        tail.append((b"/Info", trailer[b"/Info"]))
    tail.append((b"/ID", b"[<" + ident + b"> <" + ident + b">]"))
    start = len(out)
    out += bytes(xref) + b"trailer\n<<" + b" ".join(k2 + b" " + v2 for k2, v2 in tail) + b">>\n"
    out += f"startxref\n{start}\n%%EOF\n".encode()
    result = bytes(out)
    if any(b > 0x7E or (b < 0x20 and b != 10) for b in result):
        raise Refused("subway.pdf: the rewrite left bytes that are not printable ASCII")
    return result


PAGE = re.compile(rb"/Type\s*/Page(?![A-Za-z])")


def page_count(data: bytes) -> int:
    """How many page objects a PDF holds."""
    return len(PAGE.findall(data))


MAC_APPS = ("Google Chrome.app/Contents/MacOS/Google Chrome", "Chromium.app/Contents/MacOS/Chromium")
PATH_NAMES = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome")
LINUX_PATHS = ("/opt/google/chrome/chrome", "/snap/bin/chromium")


def chrome(env: Mapping[str, str] | None = None, platform: str | None = None,
           is_file: Callable[[str], bool] | None = None, which: Callable[[str], str | None] | None = None,
           home: str | None = None) -> str | None:
    """The browser that prints the poster: RAPP1_CHROME if set, else Google Chrome or Chromium where each platform
    installs it (macOS: /Applications and ~/Applications; Windows: Program Files and the user's LocalAppData,
    then Microsoft Edge, which prints the same way; Linux: the usual names on PATH), else None."""
    env = os.environ if env is None else env
    platform = sys.platform if platform is None else platform
    is_file = is_file or (lambda path: Path(path).is_file())
    which = which or shutil.which
    override = env.get("RAPP1_CHROME")
    if override:
        return override if is_file(override) else which(override)
    candidates: list[str] = []
    if platform == "darwin":
        home = home if home is not None else str(Path.home())
        candidates = [f"{base}/{app}" for app in MAC_APPS for base in ("/Applications", f"{home}/Applications")]
    elif platform.startswith(("win", "cygwin")):
        bases = [env[var] for var in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA") if env.get(var)]
        candidates = [str(PureWindowsPath(base, *parts)) for parts in
                      (("Google", "Chrome", "Application", "chrome.exe"), ("Chromium", "Application", "chrome.exe"),
                       ("Microsoft", "Edge", "Application", "msedge.exe")) for base in bases]
    for path in candidates:
        if is_file(path):
            return path
    names = PATH_NAMES + (("msedge",) if platform.startswith(("win", "cygwin")) else ())
    for name in names:
        found = which(name)
        if found:
            return found
    if not platform.startswith(("win", "cygwin", "darwin")):
        return next((path for path in LINUX_PATHS if is_file(path)), None)
    return None


def chrome_flags(raw: Path, platform: str | None = None, root: bool | None = None) -> list[str]:
    """Headless printing flags (no --user-data-dir: with it, a print can hang). Chrome refuses to run as root on
    Linux without --no-sandbox, which a container needs."""
    platform = sys.platform if platform is None else platform
    if root is None:
        root = hasattr(os, "geteuid") and os.geteuid() == 0
    return (["--headless=new", "--disable-gpu", "--no-pdf-header-footer"]
            + (["--no-sandbox"] if root and platform.startswith("linux") else []) + [f"--print-to-pdf={raw}"])


def _command(exe: str | Path | Sequence[str] | None) -> list[str]:
    if exe is None:
        found = chrome()
        if found is None:
            raise Refused("no Chrome or Chromium found (set RAPP1_CHROME to its path): subway.pdf was not printed")
        return [found]
    if isinstance(exe, (str, Path)):
        return [str(exe)]
    return [str(part) for part in exe]


def wrap_pdf(data: bytes, poster_html: str, date: str, permalink: str) -> str:
    """One printed page as the wrapped subway.pdf.md: 7-bit text, printed_from = the poster HTML's SHA-256."""
    count = page_count(data)
    if count != 1:
        raise Refused(f"subway.pdf has {count} pages, not 1")
    text = ascii_pdf(data, date).decode("ascii")
    wrapped = wrap(permalink, text).replace("layout: null\n", f"layout: null\nprinted_from: {sha256(poster_html)}\n", 1)
    if len(wrapped.encode()) > HIVE_MAX_BYTES:
        raise Refused(f"subway.pdf is {len(wrapped.encode())} bytes as text, over the Hive's 1 MB limit")
    return wrapped


def print_pdf(poster_html: str, date: str, permalink: str, chrome: str | Path | Sequence[str] | None = None,
              timeout: float = 240, platform: str | None = None) -> str:
    """Print the poster page with headless Chrome and return the wrapped subway.pdf.md served at `permalink`.
    `chrome` is the browser (None: found by chrome()) or a whole command prefix, e.g. a fake in tests. On Linux a
    print that produced nothing is tried once more with --no-sandbox (hosts that forbid the sandbox's user
    namespaces); the page is this package's own local file."""
    command = _command(chrome)
    platform = sys.platform if platform is None else platform
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as scratch:
        source, raw = Path(scratch) / "poster.html", Path(scratch) / "subway.chrome.pdf"
        write_text(source, poster_html)
        flags = chrome_flags(raw, platform)
        tries = [flags] + ([["--no-sandbox", *flags]] if platform.startswith("linux") and "--no-sandbox" not in flags
                           else [])
        for extra in tries:
            try:
                subprocess.run([*command, *extra, source.as_uri()], capture_output=True, timeout=timeout, check=False)
            except subprocess.TimeoutExpired:
                pass  # Chrome can stay up after it has printed; the file decides
            except OSError as error:
                raise Refused(f"Chrome could not start ({error.strerror or error}): subway.pdf was not printed")
            if raw.is_file():
                break
        if not raw.is_file():
            raise Refused("Chrome did not print subway.pdf")
        data = raw.read_bytes()
    return wrap_pdf(data, poster_html, date, permalink)
`````
{% endraw %}
