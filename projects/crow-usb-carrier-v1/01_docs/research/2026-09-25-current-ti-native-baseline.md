# Current TI source: private native baseline and Q_PRE comparison

**Research diagnostic, no P1/P2/P3, connector FULL, release, fabrication or
order claim.** The producer in D14 used the current authored floorplan SHA-256
`c2a6562c1a012e692109b852158af2ef73a432f712a62ae87cbd8e49c4c4ecd6`
and the hash-bound TI prototype circuit/netlist. Its final private receipt is
`06_build/prototype_board_diagnostic/current-ti-baseline-final-20260925/receipt.json`.
The exact final PCB SHA-256 is
`c5229350807edd85ce95eadd4ec8e4190941b0dd27edcf0a54a6defda145e6b8`.

The archived diagnostic floorplan differs from current source by exactly the
reviewed `Q_PRE` move `(46.0,106.85,0°) → (46.0,107.15,0°)`. A native
comparison of the archived board against the new board found the same 569
reference names and 1,872 pads, with `Q_PRE` the sole moved footprint. Both
generated rule sidecars have the same pinned effective hashes as the archived
profile: `.kicad_pro` `7977bc9e…6087ddc094` and `.kicad_dru`
`00ab83d8…4f9c3b0a`. The producer checked all 107 named effective DRU rules
against the pinned seed; no extra retained rule appeared.

Current native `kicad-cli pcb drc --severity-all --refill-zones
--schematic-parity --format json` reports **0 violations, 499 unconnected
items, and 0 schematic parity issues**. `count_parity.py` passes 569/569 for
circuit and netlist against PCB; `pin_map_check.py` passes 799 declared pin
identities across 79 multi-pin references. The board has no accepted signal
routing or saved filled-return proof.

Using the same current modular plan, current region declarations and native
full-envelope census for both exact boards, cross-owner interaction pairs fall
**1 → 0**: only the archived `C_IN3`/`Q_PRE` courtyard-corner pair disappears.
Body and pad overlap pairs remain 0. The other census counts remain 128
outside-owner refs and 148 refs entering foreign planning regions. These
counts differ from the later 15-part research placement because that board
changed additional poses; it is not the current-source baseline.

Three private builds have equal rule sidecars, DRC counts and native
footprint/pad/zone-bounds geometry fingerprint
`585371c06cb9a378806a97fac5659d724537c2e5a1c48fda4f45edbcb65053f7`.
Their PCB byte hashes differ because the TMUX POFV producer assigns fresh area
UUIDs and KiCad serializes those areas in varying order. The fingerprint is a
diagnostic comparison of placed objects and zone bounds, not a replacement
for exact PCB identity. Every downstream check must use the final PCB hash
above and its matching receipt.

The initial stock snapshot remains locked. USB ESD remains `prototype_only`
with unresolved XU316 transient coordination. Connector FULL still has 19
physical unknowns. The next engineering step is an independent review of
this exact private receipt, followed by one bounded coupled placement/route
objective under the existing decision protocol. This research result does
not consume a formal P1 TaskAttempt or reset the existing investigation.
