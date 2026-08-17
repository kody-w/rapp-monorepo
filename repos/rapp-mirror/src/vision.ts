/**
 * Monkey SEE: eyes. Face presence / attention / nod / shake / blink-hold plus
 * hand gestures, all local (MediaPipe tasks-vision, models cached by the
 * browser after first load). Built to fail soft: each detector loads
 * independently, tick errors are counted and the loop stops with a visible
 * reason instead of dying silently — "camera doesn't work" must always have
 * a message attached.
 */

import { FaceLandmarker, FilesetResolver, GestureRecognizer } from "@mediapipe/tasks-vision";

// All runtime assets are staged locally by scripts/setup-vision-assets.mjs
// (postinstall) — no CDN at runtime; some networks break jsdelivr entirely.
const assetUrl = (relative: string) =>
  new URL(relative, window.location.href).toString();
const WASM_BASE = assetUrl("./vision/wasm");
const FACE_MODEL = assetUrl("./vision/models/face_landmarker.task");
const GESTURE_MODEL = assetUrl("./vision/models/gesture_recognizer.task");

export type HeadGesture = "nod" | "shake";
export type HandGesture =
  | "Open_Palm"
  | "Thumb_Up"
  | "Thumb_Down"
  | "Closed_Fist"
  | "Victory"
  | "Pointing_Up"
  | "ILoveYou";

export interface VisionEvents {
  onStatus(text: string): void;
  onSeen(parts: string[]): void;
  onHead(gesture: HeadGesture): void;
  /** Head-assisted pointing: nose offset from frame center, mirrored so the
   *  user's right is positive x, down is positive y (each roughly ±0.25). */
  onPose(dx: number, dy: number): void;
  onHand(gesture: HandGesture): void;
  /** Fingertip cursor (index tip, mirrored to screen space 0..1) with pinch
   *  state — rapp-vui's hand cursor: .40 close / .62 open hysteresis, scale
   *  invariant (normalized by the wrist→index-MCP span). `pinchDown` fires
   *  exactly once per pinch closure. null x/y when the hand is lost. */
  onHandPoint(x: number | null, y: number | null, pinching: boolean, pinchDown: boolean): void;
  onBlinkHold(): void;
  onFatal(message: string): void;
}

interface Detectors {
  mode: "VIDEO" | "IMAGE";
  face: FaceLandmarker | null;
  hands: GestureRecognizer | null;
}
interface FaceResult {
  faceLandmarks?: { x: number; y: number }[][];
  faceBlendshapes?: { categories: { categoryName: string; score: number }[] }[];
}
interface HandResult {
  gestures?: { categoryName: string; score: number }[][];
  landmarks?: { x: number; y: number }[][];
}

const detectorCache = new Map<"VIDEO" | "IMAGE", Detectors>();

async function loadDetectors(
  onStatus: (s: string) => void,
  mode: "VIDEO" | "IMAGE",
): Promise<Detectors> {
  const cached = detectorCache.get(mode);
  if (cached) return cached;
  onStatus("loading vision runtime…");
  const files = await FilesetResolver.forVisionTasks(WASM_BASE);
  const loaded: Detectors = { mode, face: null, hands: null };
  try {
    onStatus("loading face model…");
    loaded.face = await FaceLandmarker.createFromOptions(files, {
      baseOptions: { modelAssetPath: FACE_MODEL },
      outputFaceBlendshapes: true,
      runningMode: mode,
      numFaces: 1,
    });
  } catch (err) {
    console.error("[vision] face model failed:", err);
  }
  try {
    onStatus("loading gesture model…");
    loaded.hands = await GestureRecognizer.createFromOptions(files, {
      baseOptions: { modelAssetPath: GESTURE_MODEL },
      runningMode: mode,
      numHands: 1,
    });
  } catch (err) {
    console.error("[vision] gesture model failed:", err);
  }
  if (!loaded.face && !loaded.hands) {
    throw new Error("vision models missing — run `npm install` once while online to stage them");
  }
  detectorCache.set(mode, loaded);
  return loaded;
}

export interface VisionModes {
  /** Face tracking: presence, attention, head-pointing dwell, nod/shake, blink. */
  eyes: boolean;
  /** Hand tracking: gesture selection (point to cycle, thumb-up to confirm…). */
  hands: boolean;
}

export interface VisionSession {
  setModes(modes: VisionModes): void;
  stop(): void;
}

export async function startVision(
  video: HTMLVideoElement,
  ev: VisionEvents,
  initialModes: VisionModes = { eyes: true, hands: true },
  frameUrl = window.mirror.cameraFrameUrl,
): Promise<VisionSession> {
  let stream: MediaStream | null = null;
  let remoteImage: HTMLImageElement | null = null;
  let remoteLoading = false;
  let remoteFrameVersion = 0;
  let lastProcessedRemoteFrame = -1;
  let lastRemoteFrameAt = 0;
  const remote = frameUrl.trim();
  if (remote) {
    if (!/^https?:\/\/(?:127\.0\.0\.1|localhost)(?::\d+)?\//.test(remote)) {
      throw new Error("remote camera endpoint must stay on loopback");
    }
    ev.onStatus("connecting to RBox camera sensor…");
    remoteImage = new Image();
    remoteImage.crossOrigin = "anonymous";
    await new Promise<void>((resolve, reject) => {
      remoteImage!.onload = () => {
        remoteFrameVersion += 1;
        lastRemoteFrameAt = performance.now();
        resolve();
      };
      remoteImage!.onerror = () => reject(
        new Error(
          "RBox camera sensor did not return a CORS-enabled frame",
        ),
      );
      remoteImage!.src = `${remote}${remote.includes("?") ? "&" : "?"}t=${Date.now()}`;
    });
    video.poster = remote;
  } else {
    // Ask the OS first (macOS): a denied TCC prompt is the #1 "camera doesn't
    // work" cause, and getUserMedia alone reports it as an opaque NotAllowed.
    const osOk = await window.mirror.askMedia("camera");
    if (!osOk) {
      throw new Error(
        "macOS denied camera access — enable it in System Settings → Privacy & Security → Camera, then retry.",
      );
    }
    ev.onStatus("starting camera…");
    stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 640, height: 480, facingMode: "user" },
    });
    video.srcObject = stream;
    await video.play().catch(() => undefined);
  }

  const dets = await loadDetectors(
    ev.onStatus,
    remote ? "IMAGE" : "VIDEO",
  );
  ev.onStatus("tracking");

  const refreshRemote = () => {
    if (!remoteImage || remoteLoading) return;
    remoteLoading = true;
    const next = new Image();
    next.crossOrigin = "anonymous";
    next.onload = () => {
      remoteImage = next;
      remoteFrameVersion += 1;
      lastRemoteFrameAt = performance.now();
      remoteLoading = false;
    };
    next.onerror = () => {
      remoteLoading = false;
    };
    next.src = `${remote}${remote.includes("?") ? "&" : "?"}t=${Date.now()}`;
  };

  const nose: { t: number; x: number; y: number }[] = [];
  let lastHand: { name: string; since: number; fired: number } = { name: "", since: 0, fired: 0 };
  let blinkStart = 0;
  let errors = 0;
  let stopped = false;
  let modes: VisionModes = { ...initialModes };
  let pinching = false;

  const headGesture = (): HeadGesture | null => {
    if (nose.length < 6) return null;
    const axis = (k: "x" | "y") => {
      let revs = 0, dir = 0, amp = 0, last = nose[0][k];
      for (const p of nose) {
        const d = p[k] - last;
        if (Math.abs(d) > 0.004) {
          const nd = Math.sign(d);
          if (dir && nd !== dir) revs++;
          dir = nd;
          amp = Math.max(amp, Math.abs(d));
        }
        last = p[k];
      }
      return { revs, amp };
    };
    const y = axis("y"), x = axis("x");
    if (y.revs >= 2 && y.amp > 0.012 && y.revs > x.revs) { nose.length = 0; return "nod"; }
    if (x.revs >= 2 && x.amp > 0.015) { nose.length = 0; return "shake"; }
    return null;
  };

  const tick = () => {
    if (stopped) return;
    try {
      if (
        remoteImage &&
        performance.now() - lastRemoteFrameAt > 1000
      ) {
        lastHand.name = "";
        nose.length = 0;
        blinkStart = 0;
        if (pinching) pinching = false;
        ev.onHandPoint(null, null, false, false);
        refreshRemote();
        setTimeout(tick, 100);
        return;
      }
      const sourceReady = remoteImage
        ? remoteImage.complete &&
          remoteImage.naturalWidth > 0 &&
          remoteFrameVersion !== lastProcessedRemoteFrame
        : video.readyState >= 2;
      if (sourceReady) {
        if (remoteImage) lastProcessedRemoteFrame = remoteFrameVersion;
        const now = performance.now();
        const parts: string[] = [];
        if (dets.face && modes.eyes) {
          const faces = (
            remoteImage
              ? dets.face.detect(remoteImage)
              : dets.face.detectForVideo(video, now)
          ) as FaceResult;
          const face = faces.faceLandmarks?.[0];
          if (face) {
            const n = face[1];
            nose.push({ t: now, x: n.x, y: n.y });
            while (nose.length && now - nose[0].t > 1400) nose.shift();
            ev.onPose(0.5 - n.x, n.y - 0.5);
            const g = headGesture();
            if (g === "nod") ev.onHead("nod");
            if (g === "shake") ev.onHead("shake");
            parts.push(Math.abs(n.x - 0.5) < 0.16 ? "attentive" : "present");
            const bs = faces.faceBlendshapes?.[0];
            if (bs) {
              const score = (nm: string) => bs.categories.find((c) => c.categoryName === nm)?.score ?? 0;
              const closed = score("eyeBlinkLeft") > 0.55 && score("eyeBlinkRight") > 0.55;
              if (closed) {
                if (!blinkStart) blinkStart = now;
                else if (now - blinkStart > 1200) { ev.onBlinkHold(); blinkStart = 0; }
              } else blinkStart = 0;
            }
          } else nose.length = 0;
        }
        if (dets.hands && modes.hands) {
          const hands = (
            remoteImage
              ? dets.hands.recognize(remoteImage)
              : dets.hands.recognizeForVideo(video, now)
          ) as HandResult;
          // fingertip cursor + pinch (index tip 8, thumb tip 4; span wrist 0 -> index MCP 5)
          const lm = hands.landmarks?.[0];
          if (lm && lm.length > 8) {
            const span = Math.hypot(lm[0].x - lm[5].x, lm[0].y - lm[5].y) || 1;
            const ratio = Math.hypot(lm[4].x - lm[8].x, lm[4].y - lm[8].y) / span;
            let pinchDown = false;
            if (!pinching && ratio < 0.4) { pinching = true; pinchDown = true; }
            else if (pinching && ratio > 0.62) pinching = false;
            ev.onHandPoint(1 - lm[8].x, lm[8].y, pinching, pinchDown);
          } else {
            if (pinching) pinching = false;
            ev.onHandPoint(null, null, false, false);
          }
          const g = hands.gestures?.[0]?.[0];
          if (g && g.score > 0.6 && g.categoryName !== "None") {
            if (lastHand.name !== g.categoryName) {
              lastHand = { name: g.categoryName, since: now, fired: lastHand.fired };
            } else if (now - lastHand.since > 500 && now - lastHand.fired > 1800) {
              lastHand.fired = now;
              ev.onHand(g.categoryName as HandGesture);
            }
            parts.push(g.categoryName.toLowerCase().replace(/_/g, " "));
          } else lastHand.name = "";
        }
        ev.onSeen(parts);
      }
      if (remoteImage) refreshRemote();
      errors = 0;
    } catch (err) {
      if (++errors >= 5) {
        stopped = true;
        stream?.getTracks().forEach((t) => t.stop());
        ev.onFatal(`vision loop failed: ${err instanceof Error ? err.message : String(err)}`);
        return;
      }
    }
    setTimeout(tick, 100);
  };
  tick();

  return {
    setModes(next: VisionModes) {
      modes = { ...next };
    },
    stop() {
      stopped = true;
      stream?.getTracks().forEach((t) => t.stop());
      video.srcObject = null;
      video.poster = "";
    },
  };
}
