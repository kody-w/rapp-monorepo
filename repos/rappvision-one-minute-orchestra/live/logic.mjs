export const canonical = Object.freeze({
  pulse: Object.freeze([1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0]),
  prism: Object.freeze([0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0]),
  verdant: Object.freeze([1,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0]),
  pearl: Object.freeze([0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1])
});

const voices = Object.freeze(Object.keys(canonical));

function copyPattern(pattern) {
  return Object.fromEntries(voices.map((voice) => [voice, [...pattern[voice]]]));
}

export function createState() {
  return {
    remix: copyPattern(canonical),
    enabled: Object.fromEntries(voices.map((voice) => [voice, true]))
  };
}

export function toggleStepState(state, voice, step) {
  if (!voices.includes(voice) || !Number.isInteger(step) || step < 0 || step > 15) {
    throw new RangeError("Unknown remix voice or step.");
  }
  state.remix[voice][step] = state.remix[voice][step] ? 0 : 1;
  return state;
}

export function toggleVoiceState(state, voice) {
  if (!voices.includes(voice)) throw new RangeError("Unknown remix voice.");
  state.enabled[voice] = !state.enabled[voice];
  return state;
}

export function rejectCanonicalEditState(state) {
  return {
    accepted: false,
    state,
    message: "Rejected: the canonical score is locked. Edit the remix instead."
  };
}

export function resetState() {
  return createState();
}

export function snapshotState(state) {
  return JSON.stringify({ canonical, remix: state.remix, enabled: state.enabled });
}
