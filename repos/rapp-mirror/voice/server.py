#!/usr/bin/env python3
"""RAPP Mirror voice service — Microsoft VibeVoice-Realtime-0.5B over HTTP.

Gives the mirror its spoken voice. Loads the streaming TTS model once
(device auto: mps > cuda > cpu, per the upstream demo recipe: float32 + sdpa
on mps, 5 ddpm steps) and serves:

  GET  /health          -> {"status": "loading"|"ready"|"error", "speaker", "device", "voices"}
  GET  /voices          -> {"voices": [...]}
  POST /tts {"text", "speaker"?} -> audio/wav (24 kHz mono)

The mirror falls back to the browser's speechSynthesis when this service
isn't running, so it is always optional.

Setup (once): voice/setup.sh   — clones microsoft/VibeVoice into
~/.rapp-mirror/VibeVoice and installs the [streamingtts] extras into
~/.rapp-mirror/venv. Run with that venv's python:

  ~/.rapp-mirror/venv/bin/python voice/server.py
"""

import copy
import glob
import io
import json
import os
import threading
import wave
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("VOICE_PORT", "8971"))
MODEL = os.environ.get("VIBEVOICE_MODEL", "microsoft/VibeVoice-Realtime-0.5B")
VIBEVOICE_HOME = os.path.expanduser(os.environ.get("VIBEVOICE_HOME", "~/.rapp-mirror/VibeVoice"))
PREFERRED_SPEAKER = os.environ.get("VIBEVOICE_SPEAKER", "carter")
SAMPLE_RATE = 24000
MAX_CHARS = 800

STATE = {"status": "loading", "error": None, "device": None, "speaker": None}
VOICES = {}   # name -> .pt path
ENGINE = {}   # model, processor, prompts cache
GEN_LOCK = threading.Lock()


def find_voices():
    vdir = os.path.join(VIBEVOICE_HOME, "demo", "voices", "streaming_model")
    for pt in glob.glob(os.path.join(vdir, "**", "*.pt"), recursive=True):
        VOICES[os.path.splitext(os.path.basename(pt))[0].lower()] = os.path.abspath(pt)


def load_model():
    try:
        import torch
        from vibevoice.modular.modeling_vibevoice_streaming_inference import (
            VibeVoiceStreamingForConditionalGenerationInference,
        )
        from vibevoice.processor.vibevoice_streaming_processor import VibeVoiceStreamingProcessor

        device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
        dtype = torch.bfloat16 if device == "cuda" else torch.float32
        attn = "flash_attention_2" if device == "cuda" else "sdpa"

        processor = VibeVoiceStreamingProcessor.from_pretrained(MODEL)
        try:
            model = VibeVoiceStreamingForConditionalGenerationInference.from_pretrained(
                MODEL, torch_dtype=dtype, attn_implementation=attn,
                device_map=(device if device in ("cuda", "cpu") else None),
            )
        except Exception:
            model = VibeVoiceStreamingForConditionalGenerationInference.from_pretrained(
                MODEL, torch_dtype=dtype, attn_implementation="sdpa",
                device_map=(device if device in ("cuda", "cpu") else None),
            )
        if device == "mps":
            model.to("mps")
        model.eval()
        model.set_ddpm_inference_steps(num_steps=5)

        find_voices()
        if not VOICES:
            raise RuntimeError(f"no voice .pt files under {VIBEVOICE_HOME}/demo/voices/streaming_model")
        want = PREFERRED_SPEAKER.lower()
        speaker = next((v for v in sorted(VOICES) if want in v), None) \
            or next((v for v in sorted(VOICES) if v.startswith("en-")), None) \
            or sorted(VOICES)[0]

        ENGINE.update(model=model, processor=processor, torch=torch, prompts={})
        STATE.update(status="ready", device=device, speaker=speaker)
        print(f"[voice] ready on {device} · speaker={speaker} · voices={sorted(VOICES)}")
    except Exception as e:  # surface the reason in /health instead of dying
        STATE.update(status="error", error=str(e))
        print(f"[voice] failed to load: {e}")


def voice_prompt(name):
    """Load (and cache) a speaker's prefilled voice prompt tensors."""
    torch = ENGINE["torch"]
    if name not in ENGINE["prompts"]:
        from transformers.cache_utils import DynamicCache
        from transformers.modeling_outputs import BaseModelOutputWithPast

        target = STATE["device"] if STATE["device"] != "cpu" else "cpu"
        try:
            with torch.serialization.safe_globals([BaseModelOutputWithPast, DynamicCache]):
                ENGINE["prompts"][name] = torch.load(VOICES[name], map_location=target, weights_only=True)
        except Exception:
            # torch >= 2.6 weights_only unpickler can't rebuild these dataclass
            # containers even when allowlisted. The presets ship inside the
            # cloned microsoft/VibeVoice repo (trusted source), so fall back.
            ENGINE["prompts"][name] = torch.load(VOICES[name], map_location=target, weights_only=False)
    return ENGINE["prompts"][name]


def synthesize(text, speaker=None):
    torch = ENGINE["torch"]
    name = (speaker or STATE["speaker"] or "").lower()
    if name not in VOICES:
        name = STATE["speaker"]
    prompt = voice_prompt(name)
    inputs = ENGINE["processor"].process_input_with_cached_prompt(
        text=text, cached_prompt=prompt, padding=True,
        return_tensors="pt", return_attention_mask=True,
    )
    target = STATE["device"] if STATE["device"] != "cpu" else "cpu"
    for k, v in inputs.items():
        if torch.is_tensor(v):
            inputs[k] = v.to(target)
    with GEN_LOCK, torch.inference_mode():
        out = ENGINE["model"].generate(
            **inputs,
            max_new_tokens=None,
            cfg_scale=1.5,
            tokenizer=ENGINE["processor"].tokenizer,
            generation_config={"do_sample": False},
            verbose=False,
            all_prefilled_outputs=copy.deepcopy(prompt),
        )
    speech = out.speech_outputs and out.speech_outputs[0]
    if speech is None:
        raise RuntimeError("model produced no audio")
    audio = speech.detach().to("cpu", dtype=torch.float32).numpy().reshape(-1)
    pcm = (audio.clip(-1, 1) * 32767).astype("<i2").tobytes()
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(pcm)
    return buf.getvalue()


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "content-type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(200, b"")

    def do_GET(self):
        if self.path.startswith("/health"):
            self._send(200, json.dumps({**STATE, "voices": sorted(VOICES)}).encode())
        elif self.path.startswith("/voices"):
            self._send(200, json.dumps({"voices": sorted(VOICES)}).encode())
        else:
            self._send(404, b'{"error":"not found"}')

    def do_POST(self):
        if not self.path.startswith("/tts"):
            return self._send(404, b'{"error":"not found"}')
        if STATE["status"] != "ready":
            return self._send(503, json.dumps({"error": f"voice {STATE['status']}", "detail": STATE["error"]}).encode())
        try:
            length = int(self.headers.get("Content-Length", "0"))
            req = json.loads(self.rfile.read(length) or b"{}")
            text = (req.get("text") or "").strip()[:MAX_CHARS]
            if not text:
                return self._send(400, b'{"error":"text is required"}')
            self._send(200, synthesize(text, req.get("speaker")), ctype="audio/wav")
        except Exception as e:
            self._send(500, json.dumps({"error": str(e)}).encode())

    def log_message(self, fmt, *args):
        print("[voice]", fmt % args)


if __name__ == "__main__":
    threading.Thread(target=load_model, daemon=True).start()
    print(f"[voice] serving on http://127.0.0.1:{PORT} (model loads in background)")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
