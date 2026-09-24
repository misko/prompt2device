# XU exact-pin local power-neckdown architecture

## Finding

The current `DIGITAL_POWER` class assigns `N0V9` and `N1V8` a 0.60-mm
minimum width and 0.15-mm clearance in `03_src/rules/nets.yaml`. That width
cannot launch directly from the selected XU footprint's 0.25-mm-wide,
0.40-mm-pitch pads: at pins 14 and 17, a centred outward 0.60-mm track would
overlap the neighbouring-pad space by 0.025 mm. A 0.15-mm centred launch has
0.20 mm nominal clearance to each adjacent pad, so this solution need not
relax the existing 0.15-mm clearance.

The selected footprint source is
`03_src/lib/crow_usb_digital.pretty/TQFP-128_14x14mm_P0.4mm_EP_XU316.kicad_mod`:
pins 14/17 and 41 are 0.25-mm-wide lands at 0.40-mm pitch. The retained public
JLC 1-oz selected-stack record,
`01_docs/research/2026-09-22-usb-impedance-evidence.md`, records a 0.09/0.09-mm
minimum trace/space for multilayer 0.5- or 1-oz copper. Thus 0.15 mm is inside
the recorded fabrication capability, subject to exact-order review. It is a
project-owned geometry value, not an XMOS rule, current rating, or route pass.

## Proposed source-owned architecture

Do not lower the `DIGITAL_POWER` class. Instead, add a declarative
`xu_local_power_launches` source object which generates native rule areas and
custom rules for these exact branches only:

| ID | Net | Exact permitted branch |
|---|---|---|
| `XU_VDDIO17_LOCAL` | `N1V8` | `U_XU.17` to `C_XU_VDDIO_17.1` |
| `XU_VDD14_LOCAL` | `N0V9` | `U_XU.14` to `C_XU_VDD_14.1` |
| `XU_PLL41_LOCAL` | `PLL_0V9` | `U_XU.41` to the declared PLL-filter/capacitor branch, only if the final exact route requires it |

Each entry must identify the XU pad, capacitor/filter endpoint, F.Cu-only
outward window, and a named flare boundary. The generator derives the window
from the actual footprint pad and the declared branch geometry on an exact
native board. Inside it, an exact-net rule requires a 0.15-mm track; at the
flare boundary the normal net-class width resumes. `N0V9` and `N1V8` therefore
resume the existing 0.60-mm rule outside their own windows.

`PLL_0V9` is absent from the current `nets.yaml` classes and must first receive
an explicit PLL-filter net class. Do not allow it to inherit the 0.20-mm
default silently. Its normal width and any U_XU.41 launch exception require a
separate project decision; XMOS supplies a qualitative clean/filtered/local
PLL requirement, not a numeric trace-width limit.

## Offsite guardrails

- Match every exception by exact net, `U_XU` reference, pad number, layer and
  generated rule-area identity. Do not use wildcards or a package-wide rule.
- Preserve the 0.15-mm clearance rule. The exception changes width only.
- Prohibit vias, branches and foreign-net copper in every launch window.
- Fail an audit if any `N0V9`/`N1V8` segment narrower than 0.60 mm is not
  completely contained by one declared launch window. Apply the same rule to
  `PLL_0V9` after its normal class is declared.
- On the exact saved/re-filled native board, extract and render each launch;
  prove it starts on its named XU pad, reaches the declared flare, retains
  clearance to every foreign feature, and has no unconnected/DRC finding.
- Keep the exceptions out of converter loops and distribution trunks. A short
  physical neck does not establish its current share, IR drop, thermal margin,
  or transient behavior.
- Independently prove the named capacitor ground-pad return to U_XU
  centre-ground/ground pins and the continuous reference plane. The width rule
  does not close XMOS's direct, short decoupler-return requirement.

XMOS source `XM-014532-PC v2.0.0` (retained at
`02_parts/XU316-1024-TQ128-C24/XM-014532-PC-v2.0.0.pdf`) supports local VDDIO
decoupling and direct/short returns, and requires a local, filtered clean
PLL_AVDD supply. It does not publish a 0.15-mm launch, a maximum neck length,
or an acceptable via count. The architecture is therefore a bounded future
native-test mechanism, not route, power-integrity, or release acceptance.
