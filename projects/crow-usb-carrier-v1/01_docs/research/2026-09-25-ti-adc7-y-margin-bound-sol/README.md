# ADC7 oscillator y-margin bound

**Y-only adjustment is blocked at the existing pose.** This research screen is tied to the exact [three-part local candidate](../2026-09-25-ti-adc7-local-osc-probe-sol/README.md) board SHA-256 `c9b758d69867b274f0592bd2eceb9a26d64a80dd2daafa8ab9516d23d5925502`. It holds `C_ADC_I2C_A=(168.0,97.6)`, `C_ADC_CLOCK_OK=(164.6,76.2)`, and all 27 fixed references. It changes no canonical source, board, or P1 attempt.

With `Y_AUDIO` x=167.5 mm, the 0.01-mm sweep of y=87.20..88.50 finds **y=87.20 mm** as the largest no-new-physical-collision pose. Its checker `_physical_envelope` is `[164.705,85.105,170.295,89.295]`, giving **0.105 mm** from the channel-7 portal's y=85 southern edge to the north courtyard edge. The closest Y copper-pad edge is y=85.400, a separate **0.400-mm** pad-to-portal gap. At **y=87.21**, `Y_AUDIO` overlaps `C_ADC_I2C_B`'s physical envelope `[164.245,89.295,166.155,90.305]`. Clock and oscillator-bypass pad-center distances still improve slightly at that step, so locality is not the limiting condition.

A Y-only sideways dodge in this adjacent band is geometrically impossible: after a positive y increase, avoiding `C_ADC_I2C_B` requires the Y origin **x≥168.950**, while avoiding `C_AUDIO_OSC` `[170.745,88.995,172.655,90.005]` requires **x≤167.950**. `C_ADC_OUT` and `C_ADC_OK_VDD` add further right-side obstacles. The minimal next placement scope therefore includes at least one of the neighboring movable parts, rather than a larger Y y value alone. Terra's independent review correctly holds the existing 0.105-mm margin from P2 portal credit; an illustrative 0.25-mm target is **not** a declared requirement.

Native `kicad-cli pcb drc --severity-all --refill-zones --format json` reports **12→12** silk-only warnings and **499→499** unconnected items between y=87.20 and the first failed physical step y=87.21. DRC does not detect the virtual portal/courtyard constraint and does not clear the physical overlap. The exact [receipt](receipt.json) records the bound and warning types. Run from repository root:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-adc7-y-margin-bound-sol/probe.py > projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-adc7-y-margin-bound-sol/receipt.json
```
