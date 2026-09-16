# Crow Audio Carrier v1 preferred-offset source and candidate review — 2026-09-11

- Reviewer: independent judgment agent, preferred-source-review
- Context given: fresh, focused, noncanonical source/candidate review; read-only packet
- Source commit: `4c443c4f02d48bd575b4c1d9618b0e651f27562b` (informational base plus supplied uncommitted preferred-offset delta)
- Current board SHA-256: `0ab5b6dae425074f2515dc3c3d737e56f2292d83140590dca592b7b964e73090`
- Proposed board SHA-256: `23bd10096eb279c23b10ac29cb7057faadb8bc2a22544fa4c697ee58495dd93b`
- Subject raw / semantic SHA-256: `9216c9b513ed73f2a96fd04a2ea7af98e167c97523c21da7a9d8cebd2b259fe0` / `defa1e96afd083a964dfa6fb97b1e83c7a7c1577a225ead8b662b0355c57689f`
- Preferred-offset code capability verdict: **SOUND**
- Proposed source/candidate verdict: **DEFECTIVE**
- Physical-label verdict: **DEFECTIVE**
- Locator candidate verdict: **SOUND**
- Overall adoption verdict: **DEFECTIVE — do not adopt these two offsets or this native candidate as-is**
- Design-rules SHA-256: unavailable for this partial, noncanonical proposed-source review; no digest is guessed

## Scope and limits

This report judges only the new generic `silk.refdes.preferred_offsets` capability, its supplied tests/contracts, the exact current-to-proposed native delta, the two resulting reference labels, and the proposed 25-page locator substitution. It does not regenerate a board, propose another offset, edit live source, assess routing, or claim a full-board render review. The 306 unchanged visible reference labels and all other unchanged native geometry inherit the prior evidence; no current-placement SOUND claim is made.

## Code and source capability

The generic capability is sound. `preferred_offsets` is an optional exact-refdes map. The implementation rejects non-maps, empty or non-string keys, unknown/wildcard/hole refs, empty/oversized lists, malformed pairs, booleans, non-numbers, nonfinite values, duplicates, and distances beyond the existing ordinary-offset radius. Per-ref preferred pairs are prepended to the same four size/rotation poses. `_place_owned` still performs collision checks, frame checks, owned-first phase 1, and measured minimum-deficit phase 2. Missing and empty mappings preserve prior behavior.

The supplied final evidence is discriminating: the actual pre-feature producer is RED at 0/3 new tests; the implemented producer is GREEN at 6/6 focused tests; and the full generic suite is 65/65 with 39 known-bad fixtures. The first 5/6 GREEN was an invalid degraded-fixture offset colliding with a pad; changing the test offset from -1 to -1.5, without a production-code change, produced the final 6/6 result. The tests meaningfully cover native recovery without moving other fields or physical geometry, empty-map equality, collision rejection, explicit degradation reporting, and 16 hostile malformed cases.

The proposed floorplan source adds only `R_FILT1P: [[-9.6, 3.1]]` and `R_VMID2_BOT: [[1.1, -4.6]]`. The locator source removes `R_FILT2P` and adds `C_VDDA2_10N`; contracts are byte-identical. Although the generic mechanism is sound, the proposed source is defective because both selected offsets produce labels without acceptable visual ownership.

## Exact native delta and checks

Independent textual comparison found exactly two changed native `Reference` fields: `R_FILT1P` and `R_VMID2_BOT` change from hidden placeholder positions to visible 0.55 mm, 90-degree fields with 0.1125 mm stroke. No other line in the board changes. The candidate contains 340 footprint blocks and 1002 pad blocks, consistent with the supplied exact native physical-pin projection equality and unchanged local-zone modes. Hidden references fall from 27 to 25, solely because those two fields become visible.

The supplied refilled DRC has 0 violations, 499 unrouted connections, and 0 schematic-parity findings; the owning placement check passes. These establish collision and native-integrity properties, but they do not establish readable ownership.

## Physical-label judgment

`R_FILT1P` is **DEFECTIVE**. Its glyphs are legible and collision-free, but the vertical label is 10.088111 mm from its own part and 8.556285 mm from `R_CFG2`, a 1.531826 mm ownership deficit. In the actual F.Silk/F.Fab/pad neighborhood it sits among unrelated VMID/ADC labels while its 1206 body is far to the upper right. There is no leader or other unambiguous association. Its 374 collision-free candidates and zero owned candidates do not cure that visual ambiguity.

`R_VMID2_BOT` is **DEFECTIVE**. Its glyphs are legible and collision-free, but the label is placed above the narrow gap between the adjacent, visually identical `R_VMID2_BOT` and `R_VMID2_TOP` 0603 bodies. It is 4.729694 mm from its owner and 4.669047 mm from `R_VMID2_TOP`, so it is 0.060647 mm closer to the wrong part. The actual native crop confirms that the tiny deficit corresponds to a real ambiguous alignment, not harmless numeric noise. The explicit `_BOT` text distinguishes the electrical name but does not identify which of the adjacent physical packages it owns. Its 53 collision-free candidates and zero owned candidates therefore do not support adoption.

`C_VDDA2_10N` has zero collision-free slots under the corrected 0.1125 mm-stroke measurement and appropriately remains hidden with a locator page.

## Locator candidate judgment

The locator candidate is sound and internally bound to the proposed PCB bytes. Its declared 333 references equal 333 unique locator parts and 995 locator pad objects; the native board has 340 footprints and 1002 pads. The BOM has 51 rows expanding to 300 unique fitted refs, and the CPL has the same 300 unique refs. The remaining 33 locator refs are the expected non-BOM connectors, fuse, large capacitors, ADC, and related board items, and every BOM/CPL ref is present in the locator.

The candidate hidden set, configured exception set, and page-reference set are exactly the same 25 unique refs. Pages are numbered 1–25 without gaps, all page paths are unique and manifested, and the manifest has 28 unique members. For all 25 omissions, the configured ref, value, MPN, LCSC, X/Y, rotation, side, and every pad-number/net pair exactly match the locator data. The substitution is exact: 24 prior exceptions remain, visible `R_FILT2P` is removed, and hidden `C_VDDA2_10N` is added. The full 25-page contact sheet is visually consistent, and page 5 clearly identifies `C_VDDA2_10N`, its exact body, numbered pads, 3V3_ADC/GND nets, coordinates, rotation, MPN, LCSC code, board hash, and page denominator.

This locator judgment does not turn the physically defective two-label candidate into a release. The preview remains a noncanonical candidate artifact.

## Required disposition

Do not adopt the proposed preferred offsets or promote board `23bd1009…` as the carrier placement candidate. Retain the generic `preferred_offsets` capability if desired, then select a physically unambiguous treatment for both references and repeat the ordinary source tests, canonical renewal, current-pin, render, locator, layout, route, and release gates. This report makes no carrier-release claim.
