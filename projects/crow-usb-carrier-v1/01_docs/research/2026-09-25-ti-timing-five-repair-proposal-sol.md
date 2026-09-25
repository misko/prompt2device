# Five ADC/audio timing failures: bounded repair proposal

**Research only; no P1, P2, route, or return credit.** This note uses the unified packet at commit `9f8ca953` and its exact 15-part native board `2026-09-25-ti-vmid-coupled-ch8-sol/candidate.kicad_pcb`, SHA-256 `d0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7`. The packet's exact endpoint ledger is SHA-256 `92ed09bcb38860eb16c093d7844271c8dca0878dc478faee2f16235501a6f2e3`. All five nets retain the packet's exact modular/source/native endpoint sets and null capacity. No canonical source or board was edited.

## Four exact two-terminal handoffs

| Net | `audio_clock_tdm` F.Cu pad centre (mm) | `xmos_core` F.Cu pad centre (mm) |
| --- | --- | --- |
| AUDIO_MCLK_1V8 | U_TDM_XLATE.6 `(175.3375,95.875)` | U_XU.23 `(211.1,107.6625)` |
| TDM_BCLK_1V8 | U_TDM_XLATE.4 `(175.3375,94.575)` | U_XU.22 `(210.7,107.6625)` |
| TDM_DATA_1V8 | U_TDM_XLATE.7 `(175.3375,96.525)` | U_XU.107 `(200.8375,97.8)` |
| TDM_FSYNC_1V8 | U_TDM_XLATE.5 `(175.3375,95.225)` | U_XU.20 `(209.9,107.6625)` |

Every listed native pad is on the stated net and F.Cu, inside its source-owner region (`audio_clock_tdm` `[145,72,190,99.84]`; `xmos_core` `[190,84,217.2,110.5]`), and the packet reports no foreign-region pad intersection. The regions meet at x=190 with no measured positive-width transit mouth. The existing `unresolved_multiterminal_branch` checker rejects `len(expected) < 3`; the existing `linked_paths` model requires three owners, a first measured physical corridor stage, and two stages. Neither can honestly represent these four two-terminal, unplaced paths by adding a fictitious terminal or asserting corridor capacity.

**Minimal source-model repair:** generalize the geometry-free unresolved-branch record to permit exactly two distinct source owners and two exact native terminals (the present `_unresolved_branches` cardinality floor changes from three to two, with a native two-terminal negative/positive fixture). For each of these four nets, the packet builder should emit the same exact endpoint-denominator, native-pad/net/layer, source-owner-containment, P2 pad-to-unplaced-path, and filled In1.Cu return obligations already used by the nine timing branches, with `terminal_count: 2`, `minimum_tree_edges: 1`, `capacity_slots: null`, and a P3 one-connected-net obligation. This grants only an `INCOMPLETE` accounting record. A later source-owned physical mouth or route geometry must be measured before any capacity or adjacency claim. The current south-edge XU pads and west-edge U_XU.107 also prevent treating the four nets as one automatically proven straight bundle.

## AUDIO_EN owner containment

`AUDIO_EN` has exactly 11 declared/native F.Cu terminals. Eight owner-contained terminals stay as recorded in the packet. Three pads are outside their owners, so the current unresolved-branch record correctly fails before any geometry-free credit:

| Native pad | Current bbox (mm) | Owner region | Body-minimum east shift | Simple east-shift body conflict |
| --- | --- | --- | --- | --- |
| R_AUDIO_PD.1 | `[22.38,105.34,23.02,105.88]` | quiet_power `[25,105,75,134]` | 2.795 mm | none at that exact translated body bbox |
| U_AUDIO.6 | `[22.95,108.975,23.65,109.225]` | quiet_power `[25,105,75,134]` | 3.525 mm | R_AUDIO_PU, R_ADC_BOT, C_AUDIO |
| U_ISO1.2 | `[23.175,67.075,23.425,67.325]` | analog_ch1 `[25,42,47,84]` | 3.525 mm | R_ADC_PD1N, C_FB1N, R_ADC_PD1P |

The shifts use **whole native footprint body** containment, which is stricter than pad containment. An isolated, translation-only F.Cu body-bbox screen with 0.30-mm foreign-body spacing found these *unadopted* source-anchor trial poses: R_AUDIO_PD `(28.5,106.3,90)`, U_AUDIO `(26.6,114.0,0)`, and U_ISO1 `(27.2,74.6,0)`. Their translated body bboxes are `[28.005,105.345,28.995,107.255]`, `[25.375,112.75,27.825,115.025]`, and `[25.375,72.775,29.025,76.425]`, respectively. The selected AUDIO_EN pads would be owner-contained at those poses. This screen does **not** grade courtyards, other pads, fixed-access envelopes, local decoupling, signal/return reachability, or generator/native DRC, and it does not authorize those coordinates. P2 must regenerate a source-owned isolated candidate, check the whole local cell and all affected contacts, then refresh the exact 11-terminal branch and its foreign-region blocker inventory. `R_AUDIO_PU.2` presently overlaps the separate input_buck region even though it is inside quiet_power; that remains a declared blocker, not a reason to widen either region.

The packet's other nine timing branches are not repaired or promoted by this proposal. Its nine power-boundary diagnostics and nine derivative global denominator errors also remain outside this scope. No connector FULL, continuous filled reference, route, or P1 acceptance follows from this note.
