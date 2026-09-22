# Crow USB power-bound closure evidence

The revised contract is fail-closed where the primary evidence stops. The SOL candidate initially passed 13 topology rows. After the coordinator
withdrew its false PPTC hard-current-limit claim, the live topology reader
correctly fails on that unresolved numeric field. `early_design_check.py --capacitance` consumes every capacitor derating term and now rejects the first `UNBOUNDED...` DC-bias value instead of treating an unknown as zero. The same evidence gap exists in all eight banks.

The exact Murata TPS62825 characteristic sheets explicitly say their curves are typical. The exact AVX input-capacitor sheet says its statements and data are typical and presented without guarantee. The exact 47 µF Murata reference sheet supplies nominal tolerance, X7R class, and a 12.5% endurance change limit, but no exact guaranteed DC-bias lower bound at 5 V. Typical-only calculations remain useful screens: about 12.2 µF before aging for the TPSM input, about 5.5 µF before aging for each TPS62825 input bank after including its typical AC-amplitude effect, and about 11.3 µF before aging for the worst 3.3 V TPS62825 output bank after its typical AC-amplitude effect. None is a guaranteed worst-case value.

The consumed `N5V_BUCK` efficiency remains 85%. At 5 V × 1.9 A, this means 1.676470588 W loss. With 70 °C ambient and a 125 °C junction ceiling, the selected JLC04161H-7628G four-layer 1 oz board must realize θJA ≤32.807017544 °C/W. TI’s 33.5 °C/W figure uses a four-layer 2 oz test-board basis and cannot prove the selected board. The 88% alternative produces 1.295454545 W and 42.456140351 °C/W, but mixing that result with an 85% worst-case contract was the reviewed inconsistency.

The provisional digital rail allowances consume 1.184171123 A from the 4.95 V parent at the declared corners and 85% efficiency. Adding the retained 0.23 A quiet-analog screen leaves 0.485828877 A. This is an allocation remainder, not proof: direct 5 V devices, converter quiescent current, startup charging, and firmware-dependent XU current do not have a complete maximum census.

Closing E-CAP requires binding lower bounds for DC bias, AC amplitude, temperature, and aging from manufacturer approval data or a controlled lot-characterization/procurement contract. If those bounds cannot be obtained, exact capacitor source changes and repeat proof are required. Adding nominal capacitance alone does not convert typical curves into guaranteed limits.

## Coordinator adoption limits

This replaces unrelated battery-template rails, not an engineering approval.
The current contract now names INPUT_TRUNK from the authored net classes.
The branch PPTC trip current is not a guaranteed hard current limit: the
previous0.70A limit is withdrawn and explicitly unresolved. A time/current
fault model remains required. DC-bias/aging numeric placeholders intentionally
fail E-CAP rather than claiming unsupported worst-case retained capacitance.

The next physical work must distinguish normal-load IR, startup charging and
fault duration; neither this source topology nor a typical capacitor curve
proves those limits. No required first-article measurement is claimed complete.
