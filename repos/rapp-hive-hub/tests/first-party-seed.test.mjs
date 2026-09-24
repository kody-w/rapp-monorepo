import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFile } from "node:fs/promises";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const slug = "first-party-rapplication-company";
const starter = path.join(root, "seed-src/organizations", slug, "files");
const teams = ["ceo-office", "product", "design", "engineering", "quality", "release", "support"];
const readJson = async (file) => JSON.parse(await readFile(file, "utf8"));

test("first-party seed retains native pointer-only, unactivated setup and unclaimed work", async () => {
  const seed = await readJson(path.join(root, "public-src/organization-seeds", `${slug}.json`));
  const files = new Map(seed.files.map((file) => [file.path, file.content]));
  const setup = JSON.parse(files.get("initialize.json"));
  assert.deepEqual(seed.dependencies, await readJson(path.join(root, "seed-src/SDK_PIN.json")));
  assert.equal(seed.protocol, "rapp-work/1");
  assert.equal(seed.workspaceProfile, "rapp-work-sdk/1");
  assert.equal(seed.status, "seed-not-activated");
  assert.equal(seed.activation.grantsAuthority, false);
  assert.equal(setup.registration.pointer_only, true);
  assert.equal(setup.registration.same_world_only, true);
  assert.equal(setup.registration.requires_complete_native_plan_and_exact_sha256, true);
  assert.equal(setup.signed_estate_activation, false);
  assert.equal(setup.external_effects_authorized, false);
  assert.deepEqual(setup.workspaces.map((member) => member.id), [...teams, "casework"]);
  assert.ok(setup.workspaces.every((member) =>
    member.scaffold.world_id === setup.organization.scaffold.world_id));
  assert.equal(seed.counts.starterFiles, 21);
  assert.equal(seed.counts.tasks, 21);
  assert.deepEqual(seed.tasks.filter((task) => task.state === "ready").map((task) => task.id), [
    "configure-company"
  ]);
  assert.ok(seed.tasks.every((task) => task.assignee === null && task.completed_evidence.length === 0));
  assert.deepEqual(new Set(seed.tasks.map((task) => task.team)), new Set(teams));
  assert.equal(seed.tasks.at(-1).id, "record-owner-merge");
  for (const team of teams) {
    assert.ok(files.has(`templates/teams/${team}/work/TEAM.md`));
    assert.ok(files.has(`templates/teams/${team}/work/tasks.json`));
  }
});

test("first-party pipeline requires independent verification, separate decision, and owner merge", async () => {
  const gates = await readJson(path.join(starter, "data/pipeline-gates.json"));
  const persona = await readJson(path.join(starter, "templates/founder-ceo.json"));
  assert.equal(gates.executable, false);
  assert.equal(gates.authority, "none");
  assert.deepEqual(gates.stages.map((stage) => stage.id), [
    "idea", "spec", "build", "internal-release", "dogfood", "feedback", "iterate",
    "ship-decision", "promote"
  ]);
  const stages = new Map(gates.stages.map((stage) => [stage.id, stage]));
  for (const stage of stages.values()) {
    assert.ok(teams.includes(stage.owner));
    assert.ok(stage.next.every((next) => stages.has(next)));
    assert.ok(stage.gates.every((gate) => Object.hasOwn(gates.gates, gate)));
  }
  assert.deepEqual(stages.get("iterate").next, ["build"]);
  assert.deepEqual(stages.get("ship-decision").gates, [
    "independent-verification", "separate-decision", "owner-policy"
  ]);
  assert.deepEqual(gates.separation.verifiers_distinct_from, ["builders", "founder_ceo"]);
  assert.deepEqual(gates.separation.decider_distinct_from, ["builders", "founder_ceo"]);
  assert.equal(gates.separation.separate_decision_record_required, true);
  assert.equal(gates.separation.decision_after_verification, true);
  assert.equal(gates.terminal_completion.actor, "owner");
  assert.equal(gates.terminal_completion.event, "owner-merged-pr");
  assert.equal(gates.terminal_completion.automated_merge, false);
  assert.ok(Object.values(gates.claims).every((value) => value === false));
  assert.equal(persona.persona.display_name, null);
  assert.equal(persona.role_bindings.founder_ceo, null);
  assert.equal(persona.decision_rights.self_approval, false);
  assert.equal(persona.decision_rights.direct_publication, false);
  assert.equal(persona.decision_rights.merge, false);

  const candidate = await readJson(path.join(starter, "templates/candidate-manifest.json"));
  assert.deepEqual(Object.keys(candidate.subject_sha256), gates.subject_fields);
  assert.ok(Object.values(candidate.subject_sha256).every((value) => value === null));
  const decision = await readJson(path.join(starter, "templates/decision-receipt.json"));
  assert.equal(decision.decision, null);
  assert.equal(decision.separate_decision_record_reference, null);
  assert.equal(decision.decision_requires_separate_receipt, true);
  assert.equal(decision.authenticated_acceptance, false);
  const promotion = await readJson(path.join(starter, "templates/promotion-request.json"));
  assert.equal(promotion.status, "blocked");
  assert.equal(promotion.privacy_findings, null);
  assert.equal(promotion.owner_merge_reference, null);
  assert.equal(promotion.automatic_merge, false);
  assert.equal(promotion.publication_observed, false);
});

test("new seed locators target this distribution without rewriting upstream seed provenance", async () => {
  const declaration = await readJson(path.join(root, "public-src/skill-declarations", `seed-${slug}.json`));
  const prefix = "https://kody-w.github.io/rapp-hive-hub/api/hive-hub/v1/source/";
  assert.equal(declaration.extensions.seed.url, `${prefix}organization-seeds/${slug}.json`);
  assert.equal(
    declaration.learning.artifacts.find((artifact) => artifact.role === "examples").url,
    declaration.extensions.seed.url
  );
  const dialbook = await readJson(path.join(root, "skills/hive-hub/registry/public-dialbook.json"));
  const record = dialbook.records.find((item) => item.aliases.includes(slug));
  assert.equal(record.locator, `${prefix}skill-declarations/seed-${slug}.json`);
  const upstream = await readJson(path.join(
    root, "public-src/skill-declarations/seed-product-launch-company.json"
  ));
  assert.equal(upstream.extensions.seed.url,
    "https://kody-w.github.io/hive-hub/api/hive-hub/v1/source/organization-seeds/product-launch-company.json");
});

test("first-party offline reference passes its synthetic standard-library acceptance suite", () => {
  const result = spawnSync("python3", ["-B", path.join(starter, "reference/test_checklist.py")], {
    cwd: starter,
    encoding: "utf8",
    timeout: 30000
  });
  assert.ifError(result.error);
  assert.equal(result.status, 0, result.stdout + result.stderr);
  assert.match(result.stderr, /Ran 15 tests/);
  assert.match(result.stderr, /\bOK\b/);
});
