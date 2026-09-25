# Four-part TI VMID / ADC8 placement bound

**Rejected bounded search; no P1 or P2 placement claim.** `probe.py` binds the
exact four-part ADC7 board SHA
`046019a13094764baef313d62611b137e0f0af971079734c71ab050dbf46b3a0`,
the TI baseline, source/floorplan, and checker. It verifies that all 27
P1-fixed poses and every pad number, net, and layer remain identical before
searching. No board is edited or saved. The [receipt](receipt.json) records
the 0.1-mm unrotated grid and all measured bounds.

For each `R_B1P`–`R_B8P`, the complete native body/courtyard envelope extends
**0.975 mm east** of its channel owner. Moving it west by that minimum at
y=63 mm collides with its channel's `C_ADC_ACnN1` envelope. With all other
poses fixed and at least 0.15 mm between physical envelopes, the nearest
local legal grid pose for every resistor is **1.0 mm west and 5.1 mm south**
(5.197 mm total move). It leaves only **0.025 mm** to the owner's east edge,
which is not a useful routing mouth. Requiring an illustrative 0.56 mm
east-owner margin and 0.56 mm from other envelopes moves the nearest pose to
**1.6 mm west and 5.5 mm south** (5.728 mm total). This raises the related
`BIAS_Pn` pad-center distance to `C_AnP.2` from about 8.77 to 12.40 mm
(1.414×). The 0.56-mm mouth is a screen only; it does not demonstrate an
actual trace or return via.

`C_ADC_AC8N1` is the decisive obstruction for this nine-reference move set.
Its current physical envelope `[194.205,61.255,199.795,64.745]` mm is
inside `analog_ch8` but overlaps `usb_vbus_sense` at y≥62 mm. A whole-envelope
search over the **entire** analog_ch8 owner on the 0.1-mm grid, keeping every
other native pose fixed, found 50,325 owner/foreign-clear origins and 15,376
with ≥0.15 mm body/courtyard separation. Yet the nearest separated origin
is **(197.0, 51.0) mm**, a 12.0-mm move. Its `ISO8N` distance to `U_ISO8.6`
is 10.825 mm versus 9.142 mm baseline, and its `ADC8N` distance to
`C_ADC_CM8N.1` is 19.170 mm versus 11.811 mm baseline. The best worst-case
related-pad ratio over all separated origins is **1.569×** at
`(193.5,49.7)` mm, a 13.753-mm move. None meets the explicit exploratory
**≤1.5×** locality screen for both nets. That 1.5× threshold is a research
filter, not an authorized electrical design rule.

The combined nine-part candidate is therefore **rejected before native DRC
or routing**. This is a grid and locality bound with unchanged rotations and
all other parts fixed, not a proof that any larger refloorplan is impossible.
The existing In1.Cu GND zone is unfilled, so no return loop or actual route
space is accepted. A source-owned redesign would need to move additional
channel-8 neighbors or recut typed ownership, then regenerate a board and
check pad access, routing, return, DRC, and related-part distances. No
capacity, P1, P2, or stock credit follows.

Reproduce from the repository root:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-vmid-eight-part-bound-sol/probe.py > /tmp/ti-vmid-eight-part-bound.json
```
