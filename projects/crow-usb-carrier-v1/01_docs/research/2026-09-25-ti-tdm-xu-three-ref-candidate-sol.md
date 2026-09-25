# TI TDM→XU three-reference placement candidate

**Isolated research board; P1 remains `INCOMPLETE`.** This variant starts from
the exact TI unrouted board SHA
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`.
The script pins the source rules and floorplan SHAs, saves the board, reloads
it, and verifies all pad/net/layer identities and all 27 P1-fixed poses.
`result.json` binds the variant board SHA
`84222b009b4d3ed898bc12636d4940d3c8f93c0c1a443d6ae26f8671b04e8c77`.

| Changed P2 reference | Before → after (mm) | Change | Full native bbox after (mm) |
| --- | --- | ---: | --- |
| `C_XU_USB18` | (198.6, 93.1) → (198.6, 91.5) | 1.6 mm | [191.151428, 90.9384, 201.034524, 93.50825] |
| `C_XU_VDD_104` | (198.6, 96.0) → (197.3, 88.9) | 7.218 mm | [190.701251, 84.439313, 199.734524, 90.90825] |
| `R_ADC_I2C_SCL_B_PU` reference text | (179.8, 100.5) → (150.0, 90.0) | pads/footprint remain (170.8, 91.5) | [146.297679, 89.539313, 173.091667, 93.51825] |

The two capacitors' complete footprints remain inside `xmos_core`; the
resistor's complete footprint remains inside `audio_clock_tdm`. No full
envelope enters the tested lane or the ch7/ch8 analog regions. No new native
body/courtyard bbox intersection appears. The current direct band
`[182.475,94,199.825,100]` now has 2.5384 mm / **five** 0.45-mm slots;
expanding its north edge to 93.6 mm has 2.9384 mm / **six** slots. Both exceed
the four-slot demand, with `U_TDM_XLATE` and `U_XU` exempted only as terminal
footprints. Their actual pad fanout is not proved.

Using the exact packet project rules and footprint-library context, native
DRC finds the same 14 `via_dangling` warnings and 499 unconnected items in
both baseline and variant. The violation identity set is identical. The
research directory contains only the board and result, with no generated
project sidecar; the probe reconstructs the original project context in a
temporary directory for DRC.

**Electrical/assembly concern:** `C_XU_USB18` pad 1 on `N1V8` moves from
6.135 mm to 7.030 mm from its nearest same-net U_XU pad. `C_XU_VDD_104`
pad 1 on `N0V9` moves from 2.783 mm to 6.811 mm from the nearest same-net
U_XU pad; the nearest pad changes from 104 to 95. Center distance is only a
proxy, not a loop-inductance test. The In1.Cu GND zone is unfilled, so the
return and decoupling loop cannot be accepted. Moving the resistor's printed
reference 31.6 mm away from its pads also needs assembly-readability review.
No timing trace, reference continuity, endpoint access, or SI/PI has been
proven. This candidate is **geometrically and DRC feasible but not electrically
accepted**.

Terra's alternate `[188,94,190,99.84]` neck measures 2.5384 mm / five slots
with an `audio_clock_tdm` ownership recut at x=188 and no capacitor move.
That is a potentially lower-risk next investigation for XU decoupling, but
its source cell split, all four exact endpoint accesses, and return proof
remain outstanding. Neither option promotes P1 or stock.

Reproduce:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-tdm-xu-three-ref-candidate-sol.py /tmp/ti-tdm-xu-three-ref
```
