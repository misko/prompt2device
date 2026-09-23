# TMUX4827YBHR 3×3 DSBGA native escape coupon

Diagnostic coupon only, not Crow source or a production board. Generated with KiCad pcbnew 10.0.4 by `make_coupon.py` from TI exact SCDS457B Figure 4-1 / Table 4-1 and YBH0009-C02 package drawing pp.32–34. Four copper layers. Rebuild with `/usr/bin/python3 make_coupon.py`; DRC with `kicad-cli pcb drc coupon.kicad_pcb --output drc.txt --severity-all --exit-code-violations`. KiCad reports **0 violations, 0 unconnected pads, 0 footprint errors**. Gerbers exported with `kicad-cli pcb export gerbers coupon.kicad_pcb --layers F.Cu,In1.Cu,In2.Cu,B.Cu,F.Mask,F.Paste,Edge.Cuts --output gerbers`.

| TI bump-side-down top-view ball | Net in coupon | Land (mm) | Escape |
|---|---|---:|---|
| A1 S1A | NC_A_P | Ø0.25 | F.Cu upward to TP_A1; unused A throw in proposed circuit |
| A2 SEL | AUDIO_EN | Ø0.25 | F.Cu upward to TP_A2 |
| A3 S2A | NC_A_N | Ø0.25 | F.Cu upward to TP_A3; unused A throw in proposed circuit |
| B1 D1 | ADC_P | Ø0.25 | F.Cu left to TP_B1 |
| B2 GND | GND | Ø0.35 copper, Ø0.25 mask/paste | Center filled+capped Ø0.35/0.20 through via, B.Cu to TP_GND |
| B3 D2 | ADC_N | Ø0.25 | F.Cu right to TP_B3 |
| C1 S1B | FILTER_P | Ø0.25 | F.Cu downward to TP_C1 |
| C2 VDD | 5V_LDO_HOLD | Ø0.25 | F.Cu downward to TP_C2 |
| C3 S2B | FILTER_N | Ø0.25 | F.Cu downward to TP_C3 |

Ball centers at x/y `19.6,20.0,20.4` mm, pitch 0.40 mm. All eight F.Cu launches use 0.09 mm tracks and travel straight outward; no inter-ball lane is used. Center B2 has no F.Cu launch. Coupon includes exterior test lands solely to terminate tracks for DRC and a B.Cu test land for via continuity; these are not proposed Crow components.

`coupon.kicad_pro` selects 0.10 mm Default netclass clearance (JLC 4L BGA via/pad floor), 0.09 mm track/board copper floor, 0.25 mm minimum via copper, 0.15 mm minimum through hole, 0.075 mm minimum via annulus, 0.25 mm hole-to-hole and 0.10 mm hole-to-copper. The selected project fab tier `jlc_4layer_advanced` in `skills/kicad-pcb/references/fab_tiers.yaml` allows 0.09 mm track/space, 0.25/0.15 via minimum and via-in-pad; the coupon's 0.10 mm local clearance is stricter than 0.09 mm. The center via annulus is `(0.35−0.20)/2=0.075 mm`. Its nearest distinct-net pad gap is `0.4−(0.35+0.25)/2=0.10 mm`, exactly the JLC BGA via-to-pad floor. Nearest via-hole-to-pad-copper gap is `0.4−(0.20+0.25)/2=0.175 mm`, above the coupon's 0.10 mm hole clearance. No second hole exists on the coupon, so hole-to-hole is a configured rule, not exercised evidence.

TI example Cu lands are Ø0.23 mm; JLC's current 4L BGA guidance gives Ø0.25 mm minimum, used for the eight perimeter lands. Center B2's capped via broadens *buried copper* to Ø0.35 mm, but local -0.05 mm mask and paste margins expose Ø0.25 mm. Gerbers `coupon-F_Mask.gts` and `coupon-F_Paste.gtp` independently contain one Ø0.25 mm flash at each of U_ISO1's nine 0.4-mm-grid ball centers, including B2; mask web between adjacent openings is 0.15 mm. The Ø0.25 paste aperture matches TI's sample stencil drawing. TI illustrates solder-mask-defined lands as permitted (NSMD preferred). JLC may CAM-adjust apertures; this coupon does not claim its uploader or assembly acceptance.

The board's existing source `03_src/rules/assembly.yaml` protects six LT3045 Ø0.50/0.20 vias with a complete 0.20 mm drill-family Type VII fill/cap selector. The proposed center via uses the **same drill family** but a second copper diameter Ø0.35. The selected via-process checker now accepts both protected copper diameters in one complete 0.20 mm drill family; the LT vias remain Ø0.50/0.20 and ordinary 0.30 mm drills remain outside fill/cap. The exact coupon-bound `escape_check.py` condition recognizes the no-lane 3×3 topology as conditional source feasibility on the advanced four-layer tier. A full-board via census, final routing, assembly spacing, process acceptance and audio measurements remain owed.

Primary references: [TI SCDS457B](https://www.ti.com/lit/ds/symlink/tmux4827.pdf), [JLC BGA design guidelines](https://jlcpcb.com/help/article/bga-design-guidelines---pcb-layout-recommendations-for-bga-packages), [JLC stencil openings](https://jlcpcb.com/help/article/opening-process-standard-of-stencil). TI PDF retained at `../TMUX4827_SCDS457B.pdf`, SHA-256 `3af04d7ae37b0e43c71c1b663a2d055667d94d46b5dc87c9ca2de24ec2295028`.

The coupon also has `coupon.kicad_dru` with a 0.09 mm `Default` netclass track-width floor. The read-only P-LAND probe (`p-land.txt`) reports **PASS: 17/18 copper pads graded, 1 B2 via-on-land, 0 failing**; 17 pads already have actual same-net tracks. The generic BGA lane heuristic remains unchanged for unrelated packages; this reviewed exact coupon has a separately gated conditional topology. The Excellon `coupon.drl` and `drill-report.txt` explicitly capture the single 0.20 mm through drill; process fill/cap is encoded as native via flags and remains an external order instruction, not an Excellon instruction.

Independent review `/tmp/crow-tmux4827-coupon-independent-review.md` **ACCEPTS diagnostic geometry only**. It highlights that the 0.100 mm via-to-pad gap sits exactly on JLC's published floor with no tolerance margin; the coupon's 0.075 mm annulus is configured and DRC-clean but is not a vendor yield guarantee. JLC may CAM-change the nominal Ø0.25 circular stencil to its default 0.23 mm rounded square. Full-board census of six LT plus eight TMUX protected vias, selective fill/cap uploader/CAM/PCBA acceptance and audio testing remain separate gates.
