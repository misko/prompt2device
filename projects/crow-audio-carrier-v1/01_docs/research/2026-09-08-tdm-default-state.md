# TDM default-state correction investigation — 2026-09-08

Status: confirmed source defect; correction candidate, not adopted design.
Subject: carrier source7b13bad1; exact returned review
[CARRIER-TOPO-001](../../08_reviews/2026-09-08_7b13bad1_fresh_topology.md).

## Confirmed cause

MEASURED: root parsed the actual native netlist at14:43:00Z. TDM_RAW contains
exactly U_ADC.25 and U_TDM.2; no bias or keeper. U_TDM is locally powered
and its OE follows MCH presence, not ADC transmit state. Both458-file
review packets and all subject digests were independently reverified.

CITED: [Cirrus DS1314F1 p36](https://statics.cirrus.com/pubs/proDatasheet/CS5308P_DS1314F1.pdf)
states DOUT is high impedance outside transmission. Table3-8 p12 gives
digital logic levels and input leakage, but its input-leakage row must not
silently be relabeled a guaranteed high-impedance output-leakage limit.
The PAD_DRV1_0 register description p76 identifies DOUT1's default drive
strength; verify its exact conditions rather than treating that setting as
a complete loaded VOH/temperature guarantee.

CITED: [TI SCES223U pp5–6/10](https://www.ti.com/lit/ds/symlink/sn74lvc1g125.pdf)
identifies standard CMOS inputs, a10ns/V maximum transition rate at3.3V,
and5µA input leakage. Its4pF input-capacitance entry is typical, not a
maximum. Disabling OE does not bias A.

INFERENCE: a weak pull-down solves the settled-state absence of bias only
under a stated leakage budget. If the ADC relinquishes a high output, the
same resistor/capacitance can make A decay slowly. A resistor-only repair
therefore requires both leakage/loading and transition evidence; it cannot
be accepted solely because the DC low-state calculation passes.

## Candidate, not yet adopted

Retain U_TDM's existing tri-state/Ioff boundary and place a genuine
noninverting Schmitt buffer between a biased TDM_RAW and U_TDM.A. This would
add one active part, its bypass and one pull-down, plus a new digital net.
It must preserve output polarity, remote-presence gating and all four power
states. Check complete BCLK-to-data timing, DC load, physical placement,
all path/branch declarations and added power before selecting it.

CITED: [Nexperia74LVC1G17 Rev16.1](https://assets.nexperia.com/documents/data-sheet/74LVC1G17.pdf)
explicitly accepts unlimited input rise/fall times. It has Ioff support,
1µA maximum input leakage and2µA power-off leakage. The3.0–3.6V delay table
gives5.5ns maximum through85°C and7ns through125°C under its specified
test conditions. Threshold tables use discrete supply points: do not invent
interpolated guarantees. A push-pull output delay is not itself an output
slew specification. Its SC-74A GV variant needs exact pin/package/source
verification before adoption.

Public identity candidates:
[JLCPCB C6076](https://jlcpcb.com/partdetail/Nexperia-74LVC1G17GV125/C6076)
and [LCSC C6076](https://www.lcsc.com/product-detail/Buffers-Drivers_Nexperia_C6076.html)
identify74LVC1G17GV,125. Observed through public web lookup2026-09-08;
search/catalog text is not a fresh exact-BOM stock receipt or PCBA allocation.
Use the existing selected10k/C60490 resistor and100nF/C1525 bypass only if
the complete calculations support them. No new dossier has been adopted.

Rejected shortcut: the [Nexperia74LVC1G125 datasheet p5](https://assets.nexperia.com/documents/data-sheet/74LVC1G125.pdf)
still specifies10ns/V above2.7V despite its introductory Schmitt-action
wording. A pin-compatible vendor swap does not establish unlimited slew.

## Required correction evidence

- Exact new primary dossier and public-code match; no account/vendor action.
- Red/green regression reproducing the current absent bias/input conditioning,
  with wrong-net/value/missing-part hostile cases. Extend existing declarative
  invariants instead of weakening gate coverage.
- Preserve all accepted analog/power geometry and full digital path/branch
  coverage; any new source pose must be independently screened natively.
- Archive the old request/checkpoint cohort recoverably before regeneration;
  no stale witness restamping. Full conductor, new exact public screen and
  fresh affected schematic reviews are required before placement.
- Source and prototype acceptance remain separate: no measured timing,
  assembly allocation, physical qualification or order permission is created.

The current source remains unchanged. This investigation is not an ADR,
accepted component selection, schematic correction or release witness.
