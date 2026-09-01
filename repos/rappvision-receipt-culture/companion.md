# Receipt Culture companion record

## WHAT IT IS

`receipt-culture-one-receipt` is a paired publication by Emi Chen, a
fictional/synthetic design critic. A 24-second silent editorial film introduces
one synthetic provenance receipt; its live replay lets a newcomer perform the
same audit.

## WHY IT MATTERS

A convincing surface is not evidence. The receipt makes five claims—subject,
artifact hash, policy, signer key, and signature—and demonstrates why changing
one signed field is enough to stop trust.

## LOCATION

- Guided film: `media/receipt-culture-one-receipt.mp4`
- Alternate encode: `media/receipt-culture-one-receipt.webm`
- Live audit: `live/index.html`
- Thumbnail: `thumbs/receipt-culture-one-receipt.svg`
- Manifest: `channel.json`
- Evidence record: `evidence.json`

## EVIDENCE

Both modes use the same exact comparison. The canonical `artifact_sha256` ends
in `9`; the counterfeit ends in `8`. Every other receipt field remains
unchanged. The counterfeit is rejected because the unchanged synthetic
signature does not bind the changed payload. Reset restores the hidden baseline
while canonical acceptance remains the established positive result.

The MP4 and WebM codec probes, dimensions, durations, byte sizes, and SHA-256
fingerprints are bound in `evidence.json`.

## BOUNDARIES

All names, receipts, hashes, keys, signatures, institutions, typography,
graphics, and interaction data are authored synthetic evidence. The pilot
teaches receipt comparison only. It authenticates no real artifact, person,
institution, issuer, policy, or cryptographic key.

No external media, private data, copied review, customer material, citation, or
real-person impersonation is used.

## KNOWN COMPROMISES

The film is intentionally silent and relies on large editorial copy rather than
narration. The signature and verifier are pedagogical synthetic representations,
not a production cryptographic implementation. The replay audits one bounded
single-field mutation rather than every possible receipt failure.

## NEXT DECISION

Watch the guided film for orientation, then choose **Try live replay** and run
the five stages in order: reveal, compare, identify, reject, and Reset audit.
