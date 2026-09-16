# First-article checklist

User directive D7 authorizes the ten-board first-article order after the live
uploader checks below pass. This checklist does not authorize production or
deployment.

## Before fabrication

- [ ] Confirm parent and pod `spoke_interface.yaml` are byte-identical.
- [ ] Run the generated-artifact spoke implementation check: J1 exact MPN and
      footprint, with pad 1=12V_POD, 2=GND, 3=AUDIO_P, 4=AUDIO_N (1/1 closed).
- [ ] Confirm the exact Würth 615008160221 RJ45 connector and Weidmüller
      8909650150 factory Cat6A patch-cord contract; this interface is custom
      analog/DC and must never be connected to Ethernet or PoE equipment.
- [ ] Confirm J1 is excluded from machine assembly and retained for manual
      soldering after PCBA; inspect all eight contacts, both shield tabs and
      both guide posts.
- [ ] Resolve every part sourcing hold with a dated JLCPCB PCBA response.
- [ ] Review rendered schematic against every manufacturer pin table.
- [ ] Run ERC, invariants, parity, DRC, layout policy and release provenance.
- [ ] Review connector mouth, mounting holes, enclosure datum and cable strain relief.

## Bare-board checks

- [ ] Inspect orientation marks on J1, D1, D2, U2 and U3.
- [ ] Verify no short from 12V_POD, VIN_PROTECTED or 5V_QUIET to GND.
- [ ] Measure the PTC path from J1.1 to F1.2; check D1 separately in diode
      mode rather than interpreting a nonlinear series-diode resistance.
- [ ] Verify J1 pin identity 1:+12V, 2:GND, 3:AUDIO+, 4:AUDIO− end to end.

## Fully populated first power

- [ ] Confirm the exact 33-reference population in `first_article.yaml`, the
      U2 exposed-pad solder joint, and every manual J1/MK1 joint before power.
- [ ] Current-limit the supply to 30 mA; do not stitch together evidence from
      a partially populated board under the fully populated card.
- [ ] Sweep 10.5, 12.0 and 13.2 V with correct polarity; record TP2/TP3/current.
- [ ] Apply reverse polarity with a 20 mA current limit at ambient and the hot
      boundary; verify VIN_PROTECTED remains -0.25 to +0.05 V and 5V stays off.
- [ ] Load 5V_QUIET to 20 mA; record regulation, ripple and U2 temperature rise.
- [ ] Confirm PTC/TVS parts and polarities before any surge/ESD test.

## Audio

- [ ] Verify TP4 = half rail on the same fully populated article.
- [ ] Inject a known low-level sine through a capsule-equivalent source.
- [ ] Verify AUDIO_P/AUDIO_N equal magnitude, opposite phase and 2.5 V common mode.
- [ ] Verify differential gain 18/11 V/V and channel-to-channel leg symmetry.
- [ ] Verify common mode stays within 2.35–2.65 V and differential output stays
      at or below 1.2 Vrms over the stated acoustic operating envelope.
- [ ] Test real capsule self-noise, frequency response and clipping through 110 dB SPL.
- [ ] Repeat gain/noise/stability/common-mode tests with the exact 15 m
      Weidmüller 8909650150 factory Cat6A cable and any shorter exact cord
      proposed for deployment.
- [ ] Verify the carrier decodes polarity consistently on all eight spokes.

## Environmental/mechanical

- [ ] Qualify capsule mount, port, windscreen, wire strain relief and drainage.
- [ ] Cycle representative enclosure temperature/humidity and inspect condensation.
- [ ] Demonstrate cable mating/service with neighboring enclosure hardware present.
- [ ] Perform project-defined ESD/EMC/surge tests at the complete enclosure boundary.
