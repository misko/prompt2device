# Start here — Crow r6 quote check

Use existing branch `codex/crow-jlc-source-review-20261030`, not main.
First preserve any uncommitted MacBook work. From a clean checkout on that branch:

```sh
git pull --ff-only origin codex/crow-jlc-source-review-20261030
python3 projects/crow-array/order-readiness/substitutions-20261101/verify_public.py
```

The expected result is `QUOTE_PAYLOAD_INTEGRITY_PASS` for 94 files. This checks
the exact independently reviewed package hash; it does not check current stock,
rerun engineering, approve the factory preview or authorize manufacturing.

Upload/use the following pairs from
[`quote-draft/r6-2c8p-substitutions`](../quote-draft/r6-2c8p-substitutions/):

| Job | Gerbers | BOM | CPL | Fabricate / assemble |
|---|---|---|---|---|
| Carrier | `carrier-gerbers.zip` | `carrier-bom.csv` | `carrier-cpl.csv` | 5 / 2 |
| Pod | `pod-gerbers.zip` | `pod-bom.csv` | `pod-cpl.csv` | 10 / 8 |

BOM/CPL quantities are per one board. The Gerbers/CPLs are unchanged from r5;
the BOMs contain four reviewed new identities. Do not mix r5 and r6 BOMs or
multiply quantities inside the uploads. Home parts remain two Picos, eight
microphones and eight buzzers.

Follow the [full quote-only checklist](HANDOFF.md), especially:

1. Check exact C544855, C28323, C5362585 and C89632 matching, usable stock and
   actual gross demand for both jobs. Public observations are dated, not allocated.
2. Get exact Global Sourcing/approved-consignment information for the retained
   Littelfuse fuse, CTS oscillator and RECOM module. Blank BOM codes are required
   parts awaiting source matching, NOT instructions to omit them.
3. Record all component, assembly, setup/stencil, sourcing, shipping and tax
   charges, fees, dates and unknowns. Review complete placements and preserve the
   existing stack/rail/stencil/assembly holds and no-auto-confirm preferences.
4. Stop before purchases, payment, reservations, non-cancelable pre-orders,
   vendor messages or production approval. If JLC cannot quote without inventory
   acquisition, save the exact blocker; do not omit required placements to proceed.

## Publication boundary

The published package is byte-identical to the locally reviewed r6; manifest
SHA-256 is `c01cb5e90b31738b6afd0102aca1b22ae3322c1e82f17fbe5492c8f198f19099`.
Author-written reviews, observed stock JSON, derived calculations, native exports
and validation records accompany it. Raw manufacturer PDF/HTML research archives
and incidental KiCad preference files are retained on the server, excluded from
GitHub; their hashes/URLs remain in the source records. They are not needed for
uploading or verifying the exact quote payload.

The historical `VALIDATION.md`, generator replay command and full-project
engineering replay test require the two external research artifacts named in
`adopted-changes.json`. They ran successfully on the server but are NOT standalone
engineering replay instructions for this public checkout. Use `verify_public.py`
for the MacBook integrity check. Missing research is explicitly reported; it is
not fabricated or treated as a completed engineering review.

The full-replay regression case explicitly skips without those two research
artifacts; the other eight generator tests and two public integrity tests run
without them. Three trailing-whitespace warnings in copied native footprint
files are inherited byte-for-byte from the published baseline and intentionally
not reformatted: the reviewed r6 file hashes remain unchanged.
