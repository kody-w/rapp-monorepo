import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import {
  createSession,
  deleteSession,
  listSessions,
  resetStoreCacheForTests,
  updateSession,
} from "./sessionstore.ts";

/** Run fn against a fresh store in a mkdtemp dir (env saved/restored). */
function withStore<T>(fn: (dir: string) => T): T {
  const dir = mkdtempSync(path.join(os.tmpdir(), "mirror-sessions-"));
  const prev = process.env.MIRROR_SESSIONS_DIR;
  process.env.MIRROR_SESSIONS_DIR = dir;
  resetStoreCacheForTests();
  try {
    return fn(dir);
  } finally {
    if (prev === undefined) delete process.env.MIRROR_SESSIONS_DIR; else process.env.MIRROR_SESSIONS_DIR = prev;
    resetStoreCacheForTests();
  }
}

test("create -> list roundtrips, newest updatedAt first", () => {
  withStore(() => {
    const a = createSession();
    const b = createSession();
    assert.equal(a.title, "New conversation");
    assert.deepEqual(a.history, []);
    assert.equal(a.lastSaid, "");
    assert.ok(a.id && a.id !== b.id);

    assert.deepEqual(listSessions().map((s) => s.id), [b.id, a.id]);

    // Touching a moves it to the front.
    updateSession({ id: a.id, lastSaid: "hi" });
    assert.deepEqual(listSessions().map((s) => s.id), [a.id, b.id]);
  });
});

test("update merges the patch, bumps updatedAt, auto-titles from the first user turn", () => {
  withStore(() => {
    const s = createSession();
    const before = s.updatedAt;
    const ask = "Summarize the quarterly revenue numbers for the CFO by Friday";

    const updated = updateSession({
      id: s.id,
      history: [
        { role: "user", content: ask },
        { role: "assistant", content: "On it." },
      ],
      lastSaid: "On it.",
    });
    assert.ok(updated);
    assert.ok(updated.updatedAt > before);
    assert.equal(updated.lastSaid, "On it.");
    assert.equal(updated.history.length, 2);
    assert.equal(updated.title, ask.slice(0, 40).trim());

    // An explicit title wins and sticks — no re-auto-title on later turns.
    updateSession({ id: s.id, title: "CFO summary" });
    const again = updateSession({ id: s.id, history: [{ role: "user", content: "something else" }] });
    assert.equal(again?.title, "CFO summary");

    assert.equal(updateSession({ id: "no-such-id", lastSaid: "x" }), null);
  });
});

test("delete removes the session; unknown id is a no-op", () => {
  withStore(() => {
    const s = createSession();
    deleteSession("no-such-id");
    assert.equal(listSessions().length, 1);
    deleteSession(s.id);
    assert.deepEqual(listSessions(), []);
  });
});

test("a corrupt sessions.json yields an empty store, never a throw", () => {
  withStore((dir) => {
    writeFileSync(path.join(dir, "sessions.json"), "{not json at all");
    assert.deepEqual(listSessions(), []);
    // And the store recovers: the next mutation persists a clean file.
    const s = createSession();
    resetStoreCacheForTests();
    assert.deepEqual(listSessions().map((x) => x.id), [s.id]);
  });
});

test("sessions persist to disk across a cache reset", () => {
  withStore((dir) => {
    const s = createSession();
    updateSession({ id: s.id, history: [{ role: "user", content: "remember me" }] });
    resetStoreCacheForTests();

    const listed = listSessions();
    assert.equal(listed.length, 1);
    assert.equal(listed[0].id, s.id);
    assert.equal(listed[0].title, "remember me");
    assert.deepEqual(listed[0].history, [{ role: "user", content: "remember me" }]);

    // The on-disk artifact really is the store (tmp+rename left no droppings).
    const raw = JSON.parse(readFileSync(path.join(dir, "sessions.json"), "utf8"));
    assert.equal(raw.length, 1);
    assert.equal(raw[0].id, s.id);
  });
});
