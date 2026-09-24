# XU C17/C14 shared return: independent review (Terra)

**Scope.** Read-only review of SOL note `29fd055f` and saved isolated board `/tmp/crow-xu-c17-shared-return-sol/04_kicad/crow_carrier.kicad_pcb` (SHA-256 `85be0b4913b59d9b02051e330afbbd797a0d1114567a49a80ad8086bd06056b8`). No canonical source or PCB was changed.

## Geometry and native evidence

The exact topology is one 0.20-mm F.Cu trace from `C_XU_VDDIO_17.2` `(208.700,110.280)` to `C_XU_VDD_14.2` `(209.180,111.400)`, then one 0.20-mm trace to the ordinary 0.60/0.30-mm GND via at `(209.180,112.400)`. It removes the prior C17 via entirely. The C17 return path is consequently 2.218524 mm, while C14’s is 1.000000 mm; the N1V8 and N0V9 supply paths remain 1.657500 mm and 4.223185 mm respectively.

The via annulus envelope is `[208.880,112.100]..[209.480,112.700]` mm. C14’s F.CrtYd bottom edge is y=111.885 mm, giving 0.215 mm to the annulus; C14’s physical body ends at y=111.700 mm. The board has no overlap with either C14 or C17 F.CrtYd/F.Fab graphics. This resolves the earlier physical via-envelope conflict. It does not establish a manufacturer assembly margin because neither XMOS nor the retained public fabrication record supplies a numerical courtyard clearance for this ordinary via.

The final paired DRU has the correct order: generic `DIGITAL_POWER_width`, TMUX POFV block, then the two exact XU neck-down rules. `drc_shared_replay.json` (SHA-256 `0a66349609ec2c6b53b4dc1760b32116c0fd68a875da0aea44973ce194d4fbc8`) reports four intended `track_dangling` rows, 499 unconnected items, and zero parity issues; the via-process record grades 19/19 sites, including five ordinary 0.60/0.30 vias. The replay source contains the original six PLL banks plus four XU banks; `prep` served 10 banks and 28 primitives, and the 46 replayed copper signatures match the manually changed board. These are valid geometry/replay facts, not return-quality evidence.

## Return topology

This is not a rail short: `C_XU_VDDIO_17.1` remains N1V8 and `C_XU_VDD_14.1` remains N0V9. It does, however, make the C17 return current flow through C14 pad 2 and share C14’s pad copper, the one-millimetre branch, and the single via before reaching the plane. Thus transient return impedance is common to two distinct supply decouplers; native DRC, parity, POFV and via-process checks do not model that coupling.

XMOS `XM-014532-PC` v2.0.0, section 14 “Integration”, requires VDDIO decoupling close to the chip and says that the decoupler ground side should have as short a path back to GND pins as possible. It does not define a numerical route-length limit or explicitly prohibit a shared plane via. The 2.218524-mm C17 return is a material qualitative regression from the prior 0.456508-mm direct-via probe, and is therefore not admissible merely because it is DRC-clean.

## Verdict and required evidence

The shared-return geometry is **conditionally promotable for further source-level review**: it is not physically inadmissible on the present body/courtyard and correctly ordered native-rule evidence. It is **not an accepted XU decoupling topology**. Promotion requires all of the following:

1. A source-owned C17/C14 return contract that expressly permits or rejects the shared pad/via topology, identifies the two rails, and verifies the exact branch/via identity after replay. It must not invent an XMOS length limit.
2. Engineering evidence that the common-return inductance/current coupling is acceptable for the relevant load and transient conditions, such as a reviewed extraction or first-article measurement tied to this board stackup and plane path. Plane membership alone is insufficient.
3. An explicit ordinary-via solder-mask/tenting process decision and assembly review for the 0.215-mm native-courtyard gap. The current board shows an ordinary (not filled/capped) via; generic native DRC does not grade body clearance or process selection.
4. Reapplication and validation of the exact C14 priority and C17 F.Fab-only reference controls before any source adoption, because the isolated placement still carries those two ownership regressions.
5. Completion of the outstanding route/open/diagnostic work and an approved build stage that invokes generic rules → POFV → XU helper; the helper remains `placement_review_required` and is not part of the normal replay path.
