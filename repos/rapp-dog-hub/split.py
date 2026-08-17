#!/usr/bin/env python3
"""
split — route content to the layer it belongs on.

Most real content is mixed. "Shipped the Halcyon migration for Northwind
Traders, invoiced $45,000, Jordan handled the books" is one sentence containing
a public fact, a customer name, a private figure and a colleague. Refusing the
whole thing loses the public half; publishing it loses the private half.

So this splits it:

    GOD   the customer, the figure, the colleague -> stays in the vault
    DOG   "shipped a platform migration for a client" -> may be published

Canon allows exactly this. Privacy means don't emit, *or generalize* — "a
national retailer" instead of the name — or keep it vault-side. It never means
encrypt-and-publish.

The degradation ladder
----------------------

    1. on-device LLM     nuanced: understands that "Halcyon" is a codename
                         and "the migration" is not
    2. deterministic     entity shapes, field names, known patterns
    3. fail closed       anything not positively cleared stays GOD

The ladder is STRICTLY on-device. Sending content to a hosted model to ask
whether it is private *is the leak you were preventing* — so an endpoint that
is not loopback is refused, not used.

And the ladder is monotonic toward privacy: a weaker rung emits less, never
more. Losing a publishable sentence costs nothing permanent. Publishing a
customer's name cannot be undone.
"""

from __future__ import annotations

import json
import os
import re
import socket
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Iterable

SPEC = "rapp-dog-split/1.0"

# Loopback only. See the module docstring — this is the load-bearing rule.
LOOPBACK_HOSTS = {"127.0.0.1", "::1", "localhost", "0.0.0.0"}

# Endpoints checked in order of preference. All local by construction.
ON_DEVICE_ENDPOINTS = [
    ("ollama", "http://127.0.0.1:11434"),
    ("llama.cpp", "http://127.0.0.1:8080"),
    ("lmstudio", "http://127.0.0.1:1234"),
]


class SplitError(Exception):
    """User-facing error."""


class NotOnDevice(SplitError):
    """An endpoint was configured that would send content off the machine."""


# --------------------------------------------------------------------------
# verdicts
# --------------------------------------------------------------------------

DOG = "dog"            # publishable as-is
GENERALIZED = "generalized"  # publishable once the specifics are removed
GOD = "god"            # stays in the vault


@dataclass
class Decision:
    """Why a piece of content went where it went. Always recorded."""

    path: str
    verdict: str
    reason: str
    rung: str
    original: str | None = None
    emitted: str | None = None

    def public(self) -> dict:
        """The decision WITHOUT the original text — safe to log or publish."""
        return {"path": self.path, "verdict": self.verdict, "reason": self.reason, "rung": self.rung}


@dataclass
class SplitResult:
    dog: Any
    god: Any
    decisions: list[Decision] = field(default_factory=list)
    rung: str = "fail_closed"

    @property
    def emitted_count(self) -> int:
        return sum(1 for d in self.decisions if d.verdict in (DOG, GENERALIZED))

    @property
    def withheld_count(self) -> int:
        return sum(1 for d in self.decisions if d.verdict == GOD)

    def audit(self) -> dict:
        """A publishable record of what was decided, with no content in it."""
        return {
            "spec": SPEC,
            "rung": self.rung,
            "emitted": self.emitted_count,
            "withheld": self.withheld_count,
            "decisions": [d.public() for d in self.decisions],
        }


# --------------------------------------------------------------------------
# rung 2 — deterministic
#
# Always available, no model required. Coarse but honest: it recognises shapes
# rather than meaning, so it generalizes bluntly and withholds when unsure.
# --------------------------------------------------------------------------

# (pattern, what it is, how to generalize it — None means never publishable)
ENTITY_RULES: list[tuple[str, str, str | None]] = [
    (r"[\w.+-]+@[\w-]+\.[\w.]{2,}", "an email address", None),
    (r"\+\d[\d\s().-]{8,}\d", "a phone number", None),
    (r"\b\d{1,5}\s+[A-Z][a-z]+\s+(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Boulevard|Blvd|Way|Court|Ct)\b", "a street address", None),
    (r"\b\d{3}-\d{2}-\d{4}\b", "a national ID", None),
    (r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}", "a token", None),
    (r"\b(?:sk|pk)-[A-Za-z0-9]{20,}", "an API key", None),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "a private key", None),
    (r"\b/(?:Users|home)/[\w.-]+", "a home directory path", "a local path"),
    (r"\$\s?[\d,]+(?:\.\d{2})?(?:\s?(?:k|m|million|thousand))?", "an amount of money", "an undisclosed amount"),
    (r"\b\d{4}-\d{2}-\d{2}\b", "an exact date", "a date"),
]

# Field names whose *contents* are GOD regardless of what they contain.
GOD_FIELD_NAMES = {
    "accounts", "account", "email", "phone", "address", "handle", "password",
    "secret", "token", "credential", "apikey", "api_key", "people", "person",
    "client", "customer", "contact", "facts", "notes", "private", "pii", "ssn",
}

# Field names that are safe to publish as-is.
DOG_FIELD_NAMES = {
    "kind", "spec", "version", "schema", "count", "counts", "tone", "avoid",
    "signatures", "tools", "capability", "capabilities", "title", "license",
    "fingerprint", "seq", "ts", "emitter", "status", "public",
}

# A capitalised multi-word phrase is very often an organisation or a person.
PROPER_NOUN = re.compile(r"\b(?:[A-Z][a-z]{2,}\s+){1,3}(?:[A-Z][a-z]{2,}|LLC|Ltd|Inc|Corp|GmbH|Traders|Group|Partners)\b")

# Words that make a capitalised phrase safe — projects and tech, not people.
KNOWN_SAFE_PROPER = re.compile(
    r"\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|January|February|March|April|May|June|July|August|September|October|November|December|Python|TypeScript|JavaScript|GitHub|Linux|macOS|Windows|Docker|Azure|AWS)\b"
)


def deterministic_classify(path: str, text: str) -> tuple[str, str, str | None]:
    """
    (verdict, reason, emitted_text) for one string.

    Errs toward GOD. A false GOD costs a lost sentence; a false DOG is forever.
    """
    leaf = path.split(".")[-1].split("[")[0].lower()

    if leaf in GOD_FIELD_NAMES:
        return GOD, f"field {leaf!r} is GOD-side by name", None

    generalized = text
    reasons: list[str] = []

    for pattern, what, replacement in ENTITY_RULES:
        if re.search(pattern, generalized):
            if replacement is None:
                return GOD, f"contains {what}, which has no safe generalization", None
            generalized = re.sub(pattern, replacement, generalized)
            reasons.append(f"{what} -> {replacement}")

    # Proper nouns are the hard case: "Northwind Traders" and "Project Halcyon"
    # look identical to a regex. Without a model to tell them apart, withhold.
    for match in PROPER_NOUN.finditer(generalized):
        phrase = match.group(0)
        if KNOWN_SAFE_PROPER.search(phrase):
            continue
        return (
            GOD,
            f"{phrase!r} may be an organisation or a person and this rung cannot tell",
            None,
        )

    if reasons:
        return GENERALIZED, "; ".join(reasons), generalized

    if leaf in DOG_FIELD_NAMES:
        return DOG, f"field {leaf!r} is DOG-side by name", text

    # Nothing matched. Short, unremarkable text is publishable; anything long
    # enough to hide a detail in is not, at this rung.
    if len(text) <= 120:
        return DOG, "no private shape detected", text

    return GOD, "too long to clear without a model — withheld by default", None


# --------------------------------------------------------------------------
# rung 1 — on-device LLM
# --------------------------------------------------------------------------

CLASSIFY_PROMPT = """You are a privacy boundary running ON the owner's own device.

Decide where one piece of the owner's content belongs.

  DOG  = safe to publish to the whole world, forever, as-is
  GENERALIZE = publishable only after specifics are removed
  GOD  = must never leave the device

GOD includes: names of people, customers, clients or employers; contact
details; addresses; exact amounts of money; account handles; anything that
identifies a specific third party.

DOG includes: technology, public repositories, open-source project names,
general activity, publicly known facts.

If you are not certain, answer GOD. A wrong GOD costs nothing. A wrong DOG is
permanent.

Answer with ONLY compact JSON:
{"verdict":"DOG|GENERALIZE|GOD","reason":"<8 words>","text":"<generalized text, only if GENERALIZE>"}

Content:
"""


def assert_on_device(url: str) -> None:
    """A non-loopback endpoint is the leak, not the mitigation."""
    host = re.sub(r"^https?://", "", url).split("/")[0].split(":")[0]
    if host in LOOPBACK_HOSTS:
        return
    try:
        resolved = socket.gethostbyname(host)
    except OSError:
        resolved = ""
    if not resolved.startswith("127."):
        raise NotOnDevice(
            f"refusing to send content to {host!r}. The splitter is on-device only: "
            "asking a hosted model whether something is private would be the leak itself."
        )


def _post_json(url: str, payload: dict, timeout: float) -> dict | None:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
        return None


def detect_on_device_model(explicit: str | None = None) -> tuple[str, str, str] | None:
    """(flavour, base_url, model) for the first local model that answers."""
    configured = explicit or os.environ.get("RAPP_SPLIT_ENDPOINT")
    if configured:
        assert_on_device(configured)
        model = os.environ.get("RAPP_SPLIT_MODEL", "llama3.2")
        flavour = "ollama" if "11434" in configured else "openai-compatible"
        return flavour, configured.rstrip("/"), model

    for flavour, base in ON_DEVICE_ENDPOINTS:
        assert_on_device(base)
        if flavour == "ollama":
            try:
                with urllib.request.urlopen(f"{base}/api/tags", timeout=1.5) as response:
                    tags = json.loads(response.read().decode("utf-8"))
                models = [m.get("name") for m in tags.get("models") or [] if m.get("name")]
                if models:
                    preferred = os.environ.get("RAPP_SPLIT_MODEL")
                    return flavour, base, preferred if preferred in models else models[0]
            except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
                continue
        else:
            try:
                with urllib.request.urlopen(f"{base}/v1/models", timeout=1.5) as response:
                    body = json.loads(response.read().decode("utf-8"))
                models = [m.get("id") for m in body.get("data") or [] if m.get("id")]
                if models:
                    return "openai-compatible", base, models[0]
            except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
                continue

    return None


def llm_classify(text: str, endpoint: tuple[str, str, str], timeout: float = 20.0) -> tuple[str, str, str | None] | None:
    """Ask the local model. None means it could not answer — caller degrades."""
    flavour, base, model = endpoint
    prompt = CLASSIFY_PROMPT + text

    if flavour == "ollama":
        body = _post_json(
            f"{base}/api/generate",
            {"model": model, "prompt": prompt, "stream": False, "options": {"temperature": 0}},
            timeout,
        )
        raw = (body or {}).get("response")
    else:
        body = _post_json(
            f"{base}/v1/chat/completions",
            {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0},
            timeout,
        )
        try:
            raw = body["choices"][0]["message"]["content"]  # type: ignore[index]
        except (TypeError, KeyError, IndexError):
            raw = None

    if not raw:
        return None

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return None

    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None

    verdict = str(parsed.get("verdict", "")).strip().upper()
    reason = str(parsed.get("reason", "")).strip()[:80] or "model decision"

    if verdict == "DOG":
        return DOG, reason, text
    if verdict == "GENERALIZE":
        generalized = str(parsed.get("text") or "").strip()
        # A "generalization" that kept the original is not a generalization.
        if not generalized or generalized == text:
            return GOD, "model could not generalize it safely", None
        return GENERALIZED, reason, generalized
    if verdict == "GOD":
        return GOD, reason, None

    return None  # unparseable verdict — degrade rather than guess


# --------------------------------------------------------------------------
# the splitter
# --------------------------------------------------------------------------


def walk_strings(value: Any, path: str = "") -> Iterable[tuple[str, str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk_strings(child, f"{path}.{key}" if path else str(key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_strings(child, f"{path}[{index}]")
    elif isinstance(value, str) and value.strip():
        yield path or "value", value


def set_path(target: dict, path: str, value: Any) -> None:
    """Rebuild a nested path, creating containers as needed."""
    parts = re.findall(r"[^.\[\]]+", path)
    cursor: Any = target
    for part in parts[:-1]:
        cursor = cursor.setdefault(part, {})
    cursor[parts[-1]] = value


def split(
    content: Any,
    *,
    rung: str = "auto",
    endpoint: tuple[str, str, str] | None = None,
) -> SplitResult:
    """
    Split content into a publishable half and a vault half.

    rung: 'auto' walks the ladder, 'deterministic' forces rung 2,
          'fail_closed' emits nothing at all.
    """
    if rung == "fail_closed":
        return SplitResult(
            dog={},
            god=content,
            rung="fail_closed",
            decisions=[
                Decision(path, GOD, "fail-closed: nothing is cleared for publication", "fail_closed", text)
                for path, text in walk_strings(content)
            ],
        )

    active_endpoint = endpoint
    active_rung = "deterministic"

    if rung in ("auto", "on_device_llm") and active_endpoint is None:
        active_endpoint = detect_on_device_model()

    if active_endpoint is not None:
        active_rung = "on_device_llm"
    elif rung == "on_device_llm":
        raise SplitError(
            "no on-device model is reachable. Start one (e.g. `ollama serve`), "
            "or use --rung deterministic. A hosted model is not an option here."
        )

    dog: dict = {}
    god: dict = {}
    decisions: list[Decision] = []

    for path, text in walk_strings(content):
        verdict = reason = None
        emitted: str | None = None
        used = active_rung

        if active_endpoint is not None:
            answer = llm_classify(text, active_endpoint)
            if answer is not None:
                verdict, reason, emitted = answer
            else:
                # The model failed on this item — degrade for this item only,
                # rather than abandoning the better rung for the whole document.
                used = "deterministic"

        if verdict is None:
            verdict, reason, emitted = deterministic_classify(path, text)

        # Belt and braces: whatever the model said, anything the deterministic
        # rung considers unpublishable is withheld. A model can be talked into
        # a bad answer by its own input; a regex cannot.
        if verdict in (DOG, GENERALIZED) and emitted is not None:
            safety_verdict, safety_reason, _ = deterministic_classify(path, emitted)
            if safety_verdict == GOD:
                verdict, reason, emitted = GOD, f"model cleared it but the safety net did not: {safety_reason}", None

        decisions.append(Decision(path, verdict, reason or "", used, text, emitted))

        if verdict == GOD or emitted is None:
            set_path(god, path, text)
        else:
            set_path(dog, path, emitted)
            if verdict == GENERALIZED:
                set_path(god, path, text)  # the original still lives in the vault

    return SplitResult(dog=dog, god=god, decisions=decisions, rung=active_rung)
