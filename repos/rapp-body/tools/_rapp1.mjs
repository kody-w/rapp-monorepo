// Mirrors kody-w/rapp-1/rapp.py: rapp/1 canonicalization, hashing, and §7 frames.

import crypto from "node:crypto";

export const SPEC = "rapp/1";
export const FRAME_KEYS = new Set([
  "spec", "kind", "stream_id", "seq", "utc", "payload",
  "payload_hash", "frame_hash", "prev", "prev_wave", "sig",
]);
export const KINDS = new Set(["body.pulse", "body.pulse-reconstructed"]);

const HEX64 = /^[0-9a-f]{64}$/;
const UTC = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/;
const KIND = /^[a-z0-9]+(?:-[a-z0-9]+)*\.[a-z0-9]+(?:-[a-z0-9]+)*$/;
const RAPPID = /^rappid:@([a-z0-9]+(?:-[a-z0-9]+)*)\/([a-z0-9]+(?:-[a-z0-9]+)*):([0-9a-f]{64})$/;

function isObject(value) {
  if (value === null || typeof value !== "object" || Array.isArray(value)) return false;
  const prototype = Object.getPrototypeOf(value);
  return prototype === Object.prototype || prototype === null;
}

function compareCodePoints(a, b) {
  const left = Array.from(a);
  const right = Array.from(b);
  const length = Math.min(left.length, right.length);
  for (let i = 0; i < length; i++) {
    const difference = left[i].codePointAt(0) - right[i].codePointAt(0);
    if (difference !== 0) return difference;
  }
  return left.length - right.length;
}

function assertUnicodeScalarString(value) {
  for (let i = 0; i < value.length; i++) {
    const code = value.charCodeAt(i);
    if (code >= 0xd800 && code <= 0xdbff) {
      const next = value.charCodeAt(i + 1);
      if (!(next >= 0xdc00 && next <= 0xdfff)) {
        throw new ValueError("non-I-JSON string: unpaired surrogate");
      }
      i++;
    } else if (code >= 0xdc00 && code <= 0xdfff) {
      throw new ValueError("non-I-JSON string: unpaired surrogate");
    }
  }
}

class ValueError extends Error {
  constructor(message) {
    super(message);
    this.name = "ValueError";
  }
}

function canonicalValue(value, active) {
  if (value === null || typeof value === "boolean") return JSON.stringify(value);
  if (typeof value === "number") {
    if (!Number.isInteger(value)) {
      throw new ValueError("floats require full-JCS number serialization; use ints/strings");
    }
    if (!Number.isSafeInteger(value)) {
      throw new ValueError("integer outside the exact JavaScript safe-integer domain");
    }
    return JSON.stringify(value);
  }
  if (typeof value === "string") {
    assertUnicodeScalarString(value);
    return JSON.stringify(value);
  }
  if (typeof value !== "object") {
    throw new ValueError(`non-I-JSON value: ${typeof value}`);
  }
  if (active.has(value)) throw new ValueError("non-I-JSON value: cyclic object");
  active.add(value);
  try {
    if (Array.isArray(value)) {
      const items = [];
      for (let i = 0; i < value.length; i++) {
        if (!Object.prototype.hasOwnProperty.call(value, i)) {
          throw new ValueError("non-I-JSON value: sparse array");
        }
        items.push(canonicalValue(value[i], active));
      }
      return `[${items.join(",")}]`;
    }
    if (!isObject(value)) {
      throw new ValueError(`non-I-JSON value: ${Object.prototype.toString.call(value)}`);
    }
    const keys = Object.keys(value).sort(compareCodePoints);
    if (keys.length !== new Set(keys).size) throw new ValueError("duplicate keys");
    return `{${keys.map((key) => {
      assertUnicodeScalarString(key);
      return `${JSON.stringify(key)}:${canonicalValue(value[key], active)}`;
    }).join(",")}}`;
  } finally {
    active.delete(value);
  }
}

export function canonical(value) {
  return canonicalValue(value, new WeakSet());
}

export function H(space, value) {
  if (typeof space !== "string") throw new TypeError("hash space must be a string");
  return crypto.createHash("sha256")
    .update(space, "utf8")
    .update("\n", "utf8")
    .update(canonical(value), "utf8")
    .digest("hex");
}

export function payloadHash(payload) {
  return H("rapp/1:particle", payload);
}

export function frameHash(frame) {
  if (!isObject(frame)) throw new ValueError("frame must be an object");
  const preimage = {};
  for (const key of Object.keys(frame)) {
    if (key !== "frame_hash" && key !== "sig") preimage[key] = frame[key];
  }
  return H("rapp/1:wave", preimage);
}

function normalizeBuildArguments(args) {
  if (args.length === 1 && isObject(args[0])) return args[0];
  const [kind, stream_id, seq, utc, payload, prev, prev_wave = null, sig = null] = args;
  return { kind, stream_id, seq, utc, payload, prev, prev_wave, sig };
}

export function buildFrame(...args) {
  const {
    kind, stream_id, seq, utc, payload, prev,
    prev_wave = null, sig = null,
  } = normalizeBuildArguments(args);
  const frame = {
    spec: SPEC,
    kind,
    stream_id,
    seq,
    utc,
    payload,
    payload_hash: payloadHash(payload),
    prev,
    prev_wave,
    sig,
  };
  frame.frame_hash = frameHash(frame);
  return frame;
}

function result(ok, step, reason) {
  return { ok, step, code: step, reason };
}

export function verifyFrame(frame, head = null, { swarm = false, streamId = null } = {}) {
  // 1 shape & types
  if (!isObject(frame) || !sameKeySet(Object.keys(frame), FRAME_KEYS)) {
    const keys = isObject(frame) ? Object.keys(frame).sort(compareCodePoints) : [];
    return result(false, "1", `key set != 11 (${JSON.stringify(keys)})`);
  }
  if (frame.spec !== SPEC) return result(false, "1", "spec != rapp/1");
  if (!(typeof frame.kind === "string" && KIND.test(frame.kind))) {
    return result(false, "1", "kind grammar");
  }
  if (!KINDS.has(frame.kind)) return result(false, "1", `unknown kind ${frame.kind}`);
  if (typeof frame.stream_id !== "string") return result(false, "1", "stream_id type");
  if (!RAPPID.test(frame.stream_id)) return result(false, "1", "stream_id not rappid");
  if (!(Number.isSafeInteger(frame.seq) && frame.seq >= 0)) {
    return result(false, "1", "seq not uint53");
  }
  if (!(typeof frame.utc === "string" && UTC.test(frame.utc))) {
    return result(false, "1", "utc not fixed form");
  }
  if (!isObject(frame.payload)) return result(false, "1", "payload not object");
  for (const key of ["payload_hash", "frame_hash"]) {
    if (!(typeof frame[key] === "string" && HEX64.test(frame[key]))) {
      return result(false, "1", `${key} not 64hex`);
    }
  }
  for (const key of ["prev", "prev_wave"]) {
    if (!(frame[key] === null || (typeof frame[key] === "string" && HEX64.test(frame[key])))) {
      return result(false, "1", `${key} not null|64hex`);
    }
  }

  // 1a stream binding
  const streamOfRecord = streamId ?? (head && head.stream_id) ?? null;
  if (streamOfRecord !== null && frame.stream_id !== streamOfRecord) {
    return result(false, "1a", "stream_id mismatch (cross-stream replay)");
  }

  // 2 particle
  let computedPayloadHash;
  try {
    computedPayloadHash = payloadHash(frame.payload);
  } catch (error) {
    return result(false, "2", `payload canonicalization failed: ${error.message}`);
  }
  if (frame.payload_hash !== computedPayloadHash) {
    return result(false, "2", "payload_hash mismatch");
  }

  // 3 wave
  let computedFrameHash;
  try {
    computedFrameHash = frameHash(frame);
  } catch (error) {
    return result(false, "3", `frame canonicalization failed: ${error.message}`);
  }
  if (frame.frame_hash !== computedFrameHash) {
    return result(false, "3", "frame_hash mismatch");
  }

  // 4 chain
  if (head === null) {
    if (!(frame.seq === 0 && frame.prev === null)) {
      return result(false, "4", "genesis must be seq=0 prev=null");
    }
  } else {
    if (frame.seq !== head.seq + 1) return result(false, "4", "seq not contiguous");
    if (frame.prev !== head.payload_hash) {
      return result(false, "4", "prev != head payload_hash");
    }
    if (frame.utc < head.utc) return result(false, "4", "utc < head utc");
  }

  // 5 wire
  if (swarm && frame.seq > 0) {
    if (head !== null && frame.prev_wave !== head.frame_hash) {
      return result(false, "5", "prev_wave != head frame_hash");
    }
  } else if (frame.prev_wave !== null) {
    return result(false, "5", "prev_wave must be null off swarm");
  }

  // 6 signature
  if (swarm && frame.sig === null) {
    return result(false, "6", "swarm frame must be signed");
  }
  return result(true, null, "ok");
}

function sameKeySet(keys, expected) {
  return keys.length === expected.size && keys.every((key) => expected.has(key));
}

// JSON.parse accepts duplicate object members and rounds large integers. Frame readers use
// this exact-domain parser so invalid source JSON cannot become a different value silently.
export function parseJsonExact(text) {
  const source = String(text);
  let offset = 0;

  function fail(message) {
    throw new SyntaxError(`${message} at byte ${Buffer.byteLength(source.slice(0, offset), "utf8")}`);
  }

  function whitespace() {
    while (offset < source.length && /[\t\n\r ]/.test(source[offset])) offset++;
  }

  function string() {
    if (source[offset] !== "\"") fail("expected string");
    const start = offset++;
    while (offset < source.length) {
      const character = source[offset++];
      if (character === "\"") {
        let value;
        try {
          value = JSON.parse(source.slice(start, offset));
        } catch (error) {
          fail(`invalid string (${error.message})`);
        }
        assertUnicodeScalarString(value);
        return value;
      }
      if (character === "\\") {
        if (offset >= source.length) fail("unterminated escape");
        offset++;
      }
    }
    fail("unterminated string");
  }

  function number() {
    const match = source.slice(offset).match(/^-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?/);
    if (!match) fail("invalid number");
    const token = match[0];
    offset += token.length;
    if (/[.eE]/.test(token)) {
      throw new ValueError("floats require full-JCS number serialization; use ints/strings");
    }
    const value = Number(token);
    if (!Number.isSafeInteger(value)) {
      throw new ValueError("integer outside the exact JavaScript safe-integer domain");
    }
    return value;
  }

  function array() {
    offset++;
    const value = [];
    whitespace();
    if (source[offset] === "]") {
      offset++;
      return value;
    }
    while (true) {
      value.push(any());
      whitespace();
      if (source[offset] === "]") {
        offset++;
        return value;
      }
      if (source[offset] !== ",") fail("expected ',' or ']'");
      offset++;
      whitespace();
    }
  }

  function object() {
    offset++;
    const value = Object.create(null);
    const keys = new Set();
    whitespace();
    if (source[offset] === "}") {
      offset++;
      return value;
    }
    while (true) {
      const key = string();
      if (keys.has(key)) throw new ValueError("duplicate keys");
      keys.add(key);
      whitespace();
      if (source[offset] !== ":") fail("expected ':'");
      offset++;
      value[key] = any();
      whitespace();
      if (source[offset] === "}") {
        offset++;
        return value;
      }
      if (source[offset] !== ",") fail("expected ',' or '}'");
      offset++;
      whitespace();
    }
  }

  function any() {
    whitespace();
    const character = source[offset];
    if (character === "\"") return string();
    if (character === "{") return object();
    if (character === "[") return array();
    if (character === "-" || (character >= "0" && character <= "9")) return number();
    for (const [token, value] of [["true", true], ["false", false], ["null", null]]) {
      if (source.startsWith(token, offset)) {
        offset += token.length;
        return value;
      }
    }
    fail("unexpected token");
  }

  const value = any();
  whitespace();
  if (offset !== source.length) fail("trailing data");
  return value;
}
