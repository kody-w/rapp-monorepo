import { createLogger } from "./logger.ts";

/**
 * Voice input via a local whisper.cpp server (`brew install whisper-cpp`;
 * Kody's rappvoice stack already runs one on :8765). The renderer records the
 * mic, downsamples to 16-kHz mono WAV, and hands the bytes here;
 * `POST /inference` answers `{"text": "..."}`.
 *
 * Env override (also used by tests): `WHISPER_URL`.
 */

const log = createLogger("Whisper");

export function whisperUrl(): string {
  return (process.env.WHISPER_URL || "http://127.0.0.1:8765").replace(/\/$/, "");
}

/** True when a whisper.cpp server answers on the configured port. */
export async function whisperAvailable(): Promise<boolean> {
  try {
    const r = await fetch(whisperUrl() + "/", { signal: AbortSignal.timeout(1500) });
    return r.ok;
  } catch {
    return false;
  }
}

/** Transcribe 16-kHz mono WAV bytes -> text. Throws on server errors. */
export async function transcribe(wav: Uint8Array): Promise<string> {
  const form = new FormData();
  form.append("file", new Blob([wav as BlobPart], { type: "audio/wav" }), "audio.wav");
  form.append("response_format", "json");
  form.append("temperature", "0.0");
  const r = await fetch(whisperUrl() + "/inference", {
    method: "POST",
    body: form,
    signal: AbortSignal.timeout(60_000),
  });
  if (!r.ok) throw new Error(`whisper HTTP ${r.status}`);
  const data = (await r.json()) as { text?: string; error?: string };
  if (data.error) throw new Error(data.error);
  const text = cleanTranscript(data.text ?? "");
  log.info("heard:", text || "(silence)");
  return text;
}

/**
 * whisper.cpp emits bracketed non-speech markers ([BLANK_AUDIO], [ Silence ],
 * (typing), *music*, [NOISE]) when a push-to-talk clip has no words. Strip them
 * so silence reads as empty — never as a message or an auto-title.
 */
export function cleanTranscript(raw: string): string {
  const cleaned = raw
    .replace(/[\[(*][^\])*]*(?:blank_audio|silence|no speech|inaudible|music|noise|sound|typing|applause|laughter|beep)[^\])*]*[\])*]/gi, " ")
    .replace(/\s+/g, " ")
    .trim();
  return cleaned;
}
