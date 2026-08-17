import assert from "node:assert/strict";
import test from "node:test";

import {
  DEFAULT_GESTURE_COMMANDS,
  parseGestureMapping,
  validGestureMap,
} from "./gestures.ts";

test("spoken gesture mappings produce bounded chat commands", () => {
  assert.deepEqual(
    parseGestureMapping("map victory gesture to summarize my active agents"),
    {
      gesture: "Victory",
      command: {
        label: "summarize my active agents",
        prompt: "summarize my active agents",
      },
    },
  );
  assert.equal(parseGestureMapping("map thumbs up gesture to delete files"), null);
  assert.equal(parseGestureMapping("hello mirror"), null);
});

test("gesture maps require every bounded command", () => {
  assert.equal(validGestureMap(DEFAULT_GESTURE_COMMANDS), true);
  assert.equal(validGestureMap({ Victory: { label: "x", prompt: "short" } }), false);
  assert.equal(
    validGestureMap({
      ...DEFAULT_GESTURE_COMMANDS,
      Victory: { label: "x", prompt: "x".repeat(501) },
    }),
    false,
  );
});

