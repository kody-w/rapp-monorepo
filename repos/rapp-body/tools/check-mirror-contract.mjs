#!/usr/bin/env node
import assert from "node:assert/strict";
import fs from "node:fs";
import { SPEC_HOMES } from "./_census.mjs";

assert.deepEqual(Object.keys(SPEC_HOMES), ["historical_rapp"]);
assert.equal(SPEC_HOMES.historical_rapp.repo, "RAPP");
assert.equal(
  SPEC_HOMES.historical_rapp.ref,
  "789e6c5245f18e9685450fd6105dc26867837895",
);
assert.match(SPEC_HOMES.historical_rapp.label, /historical.*non-authoritative/i);

for (const file of ["README.md", "ORDER-BIRTH.md", "tools/_census.mjs"]) {
  const text = fs.readFileSync(new URL(`../${file}`, import.meta.url), "utf8");
  assert.doesNotMatch(
    text,
    /raw\.githubusercontent\.com\/kody-w\/rapp-(?:god|map)\/main\/.*ecosystem-spec\.json/,
    `${file} reintroduced a retired moving mirror URL`,
  );
}

console.log("mirror contract retired; one immutable historical census input");
