# Conditional external-source fault contract

This source-stage contract retains J_PWR → F_IN (0451004.MRL) → Q_IN
(DMP6023LFG-13) → N12V_PROTECTED, the parallel U_BUCK, and eight
TPS26625DRCR branch limiters. It does not add an aggregate breaker or claim
that an isolated supply has been selected or qualified. The exact fitted
44.2 kΩ ILIM and 10 nF dV/dt parts, gate pull-down/clamp, input TVS,
three post-Q_IN 10 µF capacitors, eight U_SPOKE outputs/returns, and J1–J8
power/ground pins are bound to a reviewed source circuit digest by E-FAULT.
The prior programmable-breaker E-FAULT branch remains available for other
projects.

The external isolated source and cable must deliver 11.4–13.2 V at J_PWR
at 2.185 A continuously, including one static branch-limited fault, without
foldback or hiccup. In an aggregate/TVS fault, current at J_PWR including
source-output/cable-capacitor discharge is limited to 3.4 A instantaneous.
Across the **entire fault episode**, cumulative time above the 2.85 A hot
continuous allocation is at most 10 ms. Thereafter the source is at or below
2.85 A or off while the fault remains. Autonomous retries may not obtain a
new >2.85 A allowance. A new episode requires fault removal and explicit
input power-cycle. Recovery may not exceed 13.2 V. These are procurement and
test requirements, not measured characteristics of any supply.

At the 50 mΩ Q_IN hot engineering allocation and minimum-pad 123 °C/W
thermal resistance from Diodes DS37204, 2.85 A sustained screens to about
120.0 °C junction from 70 °C ambient; 3.4 A screens to about 141.1 °C,
below the 150 °C junction limit. The 10 ms maximum at 3.4 A is 0.1156 A²s,
about 3.7% of Littelfuse's **nominal** 3.152 A²s melting entry. Neither
calculation proves fuse non-opening or hot-board survival. The formerly
admitted 8–50 A fuse-clearing mode is now historical only: at 8 A the 50 mΩ
Q_IN allocation implies 3.2 W, with no proof spanning the fuse's possible
5 s clearing interval.

Before purchase or release, qualify an exact isolated supply/cable load line,
source/output-capacitor discharge and retry/rearm waveforms at J_PWR, local
post-fuse capacitor discharge, hot F_IN/Q_IN gate drive and thermal behavior,
eight branch hard-short/overlap and all-pod startup/cable loading, and
recovery voltage. The TI 0.159 A TPS26625 row is a VIN=24 V,
VIN−VOUT=1 V static table screen; it is not a Crow hard-short maximum.
Normal and one-fault connector-plane service remains subject to the existing
10.8 V and input-path first-article gates. Multi-fault uninterrupted service
is not claimed.

Primary material: TI TPS2662 SLVSDT4F, Diodes DMP6023LFG DS37204 Rev 2-2,
and Littelfuse 451/453 series PDFs retained under `02_parts/`. Independent
engineering review: `/tmp/crow-aggregate-fault-independent-review.md`.
