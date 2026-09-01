const adults = [
  { id: "M-01", name: "Mallow", energy: 1, traits: "round wing · amber glow" },
  { id: "B-02", name: "Bramble", energy: 1, traits: "long wing · moss glow" }
];

const copy = (state) => JSON.parse(JSON.stringify(state));

export function createBaseline() {
  return {
    adults: adults.map((adult) => ({ ...adult })),
    child: null,
    inspected: false,
    lastEvent: "Baseline restored: two adults, one glow each, no hatchling."
  };
}

export function feedAdults(input) {
  const state = copy(input);
  state.adults = state.adults.map((adult) => ({
    ...adult,
    energy: Math.min(2, adult.energy + 1)
  }));
  state.lastEvent = state.adults.every((adult) => adult.energy === 2)
    ? "Both adults are well-fed: pairing is now available."
    : "Lantern spores added.";
  return state;
}

export function reproduceHatchling(input) {
  const state = copy(input);
  if (state.child) {
    state.lastEvent = "Reproduction paused: this habitat supports one hatchling.";
    return state;
  }
  if (!state.adults.every((adult) => adult.energy === 2)) {
    state.lastEvent = "Reproduction paused: both adults need two glow. Feed them first.";
    return state;
  }
  state.child = {
    id: "H-03",
    name: "Pip",
    energy: 1,
    traits: "round-long wing · amber-moss glow",
    parents: state.adults.map((adult) => adult.id)
  };
  state.adults = state.adults.map((adult) => ({ ...adult, energy: 1 }));
  state.lastEvent = "Hatchling H-03 created with immutable parent links M-01 + B-02.";
  return state;
}

export function inspectLineage(input) {
  const state = copy(input);
  if (!state.child) {
    state.lastEvent = "Lineage unavailable: reproduce a hatchling first.";
    return state;
  }
  state.inspected = true;
  state.lastEvent = "Lineage inspected: H-03 links to both M-01 and B-02.";
  return state;
}

export function attemptImpossibleMutation(input, trait) {
  const state = copy(input);
  state.lastEvent = `REJECTED — ${trait} are outside Mossbell constraints. Existing creatures and lineage were preserved.`;
  return state;
}
