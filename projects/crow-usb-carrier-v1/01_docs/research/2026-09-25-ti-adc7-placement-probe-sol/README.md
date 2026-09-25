# Isolated channel-7 port placement probe

**Result: geometric rescue, source-cell redesign still required.** This research copy is tied to Terra's [joint map](../2026-09-25-ti-adc78-tdm-xu-joint-refloorplan-map-terra.md) (`1859adca`) and [lower-neck packet](../2026-09-25-ti-tdm-xu-lower-neck-source-probe-terra/README.md) (`8d547cbf`). It changes no canonical board, source, stock, or P1 attempt. Its exact TI diagnostic source-board SHA-256 is `8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`.

Run from repository root:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-adc7-placement-probe-sol/build_probe.py > projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-adc7-placement-probe-sol/receipt.json
```

The script saves an isolated `/tmp/crow-adc7-isolated-move.kicad_pcb`, reloads it through `pcbnew`, and compares native `GetBoundingBox(True, True)` envelopes. The tested origins in mm are `Y_AUDIO=(195.5,118.0)`, `C_ADC_I2C_A=(183.0,104.0)`, and `C_ADC_CLOCK_OK=(163.5,90.0)`. All 27 fixed references retain position and orientation, all pad numbers and net identities match, and there are **zero new full-envelope overlap pairs**. The three moved footprints leave channel-7 `[166,83.9,167.12,85]`, channel-8 `[190.5,83.9,191.62,85]`, and the lower neck `[188,94,190,99.84]` untouched. Channel-7 and channel-8 rectangles are fully footprint-clear in this copy; the lower neck still intersects `C_XU_VDD_105` and `C_XU_VDDIO_109`, as in Terra's exact full-envelope screen. Baseline/copy overlap-pair totals are 2110/2071; this is a **delta check**, not a native DRC pass or route/return proof.

This is **not** a source-cell solution. The moved `Y_AUDIO` full envelope `[184.019,114.639,206.981,120.075]` crosses the present `digital_power` `[145,99.84,185,134]` and `clock_flash_debug` `[190,119.2,232,136]` cells, with an unassigned interval between them. `C_ADC_I2C_A` `[180.565,103.515,187.461,110.245]` crosses the east edge of `digital_power`; only `C_ADC_CLOCK_OK` `[159.039,82.941,165.935,92.008]` stays wholly in `audio_clock_tdm`. Simply declaring new rectangular receiver cells around those two envelopes would overlap the existing source cells. The source redesign must partition/repack those neighboring owners and every affected reference, then rerun full-envelope ownership and schema-2 allocation checks. The tested `C_ADC_I2C_A.1` to `U_ADC_I2C_XLATE.3` N1V8 pad-center distance also grows from **13.606 to 17.190 mm**, so the move does not establish the required local decoupling. Moving that decoupler near pin 3 while keeping full-envelope collision freedom likely requires surrounding P2 moves; this three-part copy is a geometric witness only.

The four TDM→XU endpoint pad witnesses, 54-member timing bundle, channel-7/8 ADC pad access, filled In1.Cu return, and signal-integrity consequences remain unproved. Do not credit P1 acceptance from this probe.
