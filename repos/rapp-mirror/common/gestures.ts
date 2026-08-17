export type CommandGesture = "Pointing_Up" | "Victory" | "ILoveYou";

export interface GestureCommand {
  label: string;
  prompt: string;
}

export type GestureCommandMap = Record<CommandGesture, GestureCommand>;

export const DEFAULT_GESTURE_COMMANDS: GestureCommandMap = {
  Pointing_Up: {
    label: "RBox status",
    prompt:
      "Give me a concise status of this RBox brainstem, its active agents, " +
      "and any work waiting for my approval.",
  },
  Victory: {
    label: "toggle screen watching",
    prompt: "@local:toggle-screen",
  },
  ILoveYou: {
    label: "ready for instruction",
    prompt:
      "Acknowledge that you are ready for my next spoken instruction and " +
      "state the current safety boundary in one sentence.",
  },
};

const GESTURE_NAMES: Record<string, CommandGesture> = {
  "pointing up": "Pointing_Up",
  "point up": "Pointing_Up",
  victory: "Victory",
  "peace sign": "Victory",
  "i love you": "ILoveYou",
  iloveyou: "ILoveYou",
};

export function parseGestureMapping(
  transcript: string,
): { gesture: CommandGesture; command: GestureCommand } | null {
  const match = transcript.trim().match(
    /^(?:set|map|change)\s+(?:the\s+)?(.+?)\s+gesture\s+(?:to|as|means?)\s+(.+)$/i,
  );
  if (!match) return null;
  const gesture = GESTURE_NAMES[match[1].trim().toLowerCase()];
  const prompt = match[2].trim();
  if (!gesture || prompt.length < 3 || prompt.length > 500) return null;
  return {
    gesture,
    command: {
      label: prompt.slice(0, 64),
      prompt,
    },
  };
}

export function validGestureMap(value: unknown): value is GestureCommandMap {
  if (!value || typeof value !== "object") return false;
  const candidate = value as Record<string, unknown>;
  return (Object.keys(DEFAULT_GESTURE_COMMANDS) as CommandGesture[]).every(
    (gesture) => {
      const command = candidate[gesture] as Partial<GestureCommand> | undefined;
      return Boolean(
        command &&
        typeof command.label === "string" &&
        command.label.length >= 1 &&
        command.label.length <= 64 &&
        typeof command.prompt === "string" &&
        command.prompt.length >= 3 &&
        command.prompt.length <= 500,
      );
    },
  );
}
