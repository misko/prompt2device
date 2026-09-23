# Independent review — TPS62822DLCR three-rail source proposal

**Verdict: CONDITIONAL PASS as a source-design adoption proposal.** The proposal is a materially better-supported candidate than a direct TLV62569 substitution and may proceed to isolated source implementation after the conditions below are incorporated. It is not a PCB, firmware, PCBA, thermal, sequencing, first-article, or order approval. Public stock is a dated availability screen only.

## Evidence and comparison

I reviewed proposal SHA-256 `2f599bc71b03a81967ac0eeb5a1dd11739c1d355e0cfab32f82d5fb16b2df776` against the retained accepted DMQ/TPS62825 source and public evidence. TI TPS6282x Rev C is retained as SHA-256 `47217a4e3b559423e2962d2a5c51b62e4d47de22c3bb04184c2ceff8c03b2b60`.

The substitution preserves a combination the TPS6282x data sheet specifically supports: 0.47 uH with nominal 47 uF output capacitance, 120 pF feedforward for the retained 100 kOhm lower feedback resistance, minimum 5 uF effective output capacitance, and minimum 3 uF effective input capacitance. This is a substantially sounder transfer basis than the prior rejected TLV alternative. It does not turn nominal-table evidence or typical capacitor curves into assembled PVT performance proof.

The raw public JLC records bind the exact proposed identities: TPS62822DLCR/C473385 has 1,979 units against a 165-unit threshold (three per board, five boards plus 150); ARG03BTC4533/C2686428 has 14,299 against 155; and CL21A106KOQNNNE/C1713 has 83,222 against 180. The exact MPNs, values and packages match the proposal: 2-A DLC regulator, 453 kOhm 0603 ±0.1%/25 ppm/C resistor, and 10 uF 16 V X5R ±10% 0805 capacitor. This does not reserve supply or prove order-time PCBA availability.

The 30% selected combined capacitor-retention factor is fairly labelled as an engineering screen rather than a characterization. The stated calculation is correct: `2 × 10 uF × 0.30 × 0.90 × 0.85 × 0.90 = 4.131 uF`, above the 3-uF input minimum. The old accepted DMQ source already treated input-capacitance and 85%-efficiency figures as engineering planning evidence, not guarantees. It is fair to retain that status while requiring a fresh E-CAP record for the exact Samsung MPN.

The feedback calculations correctly distinguish the old authored converter DC envelopes from device-pin operating requirements. The proposal's hard constraints are the downstream part limits at the pins: 3V3X constrained by XMOS USB33 at 3.00–3.60 V, 1V8 by flash at 1.70–1.95 V, and CORE by XMOS PLL at 0.855–0.945 V. The retained divider screen has usable but small dynamic allocations, especially 1V8. The 40 mV positive 1V8 allocation leaves about 11.9 mV to the flash high limit; it is a required measurement allocation, not a TPS62822 guarantee. The 3V3 and CORE allocations are similarly conditional on measured at-pin behavior.

Thermal comparison is fair to the accepted DMQ source. At 70 C ambient and a 125 C junction ceiling, the DLC JEDEC proxy allows 0.482 W versus DMQ's 0.425 W, corresponding to 87.56% versus 88.88% required efficiency at the 3V3X maximum output. The planning 85% parent allocation would fail either proxy if misread as actual conversion efficiency. Board-specific copper, enclosure, loss and temperature therefore remain physical validation, not a basis to reject source adoption now.

## Required source-acceptance conditions

1. Correct the two identified prose/geometry errors before the proposal becomes an adopted source record. With a 2.1-mm maximum body Y dimension and 0.25-mm courtyard clearance on each side, the minimum body-based courtyard Y span is **2.6 mm**, not 2.5 mm; enlarge it further if the pin-1 marker extends beyond it. The `200k/100k` alternative must say that its low DC corner cannot guarantee supervisor release, not that it prematurely releases reset below the rail floor.

2. Implement the exact DLC map and a project-owned land pattern: `1 EN, 2 FB, 3 AGND, 4 NC, 5 PGND, 6 SW, 7 VIN, 8 PG`. TI's drawing supports 0.60 x 0.25-mm lands. There is no exposed center pad. Keep NC and unused PG open, preserve the existing explicit sequencing topology, and make AGND/PGND treatment, quiet FB return, VIN/PGND input-cap loop, and SW copper intentional in source/CAD rather than inheriting the six-pin DMQ footprint.

3. Bind three exact TPS62822DLCR parts, one exact Viking 453 kOhm replacement, and six exact Samsung input capacitors in the part dossiers, source manifest, JLC identities, E-CAP evidence, and all source/native/KiCad parity inputs. Preserve the exact retained 0.47-uH inductor, 47-uF output capacitor, 120-pF feedforward capacitor, and feedback ratios unless a subsequent screen changes them.

4. Re-run source-level topology, margin, capacitor, BOM/stock, pin-map/footprint/courtyard, native DRC, and KiCad schematic/netlist checks on the composed candidate. E-MARGIN must record device-pin hard limits separately from derived DC setpoint screens and must not treat PWM-only reference limits, typical PSM/load regulation, or typical capacitor curves as guaranteed dynamic bounds.

These are normal composition and source-consistency conditions. They do not require a pre-prototype efficiency measurement or firmware work to accept the source-design change.

## First-article physical evidence still owed

Measure all three rails at their receiving pins over 5V_BUCK extremes, load and 70 C enclosure conditions: DC range, ripple, load-step overshoot/droop, ground shift and monotonic ramps. Confirm the 1V8 reset-release allocation, flash high margin, brownout falling trip, prebiased/rapid restart, CORE discharge with VIN present, and the `U_1V8_OK → CORE_EN → U_CORE` chain. Verify actual capacitance/ripple/startup behavior for the exact Samsung lot and local capacitor temperature stays within the X5R +85 C rating. Confirm DLC placement rotation/centroid, courtyard/silkscreen clearance, SW/input-return/FB layout, and board-specific thermal margin including simultaneous load. Refresh exact-MPN stock immediately before an order.

No firmware conclusion is made here. No source, PCB, order, or release artifact was changed by this review.
