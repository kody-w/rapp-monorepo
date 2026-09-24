import { canonicalJson, publicUrl, sha256Bytes } from "./canonical.mjs";

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function descriptor(filePath, digest, siteBaseUrl) {
  return { path: filePath, ref: `sha256:${digest}`, url: publicUrl(siteBaseUrl, filePath) };
}

// A boot document packs one catalog seed as a RAPP/1 organism Egg (payload kind rapp-seed-boot/1) that a standard
// RAPP Brainstem hatches with the published hatcher. It is inert: hatching grants nothing, and SeedRunner activates
// only the plan whose exact digest the owner approves.
export async function writeOrganizationSeedBoots(writer, entries, { apiPath, siteBaseUrl, seeds, hatcher }) {
  const boots = new Map();
  const bySlug = new Map([...seeds.values()].map((seed) => [seed.document.slug, seed]));
  for (const entry of entries ?? []) {
    const boot = entry.document;
    assert(
      boot.kind === "organization-seed-boot" && boot.schema === "hive-hub-organization-seed-boot/1" &&
      boot.classification === "public-synthetic" && boot.status === "boot-not-hatched" &&
      boot.hatch?.grantsAuthority === false && /^[a-z0-9-]+$/.test(boot.slug),
      "Invalid organization seed boot boundary"
    );
    const seed = bySlug.get(boot.slug);
    assert(seed, `Boot ${boot.slug} names no published organization seed`);
    assert(!boots.has(boot.slug), "Duplicate organization seed boot");
    assert(boot.seed.archiveSha256 === seed.document.archive.sha256, `Boot ${boot.slug} is bound to a different seed archive`);
    assert(
      boot.egg.variant === "organism" && boot.egg.payloadKind === "rapp-seed-boot/1" &&
      /^rappid:@hive-hub\/[a-z0-9-]+:[0-9a-f]{64}$/.test(boot.egg.rappid) && /^[0-9a-f]{64}$/.test(boot.egg.address),
      `Boot ${boot.slug} egg identity is invalid`
    );
    const eggBytes = Buffer.from(boot.egg.base64, "base64");
    assert(
      eggBytes.length === boot.egg.bytes && eggBytes.toString("base64") === boot.egg.base64 &&
      sha256Bytes(eggBytes) === boot.egg.sha256,
      `Boot ${boot.slug} egg commitment mismatch`
    );
    assert(
      boot.organ?.name === "SeedRunner" && /^[0-9a-f]{64}$/.test(boot.organ.sha256) &&
      boot.brainstem?.hatcher?.sha256 === hatcher.sha256 && boot.brainstem.hatcher.path === hatcher.path,
      `Boot ${boot.slug} does not name the published hatcher and organ`
    );
    const eggPath = `${apiPath}/seed-boots/downloads/sha256/${boot.egg.sha256.slice(0, 2)}/${boot.egg.sha256}.egg`;
    await writer.write(eggPath, eggBytes);
    const egg = {
      ...descriptor(eggPath, boot.egg.sha256, siteBaseUrl),
      bytes: eggBytes.length,
      sha256: boot.egg.sha256,
      address: boot.egg.address,
      rappid: boot.egg.rappid,
      mediaType: "application/zip"
    };
    const { base64: _omitted, ...eggFields } = boot.egg;
    const document = { ...boot, egg: { ...eggFields, ...egg } };
    const bytes = Buffer.from(canonicalJson(document));
    const digest = sha256Bytes(bytes);
    const filePath = `${apiPath}/seed-boots/sha256/${digest.slice(0, 2)}/${digest}.json`;
    await writer.write(filePath, bytes);
    boots.set(boot.slug, { slug: boot.slug, document, digest, descriptor: descriptor(filePath, digest, siteBaseUrl), egg });
  }
  for (const slug of bySlug.keys()) assert(boots.has(slug), `Organization seed ${slug} has no Brainstem boot`);
  return boots;
}
