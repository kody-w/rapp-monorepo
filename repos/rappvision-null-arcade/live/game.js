(function (root, factory) {
  const api = factory();
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root) root.NullArcade = api;
})(typeof window !== "undefined" ? window : globalThis, function () {
  const STEPS = ["START", "BOOST", "JUMP", "FINISH"];
  const STEP_TIMES = [0, 910, 2080, 3580];

  function initialState(bestMs = null) {
    return {
      phase: "idle",
      routeIndex: -1,
      elapsedMs: 0,
      bestMs,
      integrity: "TRUSTED",
      message: "Press START, then follow the numbered route.",
      lastOutcome: "none"
    };
  }

  function transition(state, action) {
    const next = { ...state };
    if (action === "RESET") return initialState(state.bestMs);
    if (action === "CHEAT") {
      return {
        ...state,
        phase: "rejected",
        integrity: "UNTRUSTED",
        message: "CHEAT REJECTED — verified score preserved.",
        lastOutcome: "rejected"
      };
    }
    if (action === "START") {
      if (state.phase !== "idle") return { ...state, message: "Reset the run before starting again." };
      return {
        ...state,
        phase: "running",
        routeIndex: 0,
        elapsedMs: STEP_TIMES[0],
        integrity: "TRUSTED",
        message: "START verified. Next: BOOST.",
        lastOutcome: "none"
      };
    }
    const expectedIndex = state.routeIndex + 1;
    const actionIndex = STEPS.indexOf(action);
    if (state.phase !== "running" || actionIndex !== expectedIndex) {
      return {
        ...state,
        phase: "rejected",
        integrity: "UNTRUSTED",
        message: `ROUTE REJECTED — expected ${STEPS[expectedIndex] || "RESET"}, received ${action}.`,
        lastOutcome: "rejected"
      };
    }
    next.routeIndex = actionIndex;
    next.elapsedMs = STEP_TIMES[actionIndex];
    if (action === "FINISH") {
      next.phase = "finished";
      next.bestMs = state.bestMs === null ? next.elapsedMs : Math.min(state.bestMs, next.elapsedMs);
      next.message = "03.580 VERIFIED — score recorded.";
      next.lastOutcome = "verified";
    } else {
      next.message = `${action} verified. Next: ${STEPS[actionIndex + 1]}.`;
    }
    return next;
  }

  function formatTime(ms) {
    return `${String(Math.floor(ms / 1000)).padStart(2, "0")}.${String(ms % 1000).padStart(3, "0")}`;
  }

  return { STEPS, initialState, transition, formatTime };
});
