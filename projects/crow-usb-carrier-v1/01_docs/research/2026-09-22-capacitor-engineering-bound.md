# Capacitor engineering-bound candidate

This isolated candidate closes E-CAP with conservative design estimates. It
does not turn typical curves into supplier guarantees. The source adds
`C_IN3`, replaces each TPS62825 two-part 22 uF output bank with one 47 uF
`GRM32ER71A476KE15L`, preserves each `C_U_*_OUT_1` reference, and removes the
three `OUT_2` references. The output change uses a 1210 land consistently in
the TypeScript source. Its nominal 47 uF / 0.47 uH pairing appears in TI's
selection matrix; the matrix does not validate the full derating envelope used
here.

## Calculations

All losses are multiplied in the order implemented by E-CAP.

| Bank | Calculation | Estimate | Requirement |
|---|---:|---:|---:|
| TPSM63603 input | `3 * 10 * 0.90 * 0.60 * 0.85 * 0.90` | 12.393 uF | 9.4 uF |
| TPSM63603 output | `3 * 47 * 0.90 * 0.40 * 0.85 * 0.875` | 37.753 uF | 25 uF |
| each TPS62825 input | `2 * 10 * 0.90 * 0.30 * 0.85 * 0.90` | 4.131 uF | 3 uF |
| each TPS62825 output | `1 * 47 * 0.90 * 0.35 * 0.85 * 0.875` | 11.011 uF | 10 uF |

The exact `GRM21BR61C106KE15L` characteristic plots are typical. At 5 V they
show about 45% DC retention and about 80% further AC-amplitude retention, for
roughly 36% combined retention. The candidate retains 30%, so its voltage term
is more adverse than the plotted center. This corrects the earlier 5.508 uF
proposal, whose 40% retention was not more adverse than the combined plot.

The retained exact K-tolerance `GRM32ER71A476KE15L` PDF establishes 47 uF
+/-10%, 10 V, X7R -55 to 125 C, and +/-12.5% post-endurance capacitance change
after 1000 hours at maximum operating temperature and 150% rated voltage. It
contains no DC-bias curve. TI's TPSM63603 example instead names the adjacent
`GRM32ER71A476ME15L`; its `M` code is +/-20%, while the selected `K` code is
+/-10%. TI reports about 48 uF effective from two M-tolerance parts at 5 V,
approximately 51% typical retention per part. This candidate uses that only as
an adjacent-tolerance construction proxy, retains 40% at 5 V for the TPSM bank
and 35% at no more than 3.3 V for the TPS62825 banks, and never describes the
proxy as exact K-part curve evidence.

The 10% and 12.5% lifecycle entries are explicit engineering reserves. The
12.5% choice is informed by the exact K-part endurance test, but that finite
test is not a lifetime guarantee. The project has no declared service-life
duration, so no calculation here claims lifetime retention.

## Evidence and physical boundary

- Kyocera AVX exact `12105C106K4Z2A` PDF: exact identity, tolerance, voltage,
  X7R class, and typical voltage characteristics.
- Murata exact `GRM21BR61C106KE15L` characteristic PDF: typical DC- and
  AC-voltage screens used only to set a more adverse engineering estimate.
- Murata `GRM32ER71A476KE15-04CA` reference sheet: exact K-part identity,
  tolerance, temperature class, test conditions, and endurance result.
- TI SLVSFS5A: TPSM63603 25 uF effective output minimum, adjacent M-tolerance
  application BOM, approximate 48 uF effective output-bank statement, and a
  two-4.7-uF nominal ceramic input recommendation. The 9.4 uF input value in
  this candidate is the project's conservative effective floor; TI does not
  label it an effective-capacitance minimum.
- TI SLVSEF9I Table 8-3 and section 8.2.2.5: nominal 47 uF / 0.47 uH selection
  and the independent 10 uF effective-output and 3 uF effective-input minima.
  Table 8-3's footnote anticipates 35% effective-capacitance loss. This
  candidate retains 35% for its voltage term and then separately applies
  tolerance, temperature and lifecycle reserves, leaving 23.4% of nominal;
  therefore the table is nominal LC-selection support, not proof of the full
  conservative envelope or stability at its bound.

E-CAP is a source-stage engineering screen. Actual startup and load-step
stability proof remains owed. First article must still exercise startup,
steady ripple and load steps at input/output corners and hot ambient.
The current `first_article.yaml` schema has no capacitance or load-step fields,
so that work needs a separate explicit prototype acceptance record or a later
schema extension. Installed capacitance measurement is useful where practical,
but does not establish lifecycle behavior.

## Source and modular reconciliation

The authored census changes from 422 to 420 components: input power grows from
17 to 18, digital power falls from 27 to 24, and other block counts remain
unchanged. `C_IN3` is owned by `input_buck` and appears on both GND and
N12V_PROTECTED endpoints. The three retained `OUT_1` capacitors remain owned by
`digital_power` on GND and their corresponding output rails. No crossing-net
identity changes; only endpoint membership changes.

## Candidate validation

- E-CAP passes all eight banks with the estimates in the table above.
- A source-only executable TypeScript render set `pcbDisabled`,
  `pcbRoutingDisabled` and `schematicDisabled` before adding the design. It
  produced 420 source components, zero PCB components and zero PCB traces.
- `count_parity.py --pre-board` reports manifest/circuit parity at 420/420.
- `modular_design.py` reports 420/420 components and 53/53 crossing nets.
  Its machine-readable result is
  `06_build/evidence/modular_design_checker.json`.
- A full `tsci build` was attempted, entered PCB computation, and was stopped
  without a result after about six minutes because native PCB/conductor output
  is outside this candidate's scope. No output from that attempt is evidence;
  `03_tscircuit/build/circuit.json` comes from the source-only render above.

## Coordinator adoption verification

Root independently compared every retained source pin/net binding before adoption: no changes; exactly C_IN3 added, three OUT_2 references removed and three OUT_1 MPNs replaced. After adoption: TypeScript PASS; source expansion 420 components, 84 selected MPNs, 1,387 ports, 1,272 traces, zero source errors and 26 critical endpoint checks PASS. E-CAP passes eight banks. Modular plan covers420/420 components and53/53 crossings; floorplan covers409 nonconnector references and intentionally leaves11 connector poses unresolved. Integration support references were reconciled. Contracts338files, zero violations. These are source checks, not physical stability or native schematic acceptance.

Adopted input hashes:
- `03_src/rules/power_tree.yaml`: `bc2c6fc3137fff57cef417bcdc3c1b448b0f0b6e5e92ef8e6b5bd8cb2ce38370`
- `03_tscircuit/src/crow_usb_digital.tsx`: `6297c5cac1b4643795d61b5d00c0f615087bcf33e8b409a6453c945ad102938b`
- `03_tscircuit/src/crow_usb_input_power.tsx`: `a342200e0e79afd9cbfd2bab4245b216143dbe1b1178c3a2ab7a27ecc0e0e6a2`
