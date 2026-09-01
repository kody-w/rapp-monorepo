import assert from "node:assert/strict";
import { baseline, transition, CANONICAL_HASH, COUNTERFEIT_HASH } from "./audit.js";

assert.equal(CANONICAL_HASH.length, 64);
assert.equal(COUNTERFEIT_HASH.length, 64);
const differences = [...CANONICAL_HASH].filter((char, index) => char !== COUNTERFEIT_HASH[index]);
assert.deepEqual(differences, ["9"]);

let state = baseline();
assert.deepEqual(state, baseline());

state = transition(state, "reveal");
assert.equal(state.canonicalAccepted, true);
assert.equal(state.canonicalVisible, true);

state = transition(state, "compare");
assert.equal(state.counterfeitVisible, true);

state = transition(state, "identify");
assert.deepEqual(state.changedField, {
  path: "artifact_sha256",
  index: 63,
  canonical: "9",
  counterfeit: "8"
});

state = transition(state, "reject");
assert.equal(state.counterfeitVerdict, "rejected");
assert.equal(state.canonicalAccepted, true);

state = transition(state, "reset");
assert.deepEqual(state, baseline());

console.log("receipt audit state machine: reveal/compare/identify/reject/reset passed");
