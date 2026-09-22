# JLCPCB stack/process evidence captured 2026-09-22

Public primary sources:

- `https://jlcpcb.com/impedance`
- `https://jlcpcb.com/api/jlcTools/impedance/selectPageImpedanceDefaultTemplate`
- `https://jlcpcb.com/help/article/jlcpcb-copper-weight`
- `https://jlcpcb.com/capabilities/Capab`
- `https://jlcpcb.com/help/article/user-guide-to-the-jlcpcb-impedance-calculator`
- `https://jlcpcb.com/capabilities/pcb-assembly-capabilities`

The public stack API was queried with JSON
`{"plateLayerNumber":4,"plateThickness":1.6,"cuprumThickness":2,"innerCopperThickness":0.5}`.
It returned seven matching templates. The sole returned `defaultFlag: 1` template was
`JLC04162H-7628`, access id `d1c2fdb8902a452fb2baa9f55359d142`:

| order | layer/material | thickness | Dk |
|---|---|---:|---:|
| 1 | L1 copper, 2 oz | 0.0700 mm | n/a |
| 2 | 7628 RC49% prepreg | 0.21040 mm | 4.4000 |
| 3 | L2 copper | 0.0152 mm | n/a |
| 4 | NP-155F core dielectric | 1.0650 mm | 4.3800 |
| 5 | L3 copper | 0.0152 mm | n/a |
| 6 | 7628 RC49% prepreg | 0.21040 mm | 4.4000 |
| 7 | L4 copper, 2 oz | 0.0700 mm | n/a |

The API labels the core `1.1mm H/HOZ with copper`; its 1.065 mm dielectric plus two
0.0152 mm inner copper foils is 1.0954 mm. The listed construction sums to 1.6562 mm,
so the marketing thickness is not an arithmetic 1.6000 mm physical sum.

JLCPCB's copper-weight guide, updated 2026-09-09, specifies 0.16/0.16 mm minimum
trace width/space for 2 oz on any FR-4 layer. The general capabilities page also
contains a conflicting 0.15/0.15 mm multilayer statement. The conservative current
rule is therefore 0.16 mm until JLCPCB resolves the contradiction in an order review.
The immutable TPSM source has 0.15 mm minimum copper separation, so compatibility
with 2 oz is not established. The XU316 footprint has 0.22 mm lands on 0.40 mm pitch,
leaving 0.18 mm nominal copper space, and JLCPCB lists 0.4 mm as an Economic-PCBA
minimum IC pin pitch.

The calculator guide, updated 2026-09-16, explicitly says its external-copper model
supports only 1 oz, despite fabrication support for 2 oz, because wider 2 oz trace
tolerance hinders impedance control. Its documented outer-layer model uses 1.6 mil
copper, 1.2 mil base mask, 0.6 mil mask over copper, 1.2 mil mask between traces,
mask Dk 3.8, and a top width 0.7 mil narrower than the base. Therefore no 90-ohm
geometry is recorded for the 2 oz template.

