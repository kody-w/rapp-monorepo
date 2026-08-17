/**
 * Monkey SEE: ears. Two capture modes, both emitting 16-kHz mono WAV (the
 * shape whisper.cpp expects):
 *
 *  - `startRecording()` — push-to-talk (hold space): one utterance per hold.
 *  - `startNarration()` — narrate mode (the orb): the mic stays open and
 *    utterances are segmented on silence, skill-recorder's "Narrate — explain
 *    out loud" ethos applied to conversation. Chromium noise suppression +
 *    echo cancellation + OS voice isolation keep cafés survivable; energy
 *    gating keeps silence from ever reaching the transcriber.
 */

export interface Recording {
  stop(): Promise<ArrayBuffer>;
}

export interface NarrationEvents {
  /** A finished utterance, ready to transcribe. */
  onSegment(wav: ArrayBuffer): void;
  /** Smoothed input level 0..1 (~20 Hz) for UI liveness. */
  onLevel?(level: number): void;
  /** "quiet" | "speech" transitions. */
  onSpeech?(active: boolean): void;
}

export interface NarrationSession {
  stop(): void;
}

const SPEECH_RMS = 0.015;
const SPEECH_START_MS = 240;
const SILENCE_END_MS = 900;
const MIN_SEGMENT_MS = 500;
const MAX_SEGMENT_MS = 15000;

/** Open-mic narration: silence-segmented utterances via an energy gate. */
export async function startNarration(ev: NarrationEvents): Promise<NarrationSession> {
  const stream = await captureMic();
  const audioCtx = new AudioContext();
  const analyser = audioCtx.createAnalyser();
  analyser.fftSize = 2048;
  audioCtx.createMediaStreamSource(stream).connect(analyser);
  const buf = new Float32Array(analyser.fftSize);

  let recorder: MediaRecorder | null = null;
  let chunks: Blob[] = [];
  let speechAt = 0; // when continuous speech began (0 = not speaking)
  let quietAt = 0; // when the current quiet stretch began
  let segmentAt = 0; // when the current recorder started
  let inSpeech = false;
  let stopped = false;

  const startSegment = () => {
    chunks = [];
    recorder = new MediaRecorder(stream);
    recorder.ondataavailable = (e) => e.data.size && chunks.push(e.data);
    recorder.start();
    segmentAt = performance.now();
  };

  const closeSegment = (emit: boolean) => {
    const r = recorder;
    recorder = null;
    if (!r) return;
    r.onstop = async () => {
      if (emit && chunks.length) {
        try {
          ev.onSegment(await toWav16k(new Blob(chunks, { type: r.mimeType })));
        } catch {
          /* undecodable scrap segment — drop it */
        }
      }
      if (!stopped) startSegment();
    };
    r.stop();
  };

  startSegment();
  const gate = setInterval(() => {
    if (stopped || !recorder) return;
    analyser.getFloatTimeDomainData(buf);
    let sum = 0;
    for (let i = 0; i < buf.length; i++) sum += buf[i] * buf[i];
    const rms = Math.sqrt(sum / buf.length);
    ev.onLevel?.(Math.min(1, rms * 18));
    const now = performance.now();

    if (rms >= SPEECH_RMS) {
      if (!speechAt) speechAt = now;
      quietAt = 0;
      if (!inSpeech && now - speechAt > SPEECH_START_MS) {
        inSpeech = true;
        ev.onSpeech?.(true);
      }
    } else {
      speechAt = 0;
      if (inSpeech) {
        if (!quietAt) quietAt = now;
        if (now - quietAt > SILENCE_END_MS) {
          inSpeech = false;
          ev.onSpeech?.(false);
          const spoke = now - segmentAt > MIN_SEGMENT_MS + SILENCE_END_MS;
          closeSegment(spoke);
          quietAt = 0;
        }
      } else if (now - segmentAt > MAX_SEGMENT_MS) {
        closeSegment(false); // rotate away accumulated silence
      }
    }
    if (inSpeech && now - segmentAt > MAX_SEGMENT_MS) {
      inSpeech = false;
      ev.onSpeech?.(false);
      closeSegment(true); // force-cut a very long utterance
    }
  }, 50);

  return {
    stop() {
      stopped = true;
      clearInterval(gate);
      const r = recorder;
      recorder = null;
      if (r) {
        r.onstop = () => undefined;
        r.stop();
      }
      stream.getTracks().forEach((t) => t.stop());
      void audioCtx.close();
    },
  };
}

/** Teams-style capture hygiene for loud rooms: Chromium's WebRTC noise
 *  suppression + echo cancellation + AGC, plus the OS voice-isolation mic
 *  mode where the platform offers it (macOS 14+). */
async function captureMic(): Promise<MediaStream> {
  const osOk = await window.mirror.askMedia("microphone");
  if (!osOk) {
    throw new Error(
      "macOS denied microphone access — enable it in System Settings → Privacy & Security → Microphone.",
    );
  }
  // Open once so Chromium reveals device labels, then prefer the common
  // wireless creator-mic families (or an explicit configured label).
  const probe = await navigator.mediaDevices.getUserMedia({ audio: true });
  probe.getTracks().forEach((track) => track.stop());
  const devices = await navigator.mediaDevices.enumerateDevices();
  const configured = window.mirror.preferredMicLabel.trim().toLowerCase();
  const creatorMic =
    /(wireless|dji|r[oø]de|hollyland|lark|saramonic|comica|ankerwork)/i;
  const preferred = devices.find(
    (device) =>
      device.kind === "audioinput" &&
      Boolean(
        configured
          ? device.label.toLowerCase().includes(configured)
          : creatorMic.test(device.label),
      ),
  );
  return navigator.mediaDevices.getUserMedia({
    audio: {
      ...(preferred ? { deviceId: { exact: preferred.deviceId } } : {}),
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: true,
      // Newer Chromium forwards this to the OS voice-isolation pipeline.
      ...({ voiceIsolation: true } as MediaTrackConstraints),
    },
  });
}

export async function startRecording(): Promise<Recording> {
  const stream = await captureMic();
  const recorder = new MediaRecorder(stream);
  const chunks: Blob[] = [];
  recorder.ondataavailable = (e) => e.data.size && chunks.push(e.data);
  recorder.start();

  return {
    stop: () =>
      new Promise((resolve, reject) => {
        recorder.onstop = async () => {
          stream.getTracks().forEach((t) => t.stop());
          try {
            resolve(await toWav16k(new Blob(chunks, { type: recorder.mimeType })));
          } catch (err) {
            reject(err);
          }
        };
        recorder.stop();
      }),
  };
}

async function toWav16k(blob: Blob): Promise<ArrayBuffer> {
  const raw = await blob.arrayBuffer();
  const decodeCtx = new AudioContext();
  const decoded = await decodeCtx.decodeAudioData(raw);
  void decodeCtx.close();

  const rate = 16000;
  const frames = Math.max(1, Math.round(decoded.duration * rate));
  const offline = new OfflineAudioContext(1, frames, rate);
  const source = offline.createBufferSource();
  source.buffer = decoded;
  source.connect(offline.destination);
  source.start();
  const mono = (await offline.startRendering()).getChannelData(0);

  const wav = new ArrayBuffer(44 + mono.length * 2);
  const view = new DataView(wav);
  const ascii = (offset: number, s: string) => {
    for (let i = 0; i < s.length; i++) view.setUint8(offset + i, s.charCodeAt(i));
  };
  ascii(0, "RIFF");
  view.setUint32(4, 36 + mono.length * 2, true);
  ascii(8, "WAVE");
  ascii(12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true); // PCM
  view.setUint16(22, 1, true); // mono
  view.setUint32(24, rate, true);
  view.setUint32(28, rate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  ascii(36, "data");
  view.setUint32(40, mono.length * 2, true);
  for (let i = 0; i < mono.length; i++) {
    const s = Math.max(-1, Math.min(1, mono[i]));
    view.setInt16(44 + i * 2, s < 0 ? s * 0x8000 : s * 0x7fff, true);
  }
  return wav;
}
