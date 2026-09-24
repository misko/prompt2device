# XU C17/C14 shared return: conditional source-candidate contract (Terra)

**Decision.** The topology may be admitted only as an isolated, `placement_review_required` **pre-P1 source candidate**. That admission means its exact geometry/replay may be carried into bounded review work. It does not admit an XU decoupling design, a route, fabrication, assembly, P1, or release.

## Manufacturer boundary

XMOS’s public [XU316-1024 datasheet, v2.0.0, section 14](https://www.xmos.com/documentation/XM-014532-PC/html/) says VDDIO capacitors belong close to the chip and their ground side should return to GND pins as shortly as possible. It does **not** state that every decoupler needs a dedicated via, nor give a numerical maximum route length, return impedance, or rail-noise limit. A separate C17 via is therefore an engineering preference for reducing common impedance, not a primary-text XMOS mandate.

The candidate's shared path is an engineering concern because C17 (N1V8) reaches C14 pad 2, then shares C14 pad copper, a 1.000000-mm branch, and one GND via with C14 (N0V9). This is common return impedance between two rails, not a supply-net short. The geometry does not invalidate the manufacturer text, but it also cannot demonstrate compliance with its qualitative short-return direction.

## Pre-P1 source contract

A candidate record must bind the source hashes and native board to these literal identities: `C_XU_VDDIO_17.2` → `C_XU_VDD_14.2` → via `(209.18,112.40)`, all GND; `C_XU_VDDIO_17.1` remains N1V8 and `C_XU_VDD_14.1` remains N0V9. It must prove the sole common branch/via and reject an extra branch, foreign-net copper, via relocation, or a changed capacitor pad/net. It must retain the correctly ordered final DRU (generic rules → TMUX POFV → exact XU launch rules), native DRC/parity/via-process results, and the body/courtyard review. This is a topology identity guard, not an electrical-quality pass.

Before this can become an accepted placement/topology, an approved project-owned measurement plan must declare the load cases, instruments, probe points, bandwidth, grounding method, repeat count, and pass/fail limits **before** testing. The limits must be traceable to the applicable rail/device operating budget or to an explicitly reviewed engineering allocation; none may be represented as an XMOS limit.

Required later evidence is:

1. **Return path/current:** stackup- and board-hash-bound extraction or measurement identifies C17/C14 loop paths, the shared pad/branch/via contribution, and current distribution during representative simultaneous and separate rail activity. Compare the shared topology against a dedicated-via control or another reviewed topology under the same conditions.
2. **Rail noise:** measure N1V8 and N0V9 at the relevant XU/capacitor pads with a documented low-loop probe arrangement while exercising the declared worst switching/I/O activity. Record differential rail ripple and local ground displacement, including whether activity on either rail couples into the other. Functional pass alone is insufficient.
3. **Mask and assembly:** freeze the selected ordinary-via finish/covering and surface finish in the manufacturing record. The saved via is ordinary, not filled/capped. JLCPCB's public [via-covering guidance](https://jlcpcb.com/help/article/pcb-via-covering) distinguishes tented, untented, plugged, and filled/capped processes and their assembly consequences; its generic text is not approval of this exact clearance. Retain a CAM/DFM and assembly review of the exact board and the native footprint-envelope evidence.
4. **First article:** inspect C14/C17 solder joints and the via finish on the hash-bound populated board, then repeat the return/noise tests on that board at the defined operating modes and power-cycle/load transitions. Bind captures, probe photographs/setup, lot/build metadata, and failures to the board hash.

A dedicated C17 via becomes mandatory only if this project-owned contract rejects the shared topology or its later evidence fails. It is not mandatory solely on XMOS primary text. The current 0.215-mm courtyard clearance, four intentional dangling diagnostic tracks, 499 opens, reference-label waivers, and unfinished routing remain separate admission blockers.
