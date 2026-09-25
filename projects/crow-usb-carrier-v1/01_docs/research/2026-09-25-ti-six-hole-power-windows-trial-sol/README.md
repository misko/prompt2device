# Six-hole TI power-window P1 contract trial

**Research-only `INCOMPLETE`; P1, routing, and release remain unaccepted.** This packet evaluates the exact private six-hole board SHA-256 `009ecf6383f07129653758fdc0855c793d8915e4ae5b0980278e7a5fa4fc47c7` using the complete prior three-pose timing/analog/USB P1 diagnostic. The builder pins the input hashes, retains all exact native branch accounting, declares H1–H6 as fixed board features in this research contract, and changes only diagnostic source/floorplan and contract copies in this packet. It does not assign the holes a mechanical owner or keepout. The private board, canonical source, and existing research packet are unchanged.

Each of the nine former power findings used a movable pad with a wide `native_pad_face` bridge. The contract trial replaces each with a local `virtual_block_face`, its exact P2 pad-to-face obligation, and a small adjoining `power_or_mechanical` reservation in unowned planning space. The selected source pads and electrical owners stay the same.

| Net | Source pad / owner | Virtual owner face; reservation bbox mm | Outcome |
| --- | --- | --- | --- |
| GND | `C_ADC_3V3X_OK_VDD.2` / `adc_reference` | west; `[70,90,75,92]` | `INCOMPLETE` |
| N0V9 | `C_CORE_FF.1` / `digital_power` | south; `[150,134,154,136]` | `INCOMPLETE` |
| N12V_PROTECTED | `C_SPOKE_IN1.1` / `analog_ch1` | south; `[36,84,38,85]` | `INCOMPLETE` |
| N1V8 | `R_ADC_1V8_OK_TOP.1` / `adc_reference` | south; `[134,134,136,136]` | `INCOMPLETE` |
| N3V3X | `R_ADC_3V3X_OK_TOP.1` / `adc_reference` | south; `[138,134,140,136]` | `INCOMPLETE` |
| N3V3_ADC | `C_ADC_3V3X_OK_VDD.1` / `adc_reference` | west; `[70,98,75,100]` | `INCOMPLETE` |
| N5V_BUCK | `C_1V8_OK_VDD.1` / `digital_power` | south; `[160,134,164,136]` | `INCOMPLETE` |
| N5V_LDO_HOLD | `C_ISO1.1` / `analog_ch1` | south; `[40,84,42,85]` | `INCOMPLETE` |
| PWR_EN | `U_ADC_PWR_BAD.2` / `adc_reference` | west; `[70,94,75,96]` | `INCOMPLETE` |

The first full run found `H6` entering the declared `clock_flash_debug` physical cell. The trial trims that cell's unused east edge from x=232 to x=225 mm; its declared clock/flash members end near x=215.7 mm and the H6 native courtyard begins near x=226.5 mm. The two ADC south windows were placed at x=134–140 mm because `hold_bank_right` occupies x=76–126 mm at the south boundary and H5's native courtyard reaches near x=133.5 mm. The closest ADC window starts only about **0.5 mm** beyond that courtyard. The channel-1 south windows use only the 1 mm y=84–85 gap, east of H4's native courtyard near x=33.5 mm. These narrow spaces need independent electrical, mechanical, and manufacturing review, including a screw/washer/standoff envelope; the checker grants no current, copper, return, or routing capacity from them. The H6 trim is a planning-region exclusion, not mechanical clearance.

The complete `p1_corridor_capacity` evaluation with `diagnose_all=True` returns `INCOMPLETE`, `routing_realized=false`, `p1_accepted=false`, **zero global errors and zero independent diagnostics**. All ten power reservations and all five allocations remain `INCOMPLETE`; the ADC7 portal still has null capacity. This clears the nine *contract diagnostic* findings without establishing physical power distribution or any P1/release acceptance. There are no new checker regressions in this exact packet. The prior timing denominator remains 14 nets/54 terminals, including four supported two-terminal crossings and the 11-terminal AUDIO_EN branch.

Reproduce from the worktree root:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-six-hole-power-windows-trial-sol/build_trial.py
```

The builder asserts the exact board and input hashes, native witness rebind, every allocation status, all ten power reservations, zero global errors/diagnostics, and P1 rejection. The generated source SHA-256 is `e8ff456de1868386890dbb5413bb20dc054b5d711b7c9b97d8b02a6b4695ae92`; the contract SHA-256 is `6609dfb1a54febabf274a61353b9403078476c27b11ef67f31dd2e74ffda6ddf`.
