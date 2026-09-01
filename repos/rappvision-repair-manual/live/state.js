export const PARTS = Object.freeze({
  correct: Object.freeze({
    id: "RP-C17-12",
    teeth: 12,
    boreMm: 17,
    boreGeometry: "keyed-flat K3",
  }),
  wrong: Object.freeze({
    id: "RP-C17-11",
    teeth: 11,
    boreMm: 17,
    boreGeometry: "round",
  }),
});

export const REQUIRED = Object.freeze({
  id: "RP-C17-12",
  teeth: 12,
  boreMm: 17,
  boreGeometry: "keyed-flat K3",
});

export function initialState() {
  return {
    stage: "inspect",
    inspected: false,
    selected: null,
    result: null,
    restored: false,
    log: ["Replay ready. Start with INSPECT."],
  };
}

export function inspect(state) {
  return {
    ...state,
    stage: "choose",
    inspected: true,
    result: null,
    log: [...state.log, "Inspection: C17 witness marks exceed synthetic baseline."],
  };
}

export function choosePart(state, key) {
  if (!state.inspected || !PARTS[key]) return state;
  return {
    ...state,
    stage: "verify",
    selected: key,
    result: null,
    restored: false,
    log: [...state.log, `Selected ${PARTS[key].id}.`],
  };
}

export function verifyPart(state) {
  if (!state.selected) return state;
  const part = PARTS[state.selected];
  const mismatches = Object.keys(REQUIRED)
    .filter((field) => part[field] !== REQUIRED[field])
    .map((field) => ({
      field,
      expected: REQUIRED[field],
      received: part[field],
    }));

  if (mismatches.length) {
    return {
      ...state,
      stage: "reject",
      result: { status: "rejected", partId: part.id, mismatches },
      restored: false,
      log: [...state.log, `${part.id} rejected: ${mismatches.length} exact mismatch(es).`],
    };
  }

  return {
    ...state,
    stage: "accept",
    result: { status: "accepted", partId: part.id, mismatches: [] },
    restored: false,
    log: [...state.log, `${part.id} accepted: every required field matches.`],
  };
}

export function restoreMachine(state) {
  if (state.result?.status !== "accepted") return state;
  return {
    ...state,
    stage: "restore",
    restored: true,
    log: [...state.log, "Restored: synthetic runout returned to 0.2 mm baseline."],
  };
}
