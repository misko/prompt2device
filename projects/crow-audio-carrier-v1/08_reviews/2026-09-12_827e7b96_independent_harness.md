# Independent Cat5e pod-harness source review

**Engineering verdict on the frozen input packet: DEFECTIVE.** Delivery evidence itself is complete. The shared electrical contract is coherent and conservatively carries its physical holds, but two child connector-service source claims do not match the selected, unqualified installed harness.

## Findings

1. **[DEFECT] Pod cable construction contradicts the selected manufacturer part.** `projects/crow-mic-pod-v3/03_src/rules/connector_assemblies.yaml:113` calls the cable “two individually shielded twisted pairs,” while lines 114–116 select Belden 7939A. The supplied Belden PDF identifies 7939A as four bonded 24 AWG pairs with one overall foil shield and drain. This stale 6541PA-era description can misdirect termination and shield work. Minimal repair: state four twisted pairs with overall foil shield/drain. The supplied supplement makes exactly that correction.

2. **[DEFECT] Both child connector-service contracts overgrade the installed cable evidence.** `projects/crow-audio-carrier-v1/03_src/rules/connector_assemblies.yaml:95` and `projects/crow-mic-pod-v3/03_src/rules/connector_assemblies.yaml:121-126` use `grade: conservative` although the same blocks say WAGO joins, pigtails, routing, and service space remain unqualified. Because those facts govern whether the selected cable assembly can physically fit and be serviced, the installed-cable route evidence is unknown until physical qualification. Minimal repair: grade the cable block `unknown` and bind it to an `installed-cable-route-qualification` source deferral. The supplied supplement does this for both children. The carrier declaration uses the existing typed phase schema; admission/execution of the new pod phase wrapper was not included, so that gate remains to be demonstrated before source acceptance.

The nine supplied interface tests contain two positive checks and seven known-bad cases. They cover three-copy byte identity, missing-child and YAML-key failure, pin-map drift, pair allocation, single-power-pair resistance, and non-cable resistance allocation. Neither the checker nor the tests consume `connector_assemblies.yaml`, so their PASS does not contradict these findings and does not close the service-contract defects.

## Confirmed engineering

The three `spoke_interface.yaml` copies are byte-identical at SHA-256 `827e7b969c7af915f2f528446eb485e71d21eff405f5f401cadfa9a9b497e627`, and both child checkers pin that same hash. All eight conductors are represented: blue carries AUDIO+/AUDIO−; orange, green, and brown each carry one +12 V and one return. At 15 m, 93.8 ohm/km, and three conductors per rail, cable loop resistance is 0.938 ohm. Applying 1.25 hot multiplier and the explicit 0.30 ohm non-cable allocation yields 1.4725 ohm, 0.14725 V drop at 100 mA, and 10.65275 V from the 10.8 V minimum carrier supply. This meets the 2.2 ohm and 10.5 V design screens.

The contract retains the four-position Micro-Fit pinout and one wire per contact. Three 24 AWG wires plus one 22 AWG Belden 8503 pigtail occupy separate ports of each WAGO 221-415; each Micro-Fit power contact receives one 22 AWG pigtail, and each audio contact receives one 24 AWG cable conductor. Supplied records support the WAGO conductor ranges, 43030-0007 support for 20/22/24 AWG up to 1.85 mm insulation, and 8503 nominal 1.3 mm insulation diameter.

No RJ45, Ethernet, PoE, hot-plug, PCB pin-map, or sealed-release change is introduced. The move from individual pair shields to one overall shield is explicitly paired with carrier-entry chassis bond, pod-end isolation, and renewed analog qualification. The 7.49 mm cable diameter, retained 53 mm planning bend/straight allowance, glands, sixteen carrier-side joins, two pod-side joins, strain relief, weather sealing, thermal behavior, complete hot loop, audio gain/noise/crosstalk/phase, inrush/fault behavior, and one-fault/seven-healthy operation all remain expressly OWED. Nothing in the packet claims an assembled or qualified harness.

## Supplement disposition

The four supplement files were copied into review scratch after their source hashes matched the supplied manifest; copy hashes matched again. The two modified connector-service files repair the two original findings without changing limits or pin mapping. The two phase declarations express the outstanding installed-route work. On the presented bytes, no further Cat5e harness source defect was found; typed admission and execution of the pod phase declaration remain outside this supplement evidence.
