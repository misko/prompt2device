---
review_stage: pre-route
review_kind: schematic_render
design_verdict: DEFECTIVE
order_verdict: DO-NOT-ORDER
schematic_pdf_sha256: 6a6be131d497e0d2b66f53b97501251a4f37ec3a64b2d4743f9af793b512e54b
netlist_sha256: 7ab8c90f46ff4f25a9af50f43659a6b304e3c15932875519fa916fd018b1d8cc
parts_sha256: 833913d1c3d68cec43ab53f34e63b48cbf0e38bd3ec5a5115abfbaa5e23c2a0e
design_rules_sha256: 8211187b0a0bb0ab38799ade9459944f0226cdf0180a75bcfdb94ca385a1a0c1
helper_path: /tmp/crow-569-schematic-review-packet-20260924-terra-r1/review/pre_route_review_check.py
helper_sha256: b02a6d97feef2436ba71053e676d87e04c726b1ceec92cd92cf8a4b5d25c6b4e
---

# Independent schematic-render handback — 569

This is a noncanonical, read-only handback. It does not accept the design and
does not assess electrical connectivity correctness.

## Bound packet and verification

Reviewed only the frozen packet at
`/tmp/crow-569-schematic-review-packet-20260924-terra-r1`.

- Packet-manifest hash: `4f0ab185237ba22b0b01de0b98241db332d0aad456cb1407d91f932c97cce991`
  for `review/packet-sha256sums.txt`.
- The manifest's own recorded hash is that same value. `sha256sum -c` validates
  every listed payload and reports one expected self-reference failure for
  `review/packet-sha256sums.txt` itself; its actual SHA-256 equals the external
  packet-manifest hash above. No payload mismatch was found.
- PDF: 92 pages, 900 x 607.5 pt, PDF 1.7, unencrypted; PDF SHA-256 is the bound
  value in the front matter. Both old and new supplied 120-dpi render sets have
  92 pages.
- The supplied helper was imported from `helper_path`; the normalized netlist,
  complete 112-part manifest, and semantic rules digests in the front matter
  were recomputed from the frozen subject.

## Coverage and comparison

Full normal-scale visual inspection was completed for new PDF pages **1-92 of
92**. The supplied 120-dpi old/new PNG pairs were freshly compared by SHA-256:
**0/92 identical, 92/92 changed/mismatched, 0 added, 0 removed, and 0 reordered
pages**. Thus every page was inspected rather than carried over. Targeted
240-dpi inspection was additionally completed for held-LDO overview page 4,
supervisors page 14, ADC overview page 32, reset-supervisors overview page 43
and changed-cap detail page 47, and XMOS overview page 57.

Primary overview pages carry coherent `Crow USB Carrier v1` identities,
section headings, page numbers, component/pin/net/value text, and overview-page
references in the detail-page headers. The overviews make the principal
functional sections recognizable: held LDO (4), ADC (32), reset supervisors
(43), XMOS (57), TDM (70), FSYNC (80), and ADC clock control (85). Normal
single-page views of several very dense overview pages remain too small for a
reviewer to use as the detailed source, which is why the accompanying detail
pages are material to this verdict.

## Render defects

**P1 — detail-page tiling is not a reviewable schematic representation.** The
detail pages are literal crops with no continuation arrows, tile map, or usable
cross-page handoff. They frequently cut symbols, labels, nets, and components at
the page edge and leave large areas blank. A reader cannot reconstruct the
intended local circuit from a detail page or determine where a cropped item
continues.

This repeats across all generated detail sets:

- Held LDO: pages 5-13; examples include cropped input/output material on 5-10
  and fragmentary capacitor-only tiles 11-13.
- ADC: pages 33-41; pages 34, 37, and 40 are largely blank/cropped fragments,
  while the two ADC bodies and their bypass banks are split across tiles.
- Reset supervisors: pages 44-52; page 50 (DETAIL 7/9) contains only header
  text and no schematic content, while adjoining tiles cut active symbols and
  rails at their borders.
- XMOS: pages 58-66; the 128-pin device is divided into inaccessible oversized
  yellow-symbol fragments. Page 62 is essentially an unannotated symbol field;
  pages 59, 60, and 65 obscure the usable pin/net context.
- TDM translation: pages 71-79; page 73 is materially blank apart from a cropped
  edge; other pages divide the one IC and its passive network without a
  continuation convention.
- FSYNC shaping: pages 81-84; and ADC clock control: pages 86-89; both retain
  edge-cropped symbols and nets instead of independently readable details.

These are rendering/readability defects, not an assertion about underlying net
connectivity. They nevertheless prevent a human schematic review of component
identities, values, pin/net text, intentional NCs, reference uniqueness, and
cross-page continuity at the required detailed scale. The blank/cropped pages
also invalidate the claimed overview/detail mapping as a usable document
feature. Repair the detail renderer so each detail page includes whole relevant
symbols/nets, continuation references at every crop, and no empty tile; then
regenerate and review the exact PDF.

**P2 — explicit changed-bypass visibility is incomplete in the detail view.**
The new `C_ADC_DIGITAL_OK` 100 nF bypass is explicitly visible and legible on
the reset-supervisors overview (page 43) alongside `N3V3_ADC`; the high-
resolution page-47 tile also shows its reference, value, and ground symbol.
However, page 47 cuts surrounding active material and adjacent connections, so
the deliberately supplied detailed view does not communicate its local intent
as a standalone schematic. This finding does not judge its endpoint
connectivity.

No claim is made that the apparent no-connect labels on intact overview pages
are electrically correct; the tiled render prevents completing the requested
human-facing intentional-NC audit for the affected dense sheets.

## Enduring holds

All enduring holds remain open: source and datasheet authority; cable and
external-interface assumptions; firmware behavior; thermal analysis; physical
fit/placement and routed-board verification; first-article build/test; sourcing
and alternates; and release approval. The earlier ERC warning debt is not
waived. This render failure independently keeps the result at **DO-NOT-ORDER**;
it neither authorizes procurement nor removes any pre-route, placement, routing,
or release gate.
