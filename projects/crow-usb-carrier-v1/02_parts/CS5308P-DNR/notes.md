# CS5308P supporting source authority

The current component datasheet authority is
`CS5308P_Datasheet_DS1314F2.pdf`, selected by
`datasheet.local` and its SHA-256 in `part.yaml`. DS1314F2 is the January 2026
manufacturer revision. The receive-stage topology
also depends on a distinct manufacturer application note:

- document: Cirrus Logic AN0556R1, *CS530x Input Buffer/Filter Circuits*,
  July 2025;
- official URL:
  <https://statics.cirrus.com/pubs/appNote/CS530x_Input_Buffer_Filter_Circuits.pdf>;
- local supporting file:
  `CS530x_Input_Buffer_Filter_Circuits_AN0556R1.pdf`;
- SHA-256:
  `14ae45dfdc660456c225eb103b0ea9b62b6d605944d98fe78180d6cc6f62b244`;
- captured directly from `statics.cirrus.com` on 2026-09-02; 18 pages.

AN0556R1 Section 1.2 and Figure 2 (PDF p.4) are the authority for the
differential non-inverting buffer/filter skeleton used on all eight channels:
two 1 uF input couplers, two 100 kOhm ADC_VMID bias resistors, the dual-op-amp
same-leg 300 Ohm feedback paths with 680 pF feedback capacitors, two 10 Ohm
output resistors, and the 15 nF differential capacitor. The note explicitly
requires buffered ADC_VMID and describes the shown unity-gain circuit as
supporting 2 VRMS differential input.

The project's admitted input remains the stricter 1.2 VRMS differential
first-article contract. AN0556R1 does not guarantee the selected OPA1656 input
common-mode margin, the CS5308P ADC_VMID production spread, long-cable
behavior, or realized-board THD; those remain separate analyses and physical
qualification holds.

## Retained power/reference supporting authority — 2026-09-07

Two byte-identical documents from the previously retrieved official Cirrus
package are now retained here for portable re-verification. The supporting
documents remain distinct from the current DS1314F2 component authority.

- Package URL: <https://statics.cirrus.com/pubs/software/DC5302P_4P_4S_8P_8S-ADC_Schematic_Layout.zip>.
- Reopened ZIP SHA-256: `2b4f99aad0eb5a562f25aacb8ab5147f4eeadbef7c2e35aea0abc4acb9aabda7`.
- `CS530x_Schematic_Layout_Guidelines_202507.pdf`, July 2025, SHA-256
  `a97e3cfbe311caf603bd56b7aeab189dd38727104168c26bb67dd24add07b62f`.
  Section 1.9/p6 identifies the 470-uF reference bulk and the low-frequency
  THD penalty of reducing it. Sections 1.6–1.9 support the existing effective
  capacitance record in `01_docs/evidence/cs530x-effective-capacitance-source.md`.
- `DC5308P_8S_ADC_SCH_REV_E0.pdf`, E0, SHA-256
  `fce5684d95855422693ada480b59c165f95cf710b85b0e55a07cd6e26a3b3d28`.
  Reopened bytes equal the named ZIP member. PDF p17 uses zero-ohm negative
  filter returns R351/R434 and one-ohm positive feeds R352/R435. The current
  carrier likewise connects physical FILT1N/FILT2N pins directly to GND; it
  has no nonzero negative-return resistors. The configurable reference
  board is supporting evidence, not authority to ignore DS1314F2's hardware-mode impedance selection and VMID guidance.

These files are read-only manufacturer precedents. Study and re-derive the
carrier source; never import the reference board's copper or infer physical
qualification of this design from the evaluation board.

## Public routed reference actually inspected — 2026-09-08

The ZIP above was **already known**, not newly discovered. Its same bytes were
fetched again directly from the public manufacturer URL. This pass additionally
inspected `DC530X-ADC-PCB-REV-E0.pdf` (14 pages), the nested Gerbers, PADS ASCII,
IPC-D-356 netlist, drill file and stackup. No account, upload, vendor contact,
alternate identity, copied copper or imported board was used. Raw vendor board
files remain outside the repository; derived measurements and hashes are in
`06_build/tmp/adc-source-20260908/reference-measurements.json`.

The rendered primary-side artwork and editable records show outward, staggered
configuration-pin drops and local ceramic/VMID ordering. The PADS descriptor is
`CS5308P-CN/B0-QFN48-Z`, not our selected DN. Empirical scaling of these ASCII
bytes against all 49 independently exported IPC pad positions gives maximum
disagreement 0.000002 mm; this is not a universal PADS-format unit claim or an
electrical pin-review verdict. All four CONFIG1/2/4/5 first drops also reconcile
against the IPC netlist. Their straight pin-to-drop spans are approximately
1.957, 1.395, 1.495 and 1.003 mm—not routed lengths.

Do not transplant numerical geometry: reference configuration exits are
0.191 mm, vias 0.40/0.20 mm (0.10 mm annulus), and the copper EP land is 4.8 mm.
Our source retains 0.50/0.20 mm vias, 0.15 mm annulus, and its exact 4.6 mm EP
footprint. The EVM's adjacent configuration-drop spacings are 0.749276 and
0.707893 mm; enlarging those vias would not preserve our 0.25 mm copper gap.

The manufacturer stack document describes an eight-layer, 1.6 mm board, 36 um
outer copper and 118.8 um outer reference dielectric. Its 191 um coated
microstrip calculation is about 50 ohms. Our four-layer 35 um/210.4 um outer
cross-section differs; the reference calculation neither validates nor
replaces our unsolved 0.36 mm digital-width hypothesis.

New inspected identities:

- PCB PDF: `81eacff60fb6685787c303fecee60ef9cb1630377e63be806d6d852168745f41`.
- Nested Gerber ZIP: `e2fb3e16f98595fe8ffd7488ccf661e440ce1a17c7094d35c1d9f3747dd4c45b`.
- PADS ASCII: `54bd33780b42550513ffb6b8faaea8cdf7bb5fd75a9ea32a1a63604bc0e06253`.
- IPC: `654d231f233c52bf51e274133113409acdf2dea12ece16e3ac3609c2b8dcd9ae`.
- Stack PDF: `2c5abe1e51c199b395e9dc895602720df608bf63d71f84ad1a09713f66dca690`.

ADR0013 records independently derived carrier decisions. Component values and
every physical qualification hold remain unchanged. DS1314F2
adds hardware-mode meanings to pins 36 and 38; the existing low/high straps select
mid impedance and noninverted BCLK respectively. Its new clock-phase rule is recorded
in the hardware/software interface and remains an implementation and first-article hold.
