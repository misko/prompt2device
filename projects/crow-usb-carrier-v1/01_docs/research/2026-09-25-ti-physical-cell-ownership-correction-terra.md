# Correction: functional owner versus physical cells

**Conceptual correction to `0e5ef9fa`; no canonical edit.**  The statement
that a typed candidate must put the complete `analog_ch8` population in one
physical cell was too strong.  It is not a source or checker requirement.
`J8` need not move or change functional owner merely because it is remote from
the channel-8 local placement.

`skills/pcb-design/references/modular-design.md` says every electrical
component has exactly one **block** owner (lines 20--24), then explicitly says
functional ownership does not require physical colocation (lines 61--65).
Its intended remedy is coupled placement/proof groups at the endpoints they
serve, rather than a block-center test.

## What the schema/checker actually requires

`p1_corridor_capacity.py` documents `physical_cells` as optional partitioning
of one modular owner into disjoint named floorplan regions (lines 39--45).  If
the extension is absent, the checker returns an empty cell map (lines
1272--1276); it does not impose physical colocation.

If it is present, the checker requires a different, narrower invariant:

* Each cell's refs are a unique subset of its `owner_block` (1292--1293), and
  each listed footprint envelope and pad is contained in **that cell**
  (1297--1304).
* The owner denominator is complete **across all of that owner's cells**
  (1312--1315), not in any one cell.  Same-owner transit cells contain no refs
  and must positive-edge-connect the occupied cells (1317--1329).
* Every cell must avoid bodies/pads not assigned to it (1305--1308), and its
  rectangle may not overlap any foreign source region (1330--1338).  A pattern
  that assigns a ref to a region must agree with its physical-cell id
  (1302--1304).

Thus an `analog_ch8_connector_pocket` containing fixed `J8`, an
`analog_ch8_local` cell containing the ADC8 cap/ISO neighborhood, and explicit
same-owner transit cell(s) are schema-shaped.  `J8` remains an `analog_ch8`
functional member; no invented cross-block interface is needed just because
it occupies a connector pocket.  A different-block crossing still needs its
own exact interface/handoff and return obligations.

The board already supplies a direct schema example.  In the research source
`2026-09-25-ti-adc-shared-port-probe/requirements.yaml` lines 1330--1350,
functional block `clock_flash_debug` is split into occupied
`clock_flash_debug` and `clock_oscillator_local` cells plus empty
`clock_qspi_transit`.  The corresponding floorplan uses distinct rectangles
and pattern regions (`floorplan.yaml` lines 1135--1148 and 910--920).  This
is the permitted multi-cell model, rather than an exception to ownership.

## Consequence for the two-cell negative result

SOL's `61958e8a` correctly rejects only its stated **two-cell** recut: it
keeps `analog_ch8` as one rectangle and `usb_vbus_sense` as one rectangle,
then finds seven channel-8 members outside/overlapping foreign source regions.
Its `J8` observation is therefore a valid rejection of that reduced model,
not proof that `J8` must move or be functionally reassigned.  The same applies
to the other remote channel-8 attachments.

This correction does not rescue the current placement.  A connector pocket
for `J8` would still need an exclusive rectangle: its native envelope
`[198.875,19.955,216.268,34.495]` intersects the current `usb_frontend`
source region, so that region boundary must be recut before a physical cell
can pass checker lines 1330--1338.  The local cap cell also still needs the
right-divider repair, a complete same-owner cell/transit map, exact endpoint
access, and filled-return proof.  Until those are independently supplied, the
physical-cell concept grants no P1 capacity or P2 acceptance.
