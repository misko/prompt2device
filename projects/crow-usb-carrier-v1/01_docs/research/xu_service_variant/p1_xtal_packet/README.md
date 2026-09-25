# XTAL source-model packet: exact native declaration, combined schema failure

**Research disposition: FAIL closed; no P1 admission.** The isolated XTAL
declaration validates all seven exact native ref.pad/net endpoints, but the
combined XTAL + shifted QSPI source cannot be represented by the current
single-rectangle-per-modular-block checker. The whole allocation returns
`FAIL`, `p1_accepted=false`, with the exact error
`qspi_gap: integration face lacks positive non-corner shared edge`. The
canonical source, board, governed task state, and attempt count are untouched.

This packet is based on retained-cap geometric candidate commit `988a43c1`.
It keeps `C_XU_VDDIO_35` at `[218.0,105.8,90]`, with native body/courtyard
`[217.495,104.845,218.505,106.755]`. The isolated XTAL handoff is
`[217.2,107,218.95,118.5]`; the QSPI region and XU-facing edge begin at
`x=219.2`. The former QSPI face has 3.6 mm raw span and its declared demand
is 2.7 mm; these are geometric inputs, not effective capacity. No native
body/courtyard enters either handoff region on the pinned board. The cap is
retained in a physical east cell with eight other `xmos_core`-owned support
refs. The empty south physical cell supplies a proposed QSPI-facing edge.
These physical cells do not become modular endpoint owners or shared-zone
aliases.

The exact XTAL endpoint set is `U_XU.34`, `R_XTAL_DRIVE.1`, `R_XTAL_FB.1`
on `XTAL_IN`, and `U_XU.33`, `C_XTAL_OUT.1`, `R_XTAL_FB.2`, `Y_XU.3` on
`XTAL_OUT`. The two XU pads remain owned by `xmos_core`; the five oscillator
endpoints remain owned by `clock_flash_debug`. The source and contract carry
seven `P2_REQUIRED` pad-to-face obligations and an `In1.Cu` filled GND-return
obligation. The isolated native checker accepts each exact witness and its
reservation contact; that does **not** establish pad escape, effective lane
capacity, routing, crystal performance, or return continuity. The west XU
face is a 0.004 mm declaration strip between the native U_XU envelope ending
at x=217.195 and the cell edge at x=217.2. Its tiny width is another reason
to defer actual copper access to P2. The retained-cap dogleg feasibility is
measured separately in `../xtal_south_cap_handoff.json`.

## Exact current-schema blocker

The floorplan declares disjoint rectangles:

| Cell | Rect in mm | Role |
| --- | --- | --- |
| `xmos_core` | `[190,84,217.2,110.5]` | XU main cell and XTAL west face |
| `xmos_core_east` | `[217.2,84,221,107]` | nine XU-owned support refs, including retained cap |
| `xmos_core_qspi_south` | `[218.95,107,232,110.5]` | vacant QSPI-facing physical cell |
| `clock_oscillator_handoff` | `[217.2,107,218.95,118.5]` | exclusive XTAL corridor |
| `board_integration_qspi` | `[219.2,110.5,223.2,118.5]` | exclusive QSPI corridor |

The checker selects `regions[block]` for every endpoint face. Since the exact
QSPI endpoint block is `xmos_core`, its south face must touch the rectangle
named `xmos_core`. That rectangle stops at x=217.2, while the shifted QSPI
face starts at x=219.2. Expanding the single `xmos_core` rectangle through
x=219.2 and y=110.5 would positively overlap the exclusive XTAL handoff
over `[217.2,107,218.95,110.5]`. Renaming QSPI endpoints to either physical
cell would falsify the modular ownership denominator. Treating those cells as
a shared zone would likewise invent ownership authority. Thus the existing
schema cannot validate both corridors without a false alias or overlap.

The minimal generic extension is a source-owned `physical_cells` mapping:
each cell has a unique region key, one existing modular `owner_block`, a
rectangle, and an exact assigned-ref set. A corridor face and witness may
name `physical_cell_id` separately from the unchanged modular `block`.
Validation must require: the cell maps to that block; its assigned native refs
are owned by that block and their full physical envelopes fit; its face lies
on its own region boundary; cells and corridors are pairwise disjoint except
shared edges; exact endpoint, native pad/net/layer, P2 obligation, and global
coverage checks remain unchanged. A cell without assigned refs is allowed
only as a declared transit cell with explicit same-owner adjacency to an
occupied cell. This is a generic physical partition of an owner, not an
endpoint owner or a bypass for a foreign region. The proposed south cell
touches the occupied east cell along y=107, x=218.95..221. After implementing
that extension, revalidate the combined native packet and all existing
checker fixtures before using any capacity result.

## Reproduction and hashes

Run from this worktree root with KiCad 10 `pcbnew` and PyYAML:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/xu_service_variant/p1_xtal_packet/build_packet.py
```

`build_packet.py` checks every parent input hash, writes the isolated source,
floorplan, and coarse contract, checks all seven XTAL witnesses against the
pinned native board, then demands the precise combined FAIL outcome. The
machine-readable receipt is `validation.json`.

| Artifact | SHA-256 |
| --- | --- |
| native board | `fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27` |
| `p1_source_xtal.yaml` | `e819c423f211cc0b52fa222984d49bed79d47533fc679c2677eedde1067a0fd7` |
| `floorplan_xtal.yaml` | `5a0d898ba66f531861c372878480bc07890d34f1daf681b1e70fd5add3b202f2` |
| `coarse_contract_xtal.json` | `b5a2d8d18dd3849679dfd3e8142947e2dfc42bc742d3d9c4c0a65653b575db59` |
| modular plan | `7201aa55cffefca99f9f27e92711cbbcf28387432523a8c960b5cd71e973170e` |

The parent QSPI source, floorplan, contract, aliases, and board hashes are
also pinned in `build_packet.py` and recorded in `validation.json`. This is
not a route, DRC result, filled-reference proof, or P1 acceptance.
