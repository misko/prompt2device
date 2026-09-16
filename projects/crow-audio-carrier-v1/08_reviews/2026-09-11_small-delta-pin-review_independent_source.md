subject: crow-audio-carrier-v1 isolated small-delta-pin-review
date: 2026-09-11
reviewer: /root/carrier_small_delta_pin_review (fresh independent source judgment)
context-given: frozen input packet; envelope SHA256 3a0f6637d9c54242112dc881d705a2cce011d461afeb8cfd5def086ff579be01
source_commit: db86586129445c88b37d0a6a9ba52d6cec19d0b8 plus enumerated uncommitted source packet
board_sha256: 0d80ee923dbbae34995fa892e5fc2224b489e5d4afc1a03dc2a7836c44a31058
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
scope: Limited source review; original verdict and limitations below. No canonical placement or release acceptance.
original_report_sha256: 06fa1767525cd78c60de7e000d8644fa3c8bcc8db86231fd08ae7dda712330ed

# Independent 3-ref / 8-pin source and physical review

Engineering verdict: **PASS for the requested pin, native-footprint, body/model-registration, and local-clearance scope.** This is a source-only review of `Q_PRE_EN`, `Q_RST1`, and `R_PWR_TOP`; it does not accept placement/routing as a whole, purchasing, assembly process, order state, stock, or firmware.

## Eight-pin identity and connectivity census

| Ref | Physical pin | Manufacturer / source intent | TSX net | Saved PCB net and physical location | Netlist | Result |
|---|---:|---|---|---|---|---|
| Q_PRE_EN | 1 | G | PWR_EN | PWR_EN, local upper-left, (-1.00,-0.95) mm | PWR_EN / G_1 | PASS |
| Q_PRE_EN | 2 | S | GND | GND, local lower-left, (-1.00,+0.95) mm | GND / S_2 | PASS |
| Q_PRE_EN | 3 | D | PRE_GATE | PRE_GATE, local right, (+1.00,0) mm | PRE_GATE / D_3 | PASS |
| Q_RST1 | 1 | G | RESET_PULSE_H | RESET_PULSE_H, local upper-left, (-1.00,-0.95) mm | RESET_PULSE_H / G_1 | PASS |
| Q_RST1 | 2 | S | GND | GND, local lower-left, (-1.00,+0.95) mm | GND / S_2 | PASS |
| Q_RST1 | 3 | D | ADC_RESET_N | ADC_RESET_N, local right, (+1.00,0) mm | ADC_RESET_N / D_3 | PASS |
| R_PWR_TOP | 1 | A | 5V_BUCK | 5V_BUCK, local left (-0.825,0) mm; global right because footprint is 180° | 5V_BUCK | PASS |
| R_PWR_TOP | 2 | B | PWR_SENSE | PWR_SENSE, local right (+0.825,0) mm; global left because footprint is 180° | PWR_SENSE | PASS |

Diodes DS30896 Rev.20-2 p.1 was visually inspected: its top-view package and equivalent circuit independently establish pin 1=G, pin 2=S, pin 3=D for 2N7002K-7. Page 7 was visually inspected and gives the SOT23 suggested-land dimensions. Both saved instances use `crow_audio_carrier:Diodes_2N7002K_SOT23_Exact`, with 0.90 x 0.80 mm rectangular pads at the required local coordinates. The TSX Y-up definition correctly becomes the saved KiCad Y-down coordinates. Both model transforms are offset (0,0,0), scale (1,1,1), rotation (0,0,0).

Yageo RT V17 p.4 was visually inspected: RT0603 is nominal 1.60 x 0.80 x 0.45 mm and maximum 1.70 x 0.90 x 0.55 mm. The saved Fab rectangle is the corrected nominal 1.60 x 0.80 mm. The unchanged 40,618-byte STEP has Cartesian extrema x=+/-0.80, y=+/-0.40, z=0..0.45 mm and is registered with zero offset, unit scale, and zero rotation. Its immutable provenance, upstream commit `e62ed1fc7862da83f789bd562671b5e4b82afcdf`, exact URL, SHA-256, and reproduced KiCad CC-BY-SA-4.0-with-exception text were inspected.

## R_PWR_TOP land compatibility

Yageo Mounting V10 p.4 Fig.4/Table 1 was visually inspected. The reflow-0603 recommendation is A=2.60, B=0.80, C=0.90, D=0.80 mm. The native pattern has overall x envelope 2.45 mm, inner gap 0.85 mm, pad x length 0.80 mm, and pad y width 0.95 mm: deltas are -0.15, +0.05, -0.10, and +0.15 mm respectively. Each roundrect has actual radius 0.20 mm (`rratio=0.25` on 0.80 x 0.95 mm), giving 0.725664 mm2 copper area versus 0.720000 mm2 for the manufacturer's rectangular nominal land. The native pad overlaps the nominal body plan by 0.375 x 0.80 mm before corner subtraction. Those quantitative facts support compatibility for this standard extended passive land; they do not assert universal full-metallization coverage or assembly-process qualification.

The rejected `all_pad_centres` idea is not a valid physical rule for extended SMD lands: resistor pad centers at +/-0.825 mm are intentionally outside the nominal body at +/-0.800 mm, just as other lead/termination lands can extend beyond a body. The proposed `all_smd_pad_overlap` rule is acceptable as a deliberately weak registration datum if it uses every native effective copper polygon (including rounded/custom/rotated geometry), requires positive-area intersection with an independently measured model plan envelope, retains exact Fab/body-center, tolerance, courtyard, and signed-side checks, and is described only as overlap. It cannot substitute for the separate primary pin, terminal, and recommended-land review completed here.

## Local collision census

All 340 saved-board front courtyards and all 1,002 saved-board pads were enumerated. Each subject courtyard was compared against the other 339 courtyard polygons by its exact native courtyard bounding envelope (including stroke); each subject pad was compared against every pad belonging to other footprints using native effective bounding envelopes. This conservative screen found no overlap. Q_PRE_EN: minimum courtyard clearance 0.430 mm to R_AUDIO_PD; minimum pad-envelope clearance 0.920 mm to R_AUDIO_PD pad 2, denominator 2,997 pad pairs. Q_RST1: 0.230 mm to R_RESET_PU; 0.899889 mm to R_RESET_PU pad 2, denominator 2,997. R_PWR_TOP: 0.230 mm to U_PWR; 0.850 mm to R_PWR_BOT pad 1, denominator 2,000. Each courtyard denominator is 339. The evidence labels these as bounding-envelope distances rather than claiming unsupported curved-polygon precision.

Saved board: 1,453,827 bytes, SHA-256 `0d80ee923dbbae34995fa892e5fc2224b489e5d4afc1a03dc2a7836c44a31058`. Exact source footprint identities are `crow_audio_carrier:Diodes_2N7002K_SOT23_Exact` (both MOSFETs) and `crow_audio_carrier:Yageo_RT0603_NominalBody` (resistor).
