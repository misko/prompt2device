# AUDIO_EN owner repair lower bound on the unified TI board

**Research-only obstruction; no P1/P2 or route credit.** `screen.py` reopens the exact 569-ref native board SHA-256 `d0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7`, the unified timing floorplan/modular owner authority, and the prior [source-generated three-part AUDIO_EN trial](../2026-09-25-ti-audio-en-source-probe-sol/README.md). It measures complete native body/courtyard envelopes and F.Cu pad bboxes, not schematic point symbols. The existing two-terminal timing packet leaves `AUDIO_EN` as the only timing source-owner failure.

| Ref and owner | Full native envelope mm | AUDIO_EN pad bbox mm | Minimum move to fit entire body in current owner rectangle |
| --- | --- | --- | --- |
| `R_AUDIO_PD`, `quiet_power` | `[22.185,104.125,23.215,106.075]` | `[22.38,105.34,23.02,105.88]` | 2.815 mm east **and** 0.875 mm south |
| `U_AUDIO`, `quiet_power` | `[21.455,108.35,23.945,110.645]` | `[22.95,108.975,23.65,109.225]` | 3.545 mm east |
| `U_ISO1`, `analog_ch1` | `[21.455,65.755,25.145,69.445]` | `[23.175,67.075,23.425,67.325]` | 3.545 mm east |

`R_AUDIO_PD`'s AUDIO_EN pad is already north/south-contained by `quiet_power`, but its full body is 0.875 mm north of the region. Moving only that resistor south by the exact minimum makes its full envelope overlap the nearby `C_AUDIO_CT1` by **1.030 × 0.625 mm**. Pushing `C_AUDIO_CT1` south by the minimum 0.625 mm to remove that overlap then makes it overlap `U_AUDIO` by **2.490 × 0.150 mm**. This proves a coupled local move is necessary; it does not rule out a larger support-group redesign. The present U_AUDIO-to-bypass/timing same-net pad-center distances are 1.400 mm to `C_AUDIO.1`, 2.853 mm to `C_AUDIO_CT1.1`, and 2.304 mm to `C_AUDIO_CT2.1`, so moving the IC alone changes a compact electrical group.

A minimal *rectangular* region-only recut that contains the three complete bodies would change `quiet_power` from `[25,105,75,134]` to `[21.455,104.125,75,134]` and `analog_ch1` from `[25,42,47,84]` to `[21.455,42,47,84]`. The quiet-power recut newly takes in **`C_IN3.1` and `.2`**, native pads owned by `input_buck`; calling that rectangle exclusive would be false. The channel-1 recut gains no foreign native pads in this screen, but it does not repair quiet power or the other `AUDIO_EN` terminals. This is a lower bound on those simple recuts, not a proof against every nonrectangular or coupled design.

The earlier source-generated candidate moved `R_AUDIO_PD`, `U_AUDIO`, and `U_ISO1` into their nominal owner rectangles with all 569 identities and 27 P1-fixed poses retained. It remains rejected: the moved resistor enters `input_buck`, the moved audio IC enters `hold_bank_left`, the U_AUDIO-to-`C_AUDIO.1` pad distance grows 1.400→5.078 mm, and native DRC gains a 0.100-mm `U_ISO1.2` AUDIO_EN-to-GND-via clearance finding plus a second via finding. This packet pins that receipt and checks the rejection rather than repeating its source generation.

The next honest source path is a **separate opt-in sparse owner-pocket model**, or a larger coupled source placement/region recut. A pocket must bind the exact modular owner and complete refs, full native envelopes and every pad, named local region, source placement pattern, foreign footprint/pad/region exclusions, and cross-record reservation conflicts. Each remote endpoint must select its pocket without changing the exact 11-terminal `AUDIO_EN` denominator or P2 pad access, P3 connected-net, and filled In1.Cu return duties. It must also account for the other nets on `U_AUDIO` and `U_ISO1`; an AUDIO_EN-only exception would misrepresent those refs. This proposed model is not implemented or accepted here. `R_AUDIO_PU.2` remains a separate pre-existing `input_buck` planning overlap.

Reproduce from repository root:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-audio-en-owner-bound-sol/screen.py
python3 -m unittest discover -s projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-audio-en-owner-bound-sol -p 'test_screen.py' -q
```
