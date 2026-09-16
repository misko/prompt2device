# Crow microphone pod v3 — v0.1.0 design release candidate

**DO NOT ORDER.**

DESIGN: PASS candidate — the exact routed PCB is layout-sealed, all 22
governed realized-path checks pass, route acceptance has zero FAIL, and native
KiCad DRC is 0 violations / 0 unconnected / 0 schematic-parity findings.

SOURCING: BLOCKED-SOURCING — no authenticated JLCPCB assembly allocation or
order economics receipt exists. The public 22/22 exact-code catalog screen is
only a negative filter and does not authorize payment.

ORDER VERDICT: DO-NOT-ORDER until every order and first-article hold below is
closed with retained evidence.

This is one analog microphone pod for the crow-roof array. It accepts the
governed 10.8–13.2 V spoke supply and returns one active-balanced analog audio
pair. The Raspberry Pi 5, Pluto+ receiver and audio conversion are central
system components; none is mounted on this pod PCB.

## Candidate upload files

- PCB: `fab/crow_mic_pod_v3_gerbers.zip` — two-layer board.
- Assembly BOM: `fab/bom.csv` — 22 grouped exact-code rows.
- Placement: `fab/cpl.csv` — 31 top-side SMT placements.
- `J1`, `MK1`, and bare `TP1`–`TP7` are intentionally absent from BOM/CPL.
  J1 is hand-soldered; MK1 is an off-board capsule wired to the marked landing;
  the test points are copper pads, not parts.

## Mandatory order-interface checks

1. Stop unless JLCPCB resolves every BOM row to the exact LCSC code and MPN in
   `fab/bom_echo_gate.txt`; any redirect is a substitution and requires a new
   reviewed source release.
2. Stop unless all 31 CPL placements are recognized on the top side with the
   exact coordinates and rotations in `fab/cpl.csv`.
3. In JLC's rendered placement preview, independently inspect U1/C2878631,
   U2/C16430 and D1/C2972759 for pin 1 or polarity. These single-channel
   rotations cannot be qualified by symmetry alone; see
   `fab/rotation_human_gate.txt`.
4. Confirm D2 polarity and U3 pin 1 against the sealed pin review even though
   their rotation rules have stronger corroboration.
5. Confirm J1 and MK1 remain absent from machine assembly. Do not accept a
   generic connector or microphone substitution.
6. Capture the authenticated JLCPCB allocation/economics table, screenshots or
   export and grade it against the exact final BOM and quantity 10. Public LCSC
   stock is advisory only.
7. Do not approve payment while any allocation, price, excess quantity,
   extended-part fee, assembly capability, rotation or substitution row is
   unresolved.

## Manual assembly and first power

- Fit exact Molex 43650-0400 J1 after PCBA; inspect all four solder joints and
  locating pegs, then prove cavity-to-pad continuity: pin 1 `12V_POD`, pin 2
  `GND`, pin 3 `AUDIO_P`, pin 4 `AUDIO_N`.
- Mount the exact AOM-5024L-HD-R capsule in the enclosure, strain-relieve its
  two wires, solder them to the marked MK1 landing and verify acoustic polarity.
- Inspect U2's exposed pad and every polarized/pin-1-sensitive part before
  power. The board-only STEP is a PCB/copper geometry artifact, not evidence of
  complete component or enclosure fit.
- Use a current-limited isolated supply and follow
  `verification/first_article_test_plan.md`. Abort for wrong polarity,
  oscillation, smoke/odor, current-limit operation, any rail outside its
  governed range or settled no-signal input current above 20 mA.

## Unclosed system evidence

Authenticated JLC allocation/economics, connector mate/service fit, harness
crimp and shield process, capsule mount and strain relief, windscreen/drainage,
4 m and 15 m audio performance, thermal behavior, ESD/EMC, condensation and
roof-environment qualification are all open. This release may preserve a
reviewed design candidate; it may not be represented as orderable, tested,
weatherproof or production-released.
