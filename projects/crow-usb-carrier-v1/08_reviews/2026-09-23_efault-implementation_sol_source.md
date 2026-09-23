# Independent E-FAULT implementation review — 2026-09-23

**Verdict: ACCEPT as a conditional source-stage candidate.** Reviewed isolated commit `f5f558c695147afde2e32ea405ee57eb81206ea0` on base `fd48917c` in `/tmp/crow-efault-external-source-20260923`. Working tree clean. This verdict authorizes composition/review of the source contract; it does not qualify a supply, promise a hot fuse will remain closed, or admit a PCB layout.

The new `external_source_fuse` branch is exclusive of the legacy programmable-breaker/no-requirements branches. It binds the exact fresh source-circuit SHA-256 `b68fd99fad9092260c1e2fd2630cf1a63ce334057802e6c464aa6052b8ab307c`, fitted identity/value and named-net ports for J_PWR→F_IN→Q_IN, Q_IN gate/clamp and input TVS, all three post-FET input capacitors including return pads, U_BUCK input, all eight TPS26625 input/OUT/RTN/GND/ILIM/dVdt connections, and J1–J8 supply/return pins. It rejects missing/extra bound refs, extra TPS26625s, ambiguous source joins, stale digest, contradictory protection-path scalars, nonfinite/Boolean/missing numerical source fields, and auto-retry wording that renews the excess-current allowance.

The conditional envelope is explicit: 11.4–13.2 V and 2.185 A normal/one-fault delivery; ≤3.4 A instantaneous current at J_PWR including external source/cable capacitance; cumulative time >2.85 A ≤10 ms across the entire fault episode; thereafter ≤2.85 A or off until fault removal and deliberate input power-cycle; recovery ≤13.2 V. At the declared engineering allocations (Q_IN 50 mΩ hot, 123 °C/W, 70 °C ambient), computed steady/peak junction screens are 120.0/141.1 °C versus 150 °C. The 0.1156 A²s pulse comparison is only 3.7% of the 3.152 A²s **nominal** fuse melting entry; the checker does not use that nominal entry as a hot non-opening guarantee. The former 8–50 A fuse-clearing mode is no longer admitted.

Independent replay at this commit:

- `python3 -m unittest discover -s tests -p test_external_source_fault.py -q`: **17/17 pass**.
- `python3 tests/t1_early_design.py`: **52/52 pass**, including 40 expected-rejection fixtures for the legacy breaker and passive-distribution behavior.
- `python3 skills/kicad-pcb/scripts/early_design_check.py /tmp/crow-efault-view-20260923`: **5/5 Crow gate families pass**, E-FAULT explicitly prints `CONDITIONAL`. This temporary view links the candidate `03_src` and reviewed root diagnostic `06_build/verification/adc-composition/circuit.json`, whose bytes match the pinned `b68fd99f…` digest.
- `git diff HEAD^ HEAD --check`: clean. No TSX or canonical-build file is in the commit.

The project’s historical canonical `03_tscircuit/build/circuit.json` has SHA-256 `ead8cb33c07afcb9dd371a5c61188c8f2fde59c55c9e703400d5b21765daa336`; direct checking against it **correctly fails closed** on digest mismatch. Source composition must retain the fresh diagnostic association, and later canonical regeneration/admission must pin the actual reviewed bytes. This is an intentional current-state distinction, not an implementation defect.

Open downstream gates are stated in the source contract: choose and qualify an exact isolated supply/cable load line and rearm waveform; measure external and local post-fuse capacitor discharge, hot F_IN/Q_IN behavior, branch hard-short/overlap and startup, and recovery voltage on first article. These are physical/supplier qualification tasks, not missing source-stage checker bounds.
