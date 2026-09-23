# Independent adjustable TPS62825 / TPS389001 source review

Date: 2026-09-23

Review baseline: Crow USB source commit `500700a886a8774156171062f7f79626435064f6`.

Inputs reviewed:

- TI TPS6282x primary datasheet `projects/crow-usb-carrier-v1/02_parts/TPS62825DMQR/TPS6282x-SLVSEF9I.pdf`.
- TI TPS3890 adjustable primary datasheet `/tmp/crow-tps389001-20260923/projects/crow-usb-carrier-v1/02_parts/TPS389001DSER/TPS3890_SLVSD65A.pdf`.
- XMOS XU316 primary datasheet `/tmp/crow-tps389001-20260923/projects/crow-usb-carrier-v1/02_parts/XU316-1024-TQ128-C24/XM-014532-PC-v2.0.0.pdf`.
- Supervisor assessment `/tmp/crow-tps389001-assessment-20260923.md`.

## Disposition before exact source commit

The proposed substitutions are electrically feasible as a source candidate, subject to the ownership and propagation conditions below. The supervisor report is acceptable as an assessment, but it intentionally makes no source change. An exact regulator source commit was not yet available at the time of this initial disposition, so this is not an acceptance of uninspected implementation.

The proposed regulator corners independently reproduce to approximately 1.8222--1.8981 V for 210 kΩ / 100 kΩ and 3.2435--3.3932 V for 453 kΩ / 100 kΩ when using TI's 594--606 mV feedback limits, opposing 0.35% resistor corners, and adversarial ±0.05 µA feedback leakage. TI requires the lower resistor to be no higher than 100 kΩ and specifies 120 pF feed-forward for 100 kΩ; the proposal follows both points.

The 1.8 V high side is the tight limiting case. The flash operates to 1.95 V, leaving 51.9 mV above the proposed DC maximum. A proposed 40 mV combined overshoot, ripple, and ground allocation leaves only about 11.9 mV residual. This can be an explicit source engineering allocation with mandatory first-article measurement; it is not a vendor-guaranteed dynamic bound. The 3.3 V maximum remains comfortably inside the reviewed XU316 USB/I/O limits.

The adjustable supervisor arithmetic is consistent with the TPS3890 primary limits. The proposed 1.8 V divider has worst falling trip about 1.7246 V and worst rising release about 1.7893 V. The 3.3 V divider gives about 3.0323 V and 3.1743 V. These thresholds sit inside the proposed regulator DC envelopes and above the relevant downstream operating minima on falling trip. Each supervisor needs its own local divider and SENSE net; VDD, MR, CT, RESET, and open-drain wired-OR topology remain unchanged.

The fast-collapse calculation in the supervisor assessment does not establish a new source blocker. XMOS requires monotonic startup and valid I/O rails before reset release, and recommends close rail ramp completion; its reviewed primary text does not require external RESET to assert before an arbitrarily collapsing local rail crosses every operating minimum. TPS3890 specifies only typical falling propagation. The existing architecture already relies on physical rail decay and held-domain behavior for shutdown. Preserve abrupt-collapse and ordinary power-down waveforms as first-article qualification limits and do not claim guaranteed reset-before-undervoltage protection. The higher 3.3 V trip improves the old fixed 2.89 V threshold relative to the USB 3.00 V minimum; the 1.8 V trip is materially comparable to the old fixed threshold.

## Required source ownership

An acceptable implementation must update all consumers of the changed rail envelopes, including `power_tree.yaml`, capacitor derating evidence that currently cites 1.818 V / 3.38 V conditions, load and parent-current arithmetic, and monitor/CMOS-level assertions. It must retain the XMOS startup order: 1.8 V and 3.3 V domains valid before core enable/reset release, with 3.3 V domains not rising above the 1.8 V-mode absolute limit while VDDIOB18 is absent and core is present.

The source must add exact identities and local placement ownership for both regulator feedback dividers/feed-forward capacitors and all five supervisor divider pairs. It must preserve the held 3V3_ADC supply to the ADC-facing monitors, the five existing CT networks, reset net identities, and downstream ADC isolation logic. Direct JLC observations support sourcing screens only; they do not establish allocation, PCBA readiness, dynamic regulation, or first-article acceptance.

## Exact candidate review

### Adjustable TPS62825 stack `11d10575e0a1802f7a0834fdd89e561722267a78` + `3276c2d3b83992dfde2cb2ceef3da620df0f3e8e`: ACCEPT as a source candidate

The original commit had one material ownership defect: its new rail rows omitted the executable `feedback:` records, so a later wrong divider could retain green author-declared bounds. The repair closes this. `power_topology.py` now recomputes 1.822--1.898 V and 3.243--3.393 V from asymmetric 594/606 mV reference limits, exact divider values, 0.1% initial tolerance, 25 ppm/°C over 100°C, and conservative -50 to +50 nA FB bias. The declared outward windows cover those results. Independent runs returned E-TOPO 13/13 and E-MARGIN 11/11.

The TSX topology, exact identities, feedback and feed-forward connections, modular ownership, capacitor derating propagation, and qualification wording are coherent. Primary Yageo PDFs match the four exact MPN/value/package combinations. The schema-reader audit passes 969/969 with zero orphan keys. Retiring the two now-unused fixed-output dossiers leaves the common TI family primary in the selected adjustable dossier and makes the converter inventory exactly 3/3; it does not erase the files from git history.

### TPS389001 supervisor commit `40fb887e450b55e210cff64908a09e59a4adf2cc`: ACCEPT as a source candidate

All five changed supervisors retain their VDD, MR, CT, RESET, and downstream power-domain wiring. Each SENSE pin moves only to its own local 52.3 kΩ / 100 kΩ or 169 kΩ / 100 kΩ divider; the five divider pairs have distinct refs and local sense nets. The two ADC digital-rail monitors remain powered from held 3V3_ADC, their CT pins remain open, and their wired-open-drain `ADC_DIGITAL_OK` output is unchanged. U_1V8_OK and U_XU_3V3_OK retain 5V VDD/MR and their existing 10 nF / 1 nF CT networks. U_ADC_OK retains its pre-existing 3V3X VDD/MR/CT/reset topology while only its 3V3_ADC SENSE connection moves behind the divider.

The exact TPS389001/Yageo identities agree across source, dossiers, CSV, manifest, floorplan, integration, and modular ownership. The threshold arithmetic is conservative and fits the final proposed DC windows. The 20 mV low-side and 40 mV high-side dynamic numbers are explicitly engineering/first-article allocations, not supplier guarantees. No published primary constraint found in this review upgrades the documented arbitrary fast-collapse limitation to a source rejection.

Composition must still re-run the expected 506-component source census and resolve ordinary overlapping manifest/CSV/modular edits. These acceptances do not assert a routed board, waveform pass, JLC allocation, or release readiness.
