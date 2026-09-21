import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { canonicalJson, normalizeRelativePath, sha256Bytes } from "./lib/canonical.mjs";
import { UPSTREAM_COMMIT, UPSTREAM_SITE_URL } from "./lib/distribution.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const manifestPath = path.join(root, "public-manifest.json");
const manifestBytes = await readFile(manifestPath);
const manifest = JSON.parse(manifestBytes);
const objects = new Map();
const writes = new Map();
const upstream = (relative) => execFileSync(
  "git", ["show", `${UPSTREAM_COMMIT}:${relative}`],
  { cwd: root, maxBuffer: 2 * 1024 * 1024 }
);

function visit(value) {
  if (!value || typeof value !== "object") return;
  if (value.path && value.ref && value.url && !objects.has(value.path)) {
    assert.equal(normalizeRelativePath(value.path), value.path);
    assert.match(value.path, /^api\/hive-hub\/v1\/[a-z0-9/-]+\/[a-f0-9]{64}\.json$/);
    assert.equal(value.url, `${UPSTREAM_SITE_URL}/${value.path}`);
    assert.ok(objects.size < 128, "Upstream history exceeds the bounded import");
    const bytes = upstream(value.path);
    assert.equal(value.ref, `sha256:${sha256Bytes(bytes)}`);
    const document = JSON.parse(bytes);
    assert.equal(bytes.toString("utf8"), canonicalJson(document));
    objects.set(value.path, { bytes, document });
    visit(document);
  }
  for (const child of Object.values(value)) visit(child);
}

visit(JSON.parse(upstream("api/hive-hub/v1/receipts/index.json")).receipts);
const historicalDigests = new Set(manifest.entries
  .filter((entry) => ["historical-object", "historical-receipt"].includes(entry.kind))
  .map((entry) => entry.sha256));
for (const { bytes, document } of objects.values()) {
  const digest = sha256Bytes(bytes);
  if (historicalDigests.has(digest)) continue;
  const relative = `historical/upstream-distribution/${digest}.json`;
  const coreCard = document.kind === "ai-join-card" && document.schema_version === 1;
  manifest.entries.push({
    classification: "public",
    id: `historical-${coreCard ? "core-card" : "upstream"}-${digest}`,
    kind: document.kind === "receipt" ? "historical-receipt" : "historical-object",
    path: relative,
    sha256: digest
  });
  writes.set(`public-src/${relative}`, bytes);
}
const receiptPath = "receipts/0004-rapp-distribution.json";
const receiptBytes = await readFile(path.join(root, "public-src", receiptPath));
if (!manifest.entries.some((entry) => entry.path === receiptPath)) {
  manifest.entries.push({
    classification: "public",
    id: "publish-rapp-distribution-0004",
    kind: "receipt",
    path: receiptPath,
    sha256: sha256Bytes(receiptBytes)
  });
}
manifest.entries.sort((left, right) => left.id.localeCompare(right.id));
writes.set("public-manifest.json", Buffer.from(canonicalJson(manifest)));
const plan = {
  upstream: UPSTREAM_COMMIT,
  manifestSha256: sha256Bytes(manifestBytes),
  writes: [...writes].map(([file, bytes]) => ({ path: file, sha256: sha256Bytes(bytes) }))
};
const planId = sha256Bytes(Buffer.from(canonicalJson(plan)));
if (process.argv.length === 2) {
  console.log(canonicalJson({ planId, plan }).trimEnd());
} else {
  assert.deepEqual(process.argv.slice(2), ["--apply", planId], "Approve the exact current import plan");
  for (const [relative, bytes] of writes) {
    const target = path.join(root, relative);
    await mkdir(path.dirname(target), { recursive: true });
    await writeFile(target, bytes, { flag: relative === "public-manifest.json" ? "w" : "wx" });
  }
  console.log(`Preserved ${objects.size} pinned upstream objects; applied ${planId}.`);
}
