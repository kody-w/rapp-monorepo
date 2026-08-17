/**
 * Monkey SEE: the work. Screen frames (main process hands getDisplayMedia the
 * primary screen — no picker) are OCR'd locally with Tesseract.js; only the
 * extracted text snippets ever leave the renderer, and only toward the local
 * brainstem as conversation context.
 */

interface TesseractWorker {
  recognize(image: HTMLCanvasElement): Promise<{ data: { text?: string } }>;
}
declare global {
  interface Window {
    Tesseract?: {
      createWorker(
        lang: string,
        oem?: number,
        options?: Record<string, unknown>,
      ): Promise<TesseractWorker>;
    };
  }
}

export interface ScreenWatchEvents {
  onStatus(text: string): void;
  onText(snippet: string): void;
  onEnded(): void;
}

export interface ScreenWatch {
  stop(): void;
}

export async function startScreenWatch(
  video: HTMLVideoElement,
  ev: ScreenWatchEvents,
): Promise<ScreenWatch> {
  const stream = await navigator.mediaDevices.getDisplayMedia({ video: { frameRate: 2 } });
  video.srcObject = stream;
  await video.play().catch(() => undefined);
  stream.getVideoTracks()[0].addEventListener("ended", () => { stopAll(); ev.onEnded(); });

  let worker: TesseractWorker | null = null;
  let busy = false;
  let lastSig = 0;
  let stopped = false;

  const snap = async () => {
    if (stopped || busy || video.readyState < 2) return;
    const canvas = document.createElement("canvas");
    const w = 1280;
    const h = Math.round((w * video.videoHeight) / (video.videoWidth || 1)) || 720;
    canvas.width = w;
    canvas.height = h;
    canvas.getContext("2d")!.drawImage(video, 0, 0, w, h);

    const tiny = document.createElement("canvas");
    tiny.width = 32;
    tiny.height = 18;
    tiny.getContext("2d")!.drawImage(canvas, 0, 0, 32, 18);
    const px = tiny.getContext("2d")!.getImageData(0, 0, 32, 18).data;
    let sig = 0;
    for (let i = 0; i < px.length; i += 16) sig = (sig + px[i]) % 1e9;
    if (Math.abs(sig - lastSig) < 3) return;
    lastSig = sig;

    try {
      busy = true;
      ev.onStatus("reading…");
      if (!worker) {
        if (!window.Tesseract) {
          // Vendored locally by scripts/setup-vision-assets.mjs — no CDN.
          await new Promise<void>((res, rej) => {
            const s = document.createElement("script");
            s.src = "/vendor/tesseract.min.js";
            s.onload = () => res();
            s.onerror = () => rej(new Error("tesseract runtime missing — run npm install"));
            document.head.appendChild(s);
          });
        }
        worker = await window.Tesseract!.createWorker("eng", 1, {
          workerPath: "/vendor/worker.min.js",
          corePath: "/vendor/tesseract-core-simd-lstm.wasm.js",
          langPath: "https://tessdata.projectnaptha.com/4.0.0",
        });
      }
      const { data } = await worker.recognize(canvas);
      const text = (data.text || "").replace(/\s+/g, " ").trim().slice(0, 500);
      if (text) ev.onText(text);
      ev.onStatus("watching");
    } catch (err) {
      ev.onStatus(`ocr failed: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      busy = false;
    }
  };

  const timer = setInterval(() => void snap(), 5000);
  void snap();

  const stopAll = () => {
    stopped = true;
    clearInterval(timer);
    stream.getTracks().forEach((t) => t.stop());
    video.srcObject = null;
  };
  return { stop: stopAll };
}
