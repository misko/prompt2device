# Native component-source closure

The corrected component source is `03_tscircuit/src/crow_usb_digital.tsx`, derived from immutable donor SHA-256 `344378c34208e9636862b0bc8e66c896a2aae6353a5f0caf9a4de1eccd500414`.

A real tscircuit 0.0.2351 run instantiated 102 references with 36 exact MPNs. `06_build/evidence/runtime-native-inventory.json` records every ref, value, exact MPN, JLC code, resolved KiCad FPID, native file, source-port count, and native pad count. KiCad 10.0.4 `pcbnew.FootprintLoad` loaded all 102 footprints. U_XU has 129 runtime source ports and 129 unique numbered native pads; its 138 physical pad objects include the EP129 copper land plus nine segmented-paste apertures; no thermal vias are claimed.

Every runtime MPN now has a local `part.yaml`, quoted `lib:name` footprint, and local PDF evidence. Specialty lands live in `03_src/lib/crow_usb_digital.pretty`; standard packages resolve to installed KiCad libraries. This removes prose footprints, numeric YAML coercion such as unquoted `0402`, and reliance on footprinter shorthand as native geometry evidence.

The capacitor helper now defaults `jlc` to empty. It assigns `C1525` only when the actual MPN is `CL05B104KO5NNNC` and the actual value is 100 nF. Runtime validation rejects any supplier tuple except `CL05B104KO5NNNC/C1525`, `IS25WP032D-JBLE/C1349020`, and `BC847B,215/C8576`; no 10 µF, 22 µF, 22 pF, 1 nF, or 10 nF capacitor inherits C1525.

The audit also found that donor input capacitor `GRM21BR61A106KE19L` is obsolete. All six input-bank positions now use Murata’s active same-0805 upgrade `GRM21BR61C106KE15L`, with no invented catalog code. The 22 µF `GRM21BR60J226ME39L` remains exact and active in current indexed evidence.

This package proves component identity and native footprint loading. The build wrapper intentionally omits schematic layout and pin electrical attributes, so its advisory warnings are not represented as a full schematic gate. No native schematic, board, firmware, XN file, routing, or USB runtime claim was produced.

## Capacitor-bank correction from exact Murata curves

Each TPS62825 rail now has two active `GRM21BR61C106KE15L` 10 µF/16 V input capacitors and two `GRM21BR60J226ME39L` 22 µF/6.3 V output capacitors. TI SLVSEF9I Table 8-3 validates the 0.47 µH converter in the nominal 47 µF output class; the 44 µF bank lies within that class's component-tolerance span. A proposed three-part 66 µF bank was not used because 66 µF is not an explicit checked cell.

The exact Murata typical curves show about 45% retention for the 10 µF part at 5 V and about 54% for the 22 µF part at 3.3 V. Conservative screens give `20 × 0.45 × 0.90 × 0.85 = 6.89 µF` input, 2.30× TI's 3 µF effective minimum, and `44 × 0.54 × 0.80 × 0.85 = 16.16 µF` output at 3.3 V, 1.62× TI's 10 µF effective minimum. These are engineering estimates from explicitly typical curves, plus an added 0.85 temperature allowance; they are not guaranteed PVT limits.

With TI's approximately 250 µs soft-start interval, capacitor-only average output charging currents are 581 mA at 3.3 V, 317 mA at 1.8 V, and 158 mA at 0.9 V. The six input capacitors present 60 µF to `5V_BUCK` (0.300 mC, 0.750 mJ); peak parent-rail current depends on its rise time and impedance. The core has 46.6 µF nominal including local XU/PLL decoupling. At TI's guaranteed 75 mA minimum discharge current at `VSW=0.4 V`, the charge bound from 0.9 V to 0.4 V is 0.311 ms while VIN remains present; the datasheet does not bound decay below 0.4 V.

The repeated banks increase the runtime package to 102 instantiated references. A fresh tscircuit circuit-JSON run and KiCad 10.0.4 `FootprintLoad` audit passed all 102 native footprint loads; no component MPN or unique-MPN count changed.

## Coordinator adoption

Runtime closed PASS from the observed host FINAL. Adopted the hardware module,31 new exact-MPN dossiers and its component-only native library. Five shared existing dossiers were preserved; their native footprint identities agree with the packet. The source package is now part of the new carrier, with full schematic, electrical and layout admission still owed. No firmware or old native board was adopted. Copied-asset hashes and the102-reference native inventory are retained under `06_build/tmp/digital-adoption/`.
