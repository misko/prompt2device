# Reject-first source plan for a channel-8 multi-cell partition

**Research-only implementation plan.**  This applies the checker’s
`physical_cells` semantics to the exact 15-footprint candidate SHA-256
`d0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7`.
It does not alter the board, canonical source, P1 status, or P2 status.

## Three different authorities

`analog_ch8` remains the one **functional owner** of its 36 refs and the
`ADC8N` endpoint owner in `modular_plan.json`: `C_ADC_AC8N1.2`,
`C_ADC_AC8N2.2`, and `C_ADC_CM8N.1` (lines 985--1004).  It must not be
reassigned merely to fit a pocket.

A **physical cell** is a separate source-region id tied to that functional
owner through a `physical_cells` row.  The checker requires each owner’s refs
exactly once across its cells, contains each assigned native envelope/pad in
that one cell, and permits empty same-owner transit cells only when they
positive-edge-connect the occupied cells
(`skills/kicad-pcb/scripts/p1_corridor_capacity.py:1292--1329`).  A cell may
not overlap any foreign source region (1330--1338).  A supported coarse
witness or integration face may name a physical-cell id while its `block`
remains `analog_ch8`.  The current unresolved-branch checker instead tests
the primary functional region `regions['analog_ch8']`; it has no
`physical_cell_id` field.

## Complete channel-8 pocket denominator

The following is the minimum useful *ownership bucket* census.  It enumerates
all 36 refs once, but deliberately does not claim that a bucket hull is already
a valid rectangular cell.  Before authoring source, each bucket must be split
again wherever its rectangle would contain an unassigned body/pad.

| Candidate pocket | Refs |
| --- | --- |
| `analog_ch8_connector` | `J8` |
| `analog_ch8_ch7_ingress` | `R_IN8P`, `U_ESD8` |
| `analog_ch8_audio_edge` | `C_ISO8`, `C_SPOKE_DVDT8`, `C_SPOKE_OUT8`, `R_SPOKE_UVLO8` |
| `analog_ch8_cap_iso_local` | `C_A8P`, `C_ADC_AC8N1`, `C_FILTER8N1`, `C_FILTER8N2`, `C_FILTER8P2`, `C_SPOKE_IN8`, `R_B8P`, `U_ISO8` |
| `analog_ch8_core` | `C_A8N`, `C_ADC_AC8N2`, `C_ADC_AC8P1`, `C_ADC_AC8P2`, `C_ADC_CM8N`, `C_ADC_CM8P`, `C_FB8N`, `C_FB8P`, `C_FILTER8P1`, `C_OPA8`, `R_ADC_PD8N`, `R_ADC_PD8P`, `R_B8N`, `R_IN8N`, `R_OUT8N`, `R_OUT8P`, `R_SPOKE_ILIM8`, `R_X8N`, `R_X8P`, `U_AFE8`, `U_SPOKE8` |

Each occupied pocket requires a region key and a `physical_cells` row with
`owner_block: analog_ch8`.  Disconnected occupied pockets are permitted;
declare a no-ref transit row only when a needed transit region is present, in
which case it must edge-connect to an occupied same-owner cell.
`placement.patterns` must use
the physical cell id for each assigned ref, because the checker rejects a
pattern/cell disagreement.  The current broad `analog_ch8` rectangle cannot
remain as an overlapping catch-all: its id must become one occupied cell or be
replaced by a new nonoverlapping cell layout.

## Neighbor recuts that are unavoidable

The current regions are `analog_ch7=[157,42,179,84]`,
`analog_ch8=[179,42,201,84]`, `audio_clock_tdm=[145,72,190,99.84]`,
`usb_vbus_sense=[195,62,215,82]`, and `usb_frontend=[200,29,238.5,40]` mm.
Each following source authority must be revised together with its channel-8
pocket; changing an analog rectangle alone violates the checker’s foreign
region rule.

* **USB VBUS sense:** the cap cell needs the measured right divider.  `x=202.105`
  mm is SOL’s bounded screen: 0.56 mm from `U_AFE8`, 1.110 mm from the cap,
  and 3.720 mm before `R_VBUS_B`.  A paired recut makes
  `analog_ch8_cap_iso_local.x2=usb_vbus_sense.x1=202.105`; it is geometry
  only, not route width or return credit.
* **Audio/TDM:** `C_ISO8`, `C_SPOKE_DVDT8`, `C_SPOKE_OUT8`,
  `R_SPOKE_UVLO8`, and `U_ESD8` enter the current audio rectangle.  Their
  exact envelopes must be placed in channel-8 edge cells while
  `audio_clock_tdm` is partitioned so none of those cells overlaps its residual
  region.  Moving only `audio_clock_tdm.y1` is not authorized: its own native
  members need a simultaneous containment screen.
* **Channel 7:** `R_IN8P=[178.725,58.685,180.675,59.715]` and
  `U_ESD8=[178.755,70.210,181.245,72.395]` cross x=179.  A paired CH7 ingress
  recut is needed.  It cannot simply move the divider to 178.725, because
  channel-7 `C_FILTER7P1=[175.655,65.375,179.145,67.425]` then becomes the
  corresponding foreign-side containment debt.
* **USB frontend / fixed connector:** fixed `J8` has native envelope
  `[198.875,19.955,216.268081,34.495]` and intersects the *source*
  `usb_frontend` rectangle despite not intersecting a USB footprint.  It needs
  an `analog_ch8_connector` pocket plus a paired USB-frontend partition.  A
  single y shift of USB frontend is insufficient: `U_USB_CC_ESD` and
  `U_USB_VBUS_ESD` occupy y=29.010--31.195, while `U_USB_ESD` begins at
  y=35.255.  The USB block therefore needs at least separated upper-east and
  lower cells (and, if needed, its own transit) before the J8 pocket can be
  exclusive.  J8 remains fixed and functionally analog_ch8.

## Reject-first authoring and measurement order

1. In an isolated source packet, add all cell region keys, complete
   `physical_cells` rows, exact pattern-to-cell assignments, and only the
   necessary paired foreign-region partitions.  Keep the functional
   `modular_plan.json` ownership and all 27 fixed poses unchanged.
2. Run `_physical_cells` before any corridor declaration.  Reject on a missing
   or duplicate member, a noncontained envelope/pad, any unassigned body in a
   cell, a pattern mismatch, a foreign-region overlap, or disconnected transit.
3. Keep the unresolved ADC8N tree's endpoint containment check against the
   primary `regions['analog_ch8']`; the current branch schema cannot bind those
   endpoints to a physical cell.  Use physical-cell ids only on checker-
   supported witnesses/integration faces, with P2 pad-to-face and filled-return
   obligations; do not use a virtual face as pad-access proof.
4. Recheck all board invariants: original/four-part ancestry, 27 fixed refs,
   outline, layers, rotations, pad identity/net/layer, native envelope/pad
   collisions, and DRC delta.  Then require actual cap/ISO entry, route and
   continuous filled return before P2 is considered.

The unfilled GND zone, 499 unconnected items, unresolved ADC8N tree, and no
native route remain blockers.  A passing source partition is still
`INCOMPLETE` and grants no corridor capacity, P1 acceptance, or P2 acceptance.
