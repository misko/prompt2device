# Isolated XMOS service local-move trial

**Disposition: reject as a P1 source change.** One bounded source-controlled placement set opens a raw six-slot QSPI trunk and an upper two-slot crystal sublane while retaining the JTAG trunk, but it does not complete crystal endpoint coverage, preserve proven XU decoupling, or meet zero native DRC. No canonical floorplan, PCB, rule, or active P1 attempt was edited.

The isolated floorplan is `/tmp/crow-p1-service-trial-sol/projects/crow-usb-carrier-v1/03_src/floorplan.yaml`, SHA-256 `85d1bed3d3605b8666a393a74f0a84525bf9360583894ecf0f8186e060455180`. It is a copy of the current source floorplan `4a457c731c204084a83aa817a29ca8fc8acc07097723adefedc296eb4db37b98`, with these exact experimental poses (x/y mm, degrees):

| Ref | Current | Trial | Reason |
| --- | --- | --- | --- |
| `C_XU_VDD_5` | (201.0,109.4,0) | (198.0,109.4,0) | Clear QSPI south edge. |
| `C_XU_VDDIO_10` | (203.5,109.4,0) | (205.0,112.5,0) | Clear QSPI south edge. |
| `C_XU_VDD_14` | (208.5,109.4,0) | (213.5,112.5,0) | Open a crystal approach. |
| `U_FLASH` | (216.0,124.0,0) | (219.0,124.0,0) | Move flash away from crystal approach. |
| `R_QSPI_CS` | (210.8,120.1,0) | (224.0,120.1,0) | Move CS resistor away from crystal approach. |
| `C_FLASH` | (209.2,127.9,0) | (219.0,130.0,0) | Open lower crystal space. |
| `C_XTAL_IN` | (207.8,120.1,0) | (207.3,120.1,0) | Relieve crystal-side clearance. |

The three already anchored XU capacitors were changed in isolated `anchors`; the four formerly floating support parts were added to isolated `post_anchors`. `C_XU_USB33` was also post-anchored at its **unchanged** original pose (206.6,89.2,0): without that explicit pin, legalization moved it to (203.0,109.5,0) and reduced the QSPI lane to four raw slots. This is part of the tested set, not an eighth board-pose change. `U_XU`, all USB and PLL poses, the connector poses, and the TDM seeds were held fixed.

The isolated generator saved `04_kicad/service_trial_r2.kicad_pcb`, SHA-256 `6a9f1a70051150eb2f18f3ccbc3a849dce545c827d6040079f8e126f4ce1ad31`. It placed 569 footprints and reported zero inter-footprint pad overlaps/shorts and zero fixed courtyard overlaps. Exact native comparison against the current-source saved board found **only the seven intentional pose changes above** across all 569 references; every footprint's pad-number/net-name multiset was unchanged. Thus the XU/USB/PLL/TDM local seeds and all other unowned poses remained identical in this saved comparison.

Using `p1_corridor_capacity.py`'s native F.Cu body/pad rectangle screen with 0.45-mm pitch:

| Tested lane `[x0,y0,x1,y1]` mm | Connected raw width | Raw slots | Assessment |
| --- | ---: | ---: | --- |
| QSPI south `[199.900,108.675,204.100,126.925]` vertical | 4.165 mm | 9, versus 6 demanded | `C_XU_VDDIO_10` defines the neck at y=112.5. The checker validates 13 QSPI ref.pad/net endpoints in trial pockets, but the relocated flash and CS pockets stretch from x=204.1 to x=223.675 and 224.955; foreign obstacles and actual access across these pockets are unproved. |
| Crystal upper `[208.750,108.675,211.300,122.125]` vertical | 1.315 mm | 2 exploratory slots | `C_XU_VDDIO_17` defines the neck. Trial pockets cover `U_XU.34/.33`, `R_XTAL_FB.1/.2`, and `Y_XU.3`, but omit `R_XTAL_DRIVE.1` and `C_XTAL_OUT.1` below the crystal body. This is not the full `XTAL_IN`/`XTAL_OUT` requirement. |
| JTAG/reset `[217.200,54.025,223.475,105.200]` vertical | 2.540 mm | 5, versus 5 demanded | Raw trunk unchanged. The three other `XU_RESET_N` digital-power endpoints still lack a shared access plan. |

Trying one full crystal rectangle `[210.925,108.675,214.325,129.895]` on the same saved board yields only **0.630 mm / 1 slot**. `C_XU_VDDIO_17`, `C_XU_VDD_18`, and relocated `C_XU_VDD_14` obstruct its top; the upper two-slot sublane cannot simply be extended through the crystal/support cluster. A lower rectangle `[208.750,125.875,211.300,129.895]` has five raw slots but is separated by the `Y_XU` footprint and does not establish connected endpoint access. A complete crystal reservation needs a different multi-window topology and likely more XU decoupler placement changes, beyond this bounded move set.

The decoupling penalty is material. Native pad-center distance from capacitor pad 1 to its corresponding XU supply pad changed from 3.800 to **6.612 mm** for `C_XU_VDD_5`/`U_XU.5`, 3.364 to **5.030 mm** for `C_XU_VDDIO_10`/`U_XU.10`, and 1.814 to **7.340 mm** for `C_XU_VDD_14`/`U_XU.14`. These are placement distances, not checked copper/return paths; the trial cannot assert preserved local decoupling or P-ADJ admission.

Direct `kicad-cli pcb drc --format json --severity-error --refill-zones` on the isolated saved board reported **245 clearance violations and 499 unconnected items**; the current-source saved baseline reported the same counts. They are predominantly inherited TMUX-area findings under this direct CLI invocation, but the requested absolute zero native DRC gate is not met. Neither run saved a filled board, so In1.Cu reference continuity remains unproved. No rule/zone was removed to improve the result.

This trial does not justify moving the canonical parts. The next owner must jointly redesign the XU south decoupler ring with its owning supply-pad/return budgets, resolve the crystal's upper-to-lower access around `Y_XU`, place flash/CS close enough for real QSPI access, then run an exact-hash zone-filled capacity and native DRC comparison under the project's full rule sidecars. Board integration retains service-corridor ownership; `clock_flash_debug`, `digital_power`, and `xmos_core` own the affected local endpoint constraints.
