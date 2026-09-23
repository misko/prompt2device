# TMUX4827 YBH B2 POFV profile — implementation scope

**Status:** read-only implementation-scope review, 2026-09-23. No source or native board was changed, no P1 board was generated, and this does not resolve unrelated P1 rules.

## Decision

Keep the existing board floors for ordinary copper and ordinary vias. Add one small, named producer/checker for `TMUX4827_YBH_B2_POFV`; do not attempt to express this through `nets.yaml` netclasses or its generic `scoped_clearances` schema.

The current `via_process` contract is necessary but insufficient. It already supports `protected_geometries`, so it permits the two protected members of the one 0.20-mm drill family: LT3045 `0.50/0.20` and TMUX `0.35/0.20`. `via_process_check.py` verifies fill/cap flags, geometry, the complete protected drill family, and disjoint ordinary 0.30-mm drills. It does **not** bind a 0.35/0.20 via to a particular footprint, pad, net, or count. A 0.35/0.20 protected via elsewhere on GND can pass today.

`generate_rules_generic.py` only reads `rules/nets.yaml`. Its current clearance facility scopes named *areas* and named nets; it cannot name an exact reference/pad relationship. A `GND` exception leaks to all GND; an `insideArea` exception alone binds a rounded placement coordinate and matches any item overlapping the area. Neither is an admissible identity.

Use a deliberately limited extension under `assembly.yaml:via_process`, for example a `named_profiles` entry (spelling may be finalized with the producer):

```yaml
via_process:
  # Existing protected_geometries and drill-family selector remain unchanged.
  named_profiles:
    - id: TMUX4827_YBH_B2_POFV
      kind: tmux4827_ybh_b2_pofv_v1
      tier: jlc_4layer_advanced
      finish: ENIG
      refs: [U_ISO1, U_ISO2, U_ISO3, U_ISO4, U_ISO5, U_ISO6, U_ISO7, U_ISO8]
      pad: "5"                 # B2 under retained numeric ball map
      net: GND
      expected_count: 8
      geometry:
        pad_diameter_mm: 0.35
        via_diameter_mm: 0.35
        drill_mm: 0.20
        annulus_mm: 0.075
        mask_opening_mm: 0.25
        paste_opening_mm: 0.25
        bga_via_to_pad_gap_mm: 0.10
      process: type_vii_filled_and_capped_pofv
      evidence:
        part: 02_parts/TMUX4827YBHR/part.yaml
        coupon_sha256: 6f39a73aad46444e6b2256ced0b64a1dea5b9792801c3f705f8b691727ce83b6
```

Reject any other `kind`, duplicate ID, empty/duplicate refs, a non-exact eight-ref set, non-`GND` B2, nonnumeric pad 5, non-advanced tier, wrong dimensions, or a coupon/footprint hash that disagrees with the authoritative TMUX part record. Do not become a generic arbitrary POFV exception format. The part record remains the binding source for B2 mapping, footprint hash, and coupon; the checker requires equality of duplicated process geometry rather than accepting either copy.

## Producer boundary

Implement a small dedicated producer adjacent to `via_process_check.py`, then invoke it after `generate_rules_generic.py` and before pre-route native DRC. It owns only this profile's generated `.kicad_dru` rules and eight derived rule areas. Do not bolt it onto `scoped_clearances`, and do not make a hand-preserved foreign DRU block authority.

The producer reads the actual placed board and derives each scope from the selected footprint's actual pad-5 centre and shape. YAML contains no board X/Y values. It serializes deterministic names such as `tmux4827_b2_pofv_U_ISO1`, marks areas/rules producer-owned, replaces only those items on rerun, and fails if the declared pad identity is absent. It never targets by rounded coordinates or nearest-GND matching.

Native KiCad DRC can enforce narrow pad-pair clearance: it has `Reference`, `Pad_Number`, `NetName`, `Type`, and `insideArea`. For each U_ISO reference, emit 0.10 mm only for B2 pad 5 against its four orthogonal same-footprint neighbors (A2/B1/B3/C2 = numeric pads 2/4/6/8), in both A/B orders, pad-only and different-net. This is the cited via-copper-to-BGA-pad relationship. It must not lower B2 clearance to arbitrary tracks, vias, zones, diagonal lands, or other footprints.

KiCad rules can constrain `via_diameter`, `hole_size`, and `annular_width`, but a bare `Via` has no parent footprint/pad identity and native DRC has no fill/cap predicate. The producer may use the eight *derived* areas to let exact B2 vias supersede ordinary size/annulus floors, but that is only a DRC aid. The independent checker is the identity/process authority and must verify area geometry against live pads, so stale/moved areas fail closed.

## Required independent checker: fail closed

Extend `via_process_check.py` or add a narrowly named companion that reads the profile and exact candidate board. It must fail unless all conditions hold:

1. Selected tier is exactly `jlc_4layer_advanced`; exact refs `U_ISO1..8` appear once and carry the retained TMUX footprint identity.
2. At each ref, numeric pad 5 is B2/GND, an undrilled top SMD Ø0.35 land with Ø0.25 mask and paste openings; TI ball map, coupon, and native footprint hashes agree with `part.yaml`.
3. Exactly one PCB via is co-located with that pad centre within checker tolerance, not a coordinate list; it is GND, F.Cu-to-B.Cu, Ø0.35/Ø0.20, 0.075 annulus, and both filled and capped. Missing, doubled, offset, wrong-net/layer/size, ordinary, or partial state fails.
4. Board count is exactly eight such TMUX B2 vias. Every protected Ø0.35/0.20 via is one of them; existing LT Ø0.50/0.20 sites remain under the complete drill-family check. Ordinary Ø0.20 stays forbidden and ordinary Ø0.30 stays unprotected.
5. Each B2 has all four native 0.40-mm orthogonal neighbors with Ø0.25 lands and exact 0.10-mm copper gap. The native DRU rule checks this during DRC; checker validates profile geometry.
6. Generated area membership is one-to-one with the eight exact vias; no other item/via gets a local exemption. Reject missing, stale, duplicate, hand-authored, or foreign-member areas.
7. Generated order note retains fill/cap, complete protected 0.20 drill family, ordinary 0.30 exclusion, and explicit uploader confirmation. Preserve existing order-time uploader/CAM/PCBA acceptance uncertainty; add no new supplier-DFM prerequisite before P1.

Add positive coverage plus mutations for wrong ref/pad/net, diameter/drill, missing/extra via, no fill/no cap, shifted via, bad neighbor gap, stale area, extra protected Ø0.35/0.20 GND via, and a global/scoped-GND DRU leak. Existing `t1_via_process.py` mixed-geometry tests remain necessary but do not prove profile identity.

## Limits

This profile grants only eight Type-VII/POFV B2 sites at `0.35/0.20`, 0.075-mm ring, Ø0.25 mask/paste, and 0.10-mm B2-neighbor gap. It does not relax ordinary clearance, annulus, or via floors; authorize TPS62825 DMQ or USB4105 exceptions; establish CAM, stencil, populated-board, audio, or supplier acceptance; or claim all P1 rules resolved.

## Evidence inspected

* `01_docs/research/2026-09-23-package-process-reassessment-terra.md`
* `02_parts/TMUX4827YBHR/part.yaml` and qualification coupon/README
* `03_src/rules/assembly.yaml`, `nets.yaml`, and `contracts.md`
* `skills/jlcpcb-fab/scripts/via_process_check.py`
* `skills/kicad-pcb/scripts/generate_rules_generic.py` and `escape_check.py`
* Local KiCad 10 custom-DRC reference (`/usr/share/doc/kicad/help/en/pcbnew.html`)
