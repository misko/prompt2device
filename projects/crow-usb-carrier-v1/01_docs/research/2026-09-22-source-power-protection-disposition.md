# Source power and protection disposition

Reviewed subject: Crow USB source at `a9bdd97d` plus the pending PLL identity-only
candidate. The PLL identity change does not alter the power or protection paths.

## Source calculations closed

- The external supply contract is 11.4--13.2 V at J_PWR under the 2.185 A
  one-fault screen. The 4 A `0451004.MRL` has a 2.85 A at 70 C engineering
  continuous screen and 0.665 A margin. Source faults are admitted only as the
  bounded fuse-clearing or current-limit/hiccup modes in
  `protection_paths.yaml`; an ordinary regulated supply is not required to
  force fuse clearing.
- The shared 150 milliohm path, 20% adverse-drop charge, and eight 1710
  milliohm spoke allocations pass E-MARGIN. TPS26625's 145--159 mA limit is
  explicitly tied to its 24 V/1 V-drop table condition and is not presented as
  a guaranteed 12 V hard-short transient. One-fault/seven-healthy, retry
  heating, routed copper, and actual source foldback are first-article tests,
  not missing source arithmetic.
- LT3045 uses a 250 mA allocation against a 224.831 mA established static
  screen. Its 583.75 mW adverse dissipation fits the 650 mW board engineering
  capacity with 66.25 mW reserve, conditional on effective theta-JA no greater
  than 84.6 C/W at 70 C. Input/output effective-capacitance and dropout checks
  pass.
- The conservative 752 uF aluminum-only hold screen loses about 33 mV during
  an explicit 100 us adverse engineering allowance from unheld `5V_BUCK`
  detection through `PWR_EN` to `U_AUDIO` isolation at 250 mA. This allowance
  is a qualification target because TPS3890 publishes typical, not maximum,
  falling propagation. The later dump transition (about 4.21 ms fixed-rail
  engineering screen) is an active-discharge event, not the isolation hold-up
  deadline. PGFB fast-start hands off at 2.906--3.149 V, below the 3.22 V rail
  floor. Ramp, handoff, isolation, dump, and reset waveforms remain first-article
  evidence.
- The VBUS detector is an insulated-gate NMOS path: VBUS reaches only the gate
  through 100k/1M with no intended conductive power path into the unpowered 1V8 carrier domain; specified leakage and parasitic transients still require their qualification checks.
  Its gate is about 0.909 VBUS; the full USB VBUS range is far above the
  AO3400A threshold range while the 10k drain pull-up requires only 180 uA.
  Connector VBUS capacitance screens 3.5955--5.9455 uF within the adopted XMOS
  self-powered reference range. Hardware reset/clock gating assertions pass
  70/70 and the ADC reset screens give 9.102 ms initial high and 19.602 ms low.
- `W25Q128JWSIQ` powers from 1V8, starts in SPI mode with fixed QE, implements
  the ROM's EBh/24-bit transaction, and has 20 us maximum read readiness against
  XU316's 300 us requirement. Firmware still owns active-low VBUS interpretation,
  detach policy, image creation, and functional USB/TDM behavior.

## Disposition boundary

The three findings can close at source design: protection coordination,
voltage/load/thermal allocation, and pin-level power-state/boot behavior now
have explicit engineering contracts. Closure does not qualify source foldback,
fault energy, hot retry, routed resistance, regulator temperature, startup or
shutdown waveforms, USB back-voltage behavior, enumeration, or audio capture.
Those remain native-layout or first-article gates and must stay in the test
plan and commissioning/layout records.

Root disposition: source engineering portions are accepted. Existing DESIGN_CLEAN findings remain open for their native/layout or physical obligations; this source review does not close broader final-design claims. First-article execution and firmware creation remain separately unauthorized.
