export const CANONICAL_HASH = "3f1c3b2a8d4e7f901a2b3c4d5e6f70819a0b1c2d3e4f5061728394a5b6c7d8e9";
export const COUNTERFEIT_HASH = "3f1c3b2a8d4e7f901a2b3c4d5e6f70819a0b1c2d3e4f5061728394a5b6c7d8e8";
export const ORDER = ["reveal", "compare", "identify", "reject"];

export function baseline() {
  return {
    stage: "hidden",
    step: -1,
    canonicalVisible: false,
    counterfeitVisible: false,
    changedField: null,
    canonicalAccepted: false,
    counterfeitVerdict: null,
    message: "Begin by revealing the canonical receipt."
  };
}

export function transition(state, action) {
  if (action === "reset") return baseline();

  const expected = ORDER[state.step + 1];
  if (action !== expected) {
    return { ...state, message: `Next required stage: ${expected ?? "reset"}.` };
  }

  if (action === "reveal") {
    return {
      ...state,
      stage: "revealed",
      step: 0,
      canonicalVisible: true,
      canonicalAccepted: true,
      message: "Canonical receipt revealed. Its five claims form one signed payload."
    };
  }

  if (action === "compare") {
    return {
      ...state,
      stage: "compared",
      step: 1,
      counterfeitVisible: true,
      message: "Comparison ready. The cards look alike; inspect the evidence fields."
    };
  }

  if (action === "identify") {
    return {
      ...state,
      stage: "identified",
      step: 2,
      changedField: {
        path: "artifact_sha256",
        index: 63,
        canonical: "9",
        counterfeit: "8"
      },
      message: "Exact change found: artifact_sha256 character 64, 9 → 8."
    };
  }

  return {
    ...state,
    stage: "rejected",
    step: 3,
    counterfeitVerdict: "rejected",
    canonicalAccepted: true,
    message: "Counterfeit rejected. Canonical acceptance is preserved."
  };
}
