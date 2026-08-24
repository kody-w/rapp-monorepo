import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import { parseCandidateBundleUrl, validateManifest } from '../scripts/validate-manifest.mjs';

const manifest = JSON.parse(readFileSync(new URL('../.ring/manifest.json', import.meta.url)));
test('candidate URL parser accepts only the closed namespace', () => {
  const url = `https://raw.githubusercontent.com/kody-w/openrappter/${'b'.repeat(40)}/candidates/${'a'.repeat(40)}/release/tag-djEuMTMuMA/${'c'.repeat(64)}.tar.gz`;
  assert.deepEqual(parseCandidateBundleUrl(url), { source: 'a'.repeat(40), sha: 'c'.repeat(64) });
  for (const invalid of [`${url}?x=1`, `${url}\n`, url.replace('/release/tag-djEuMTMuMA', ''), url.replace('/release/', '/release/extra/'), url.replace('tag-djEuMTMuMA', '..'), url.replace('raw.githubusercontent.com', 'example.com')]) assert.throws(() => parseCandidateBundleUrl(invalid));
});
test('current alpha manifest is closed and valid', () => {
  validateManifest(manifest, 'alpha', new Date('2026-08-23T20:00:00Z'));
});
test('repository and field injection fail closed', () => {
  assert.throws(() => validateManifest({ ...manifest, extra: true }, 'alpha'));
  assert.throws(() => validateManifest({ ...manifest, source: { ...manifest.source, repository: 'evil/repo' } }, 'alpha'));
});
test('future and published-without-install fail closed', () => {
  assert.throws(() => validateManifest({ ...manifest, promoted_at: '2999-01-01T00:00:00Z' }, 'alpha'));
  assert.throws(() => validateManifest({ ...manifest, status: 'published', reason: null }, 'alpha'));
});
test('promotion receiver pulls immutable requests with only its GITHUB_TOKEN', () => {
  const workflow = readFileSync(new URL('../.github/workflows/apply-promotion.yml', import.meta.url), 'utf8');
  assert.doesNotMatch(workflow, /RING_AUTHORITY_TOKEN|repository_dispatch|secrets\./);
  assert.match(workflow, /apply-request\.yml@813eafd957982e2c64d318caa12be3e494a1c7e4/);
  assert.match(workflow, /contents: write/);
  assert.ok(workflow.includes("request_sequence:\n        required: false\n        type: string\n        default: '0'"));
  assert.ok(workflow.includes("requested_sequence: ${{ inputs.request_sequence || '0' }}"));
});
