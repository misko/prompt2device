# Crow USB power-bound closure evidence

At initial adoption, withdrawing the false PPTC hard-current-limit claim deliberately caused a topology load failure. That is now superseded by the typed passive-distribution adoption: normal E-TOPO passes 13 rails, while E-FAULT rejects missing fault qualification. See [passive-distribution adoption](2026-09-22-passive-distribution-adoption.md). `early_design_check.py --capacitance` consumes every capacitor derating term and now rejects the first `UNBOUNDED...` DC-bias value instead of treating an unknown as zero. The same evidence gap exists in all eight banks.

The exact Murata TPS62825 characteristic sheets explicitly say their curves are typical. The exact AVX input-capacitor sheet says its statements and data are typical and presented without guarantee. The exact 47 µF Murata reference sheet supplies nominal tolerance, X7R class, and a 12.5% endurance change limit, but no exact guaranteed DC-bias lower bound at 5 V. Typical-only calculations remain useful screens: about 12.2 µF before aging for the TPSM input, about 5.5 µF before aging for each TPS62825 input bank after including its typical AC-amplitude effect, and about 11.3 µF before aging for the worst 3.3 V TPS62825 output bank after its typical AC-amplitude effect. None is a guaranteed worst-case value.

The consumed `N5V_BUCK` efficiency remains 85%. At 5 V × 1.9 A, this means 1.676470588 W loss. With 70 °C ambient and a 125 °C junction ceiling, the selected JLC04161H-7628G four-layer 1 oz board must realize θJA ≤32.807017544 °C/W. TI’s 33.5 °C/W figure uses a four-layer 2 oz test-board basis and cannot prove the selected board. The 88% alternative produces 1.295454545 W and 42.456140351 °C/W, but mixing that result with an 85% worst-case contract was the reviewed inconsistency.

The provisional digital rail allowances consume 1.184171123 A from the 4.95 V parent at the declared corners and 85% efficiency. Adding the retained 0.23 A quiet-analog screen leaves 0.485828877 A. This is an allocation remainder, not proof: direct 5 V devices, converter quiescent current, startup charging, and firmware-dependent XU current do not have a complete maximum census.

## Corrected E-CAP evidence boundary

The earlier coordinator requirement for manufacturer-guaranteed derating or lot-characterization data was too strict and is superseded. The owning `skills/kicad-pcb/scripts/early_design_check.py` defines conservative effective-capacitance calculations; `03_src/rules/contracts.md` requires exact fitted contributors, every derating term, and its basis/evidence. Neither requires manufacturer-guaranteed curves.

An exact-part typical characteristic may support a deliberately more adverse engineering allowance when its operating conditions, added allowance, and remaining qualification uncertainty are explicit. That is a conservative design estimate, not a production guarantee. Tolerance, voltage/AC-amplitude effects, temperature and lifecycle reserve must all remain accounted for. Endurance-test drift is not automatically a service-life guarantee. Startup, ripple and load-step behavior still require prototype verification; a numeric gate pass does not replace those measurements.

The current numeric placeholders remain unresolved until the proposed component/bank changes and their calculations are reviewed. No E-CAP pass is asserted by correcting this interpretation. Adding nominal capacitance alone is still insufficient.

## Coordinator adoption limits

This replaces unrelated battery-template rails, not an engineering approval.
The current contract now names INPUT_TRUNK from the authored net classes.
The branch PPTC trip current is not a guaranteed hard current limit: the
previous 0.70 A hard limit is withdrawn. The typed contract records only normal-load hold-current reference evidence. A time/current fault model remains required. DC-bias/aging numeric placeholders intentionally
fail E-CAP rather than claiming unsupported worst-case retained capacitance.

The next physical work must distinguish normal-load IR, startup charging and
fault duration; neither this source topology nor a typical capacitor curve
proves those limits. No required first-article measurement is claimed complete.
