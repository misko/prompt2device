# ADR-0004 — Cirrus AN0556 Figure 2 receiver topology

Status: superseded in part by ADR-0023 (amplifier identity and VMID isolation); other historical decisions remain as scoped there
Date: 2026-09-01

2026-09-07 amendment: ADR-0008 supersedes only this record's internal-ADC-
VMID source and ground-leg reference-return choices. The power-source
startup/stability statement below is superseded by the explicit source
blocker in SOURCE-CORRECTION-20260907.md; it is not solely a bench debt.

Use the Cirrus AN0556R1 Figure 2 differential non-inverting circuit for every channel, including two 1 µF coupling capacitors, two 100 kΩ VMID bias resistors, one OPA1656 dual, 300 Ω same-leg local feedback from each inverting node to its own ADC-input branch, 680 pF C0G feedback, two 10 Ω output resistors, and one 15 nF C0G differential capacitor. Buffer ADC_VMID1 and ADC_VMID2 with a ninth OPA1656 dual; each follower closes feedback at its raw output and then drives VMIDx_BUF through 100 Ω with 4.7 µF from VMIDx_BUF to ground, matching the vendor isolation/filter network.

The two buffered-VMID shunts are exact polarized Panasonic
EEEFK1V4R7R/C401730 parts in `CP_Elec_4x5.8`: pad 1 positive to
`VMIDx_BUF`, pad 2 negative to ground. The ADC filter/LDO bank uses the exact
Murata, Samsung and KEMET identities frozen in the part dossiers, with nominal
values raised to 4.7 µF at LDO/raw-VMID bulk, 470 nF at raw-VMID HF, and
1 µF plus 10 µF at each `ADC_FILT` pair. The executable E-CAP proof
charges every ±10% MLCC by 50% DC bias, 15% temperature and 10% lifecycle loss
in addition to tolerance. Those choices clear the Cirrus effective minima;
LDO startup/stability, VMID settling, reference ripple and THD remain
first-article measurements because no production maximum-capacitance claim is
made.

The sixteen signal-path coupling capacitors are exact KEMET
R82DC4100DQ60J/C183545, 1 µF ±5%, 63 V metallized stacked PET film parts.
They are nonpolar, stable-dielectric, 5.00 mm-pitch through-hole parts with the
manufacturer 7.2 x 5.0 x 10.0 mm body envelope. They are intentionally manual
first-article population; neither the LCSC catalog row nor this selection is a
claim that JLC has accepted the THT process. Low-frequency gain and THD+N stay
in first-article qualification, and value-only/dielectric substitution is
forbidden.

This is selected over a direct-cable-to-ADC connection because CS5308P hardware mode fixes the mid-impedance input configuration and Cirrus explicitly requires the external buffer/filter and buffered VMID for this use case.
