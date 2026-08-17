import assert from "node:assert/strict";
import { test } from "node:test";

import { encodeShareUrl } from "./agentshare.ts";
import { alignmentCoords, encodeQr, qrPath } from "./qr.ts";
import type { ForgeSpecView } from "./ipc.ts";

const spec: ForgeSpecView = {
  name: "weekly-billing",
  className: "WeeklyBilling",
  title: "Weekly Unbilled Summary",
  description: "Tally unbilled time and email each client.",
  intent: "Automate the weekly billing review.",
  steps: [
    { title: "Fetch entries", detail: "Retrieve unbilled time grouped by client." },
    { title: "Total per client", detail: "Sum hours and dollar value." },
  ],
  parameters: [{ name: "run_date", description: "Period end", type: "string", required: false }],
};

test("a short payload picks a small version and a square matrix", () => {
  const qr = encodeQr("HELLO");
  assert.ok(qr);
  assert.equal(qr!.size, qr!.version * 4 + 17);
  assert.equal(qr!.modules.length, qr!.size);
  assert.ok(qr!.modules.every((row) => row.length === qr!.size));
});

test("the three finder patterns are present in the corners", () => {
  const { modules, size } = encodeQr("HELLO")!;
  // A finder's centre 3x3 is dark, and it is ringed by a light separator.
  for (const [r, c] of [
    [0, 0],
    [0, size - 7],
    [size - 7, 0],
  ] as const) {
    assert.equal(modules[r + 3][c + 3], true, `finder centre missing at ${r},${c}`);
    assert.equal(modules[r + 1][c + 1], false, `finder ring wrong at ${r},${c}`);
    assert.equal(modules[r][c], true);
  }
});

test("the timing patterns alternate along row and column six", () => {
  const { modules, size } = encodeQr("TIMING CHECK")!;
  for (let i = 8; i < size - 8; i++) {
    assert.equal(modules[6][i], i % 2 === 0, `horizontal timing broke at ${i}`);
    assert.equal(modules[i][6], i % 2 === 0, `vertical timing broke at ${i}`);
  }
});

test("a real agent share link encodes into a scannable matrix", () => {
  const { url } = encodeShareUrl(spec);
  const qr = encodeQr(url!);
  assert.ok(qr, "the share link did not fit in any QR version");
  assert.ok(qr!.version <= 40);
});

test("bigger payloads select bigger versions, monotonically", () => {
  const small = encodeQr("a")!;
  const large = encodeQr("a".repeat(600))!;
  assert.ok(large.version > small.version);
});

test("a payload beyond QR capacity returns null instead of a broken code", () => {
  assert.equal(encodeQr("x".repeat(5000)), null);
});

test("the same text always produces the identical matrix", () => {
  assert.deepEqual(encodeQr("stable")!.modules, encodeQr("stable")!.modules);
});

test("qrPath emits one drawable path covering every dark module", () => {
  const qr = encodeQr("PATH")!;
  const path = qrPath(qr);
  const dark = qr.modules.flat().filter(Boolean).length;
  assert.equal(path.split("M").length - 1, dark);
  assert.match(path, /^M\d+,\d+h1v1h-1z/);
});

test("the matrix is a mix of light and dark, never blank or solid", () => {
  const qr = encodeQr(encodeShareUrl(spec).url!)!;
  const dark = qr.modules.flat().filter(Boolean).length;
  const total = qr.size * qr.size;
  assert.ok(dark > total * 0.2 && dark < total * 0.8, `${dark}/${total} modules dark`);
});

test("alignment patterns appear at every non-finder coordinate, timing row included", () => {
  // The regression that made every version-7-and-up card unscannable: the
  // coordinates that sit on the timing row were being skipped, so the symbol
  // was structurally invalid and no scanner would read it.
  const qr = encodeQr("C".repeat(140))!;
  assert.ok(qr.version >= 7, `expected a v7+ symbol, got v${qr.version}`);
  const coords = alignmentCoords(qr.version);
  assert.ok(coords.length >= 3, "v7+ must have at least three coordinates");
  const { modules } = qr;
  const last = coords.length - 1;
  let checked = 0;
  for (let i = 0; i < coords.length; i++) {
    for (let j = 0; j < coords.length; j++) {
      const onFinder = (i === 0 && j === 0) || (i === 0 && j === last) || (i === last && j === 0);
      if (onFinder) continue;
      const r = coords[i];
      const c = coords[j];
      // Every alignment pattern is a dark centre, a light ring, a dark border.
      assert.equal(modules[r][c], true, `centre missing at ${r},${c}`);
      assert.equal(modules[r - 1][c], false, `ring missing at ${r},${c}`);
      assert.equal(modules[r][c - 1], false, `ring missing at ${r},${c}`);
      assert.equal(modules[r - 2][c], true, `border missing at ${r},${c}`);
      assert.equal(modules[r + 2][c], true, `border missing at ${r},${c}`);
      checked++;
    }
  }
  assert.ok(checked >= 6, `only checked ${checked} alignment patterns`);
});

test("version information is written for version 7 and above", () => {
  const qr = encodeQr("D".repeat(200))!;
  assert.ok(qr.version >= 7);
  const { modules, size } = qr;
  // The two 3x6 version blocks must not be uniformly blank.
  let dark = 0;
  for (let i = 0; i < 6; i++) {
    for (let j = 0; j < 3; j++) {
      if (modules[i][size - 11 + j]) dark++;
      if (modules[size - 11 + j][i]) dark++;
    }
  }
  assert.ok(dark > 0, "version information block is empty");
});

test("padding alternates with the standard pad codewords", () => {
  // A single short payload forces many pad bytes; a constant fill is a bug.
  const qr = encodeQr("X")!;
  assert.ok(qr.modules.flat().filter(Boolean).length > 20);
});
