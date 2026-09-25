# Integrated TI placement union: rejected native DRC screen

This is a reproducible **research-only rejection**, not a P1 or P2 board. The
frozen TI prototype board is SHA-256 `8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`.
`build.py` uses its pinned TI floorplan, parts, library, and netlist. It imports
only the reviewed `Q_PRE=(46.0,107.15,0°)` anchor from the current canonical
floorplan, then composes the four ADC7 poses, 15 analog/VMID poses, and 27
timing-mouth poses. `C_ADC_I2C_B` is the single overlap: the timing pose
`(172.8,98.6,0°)` supersedes its ADC7 pose `(172.8,95.0,0°)` by explicit
rule. The result has 45 distinct research moves plus Q_PRE, with no source
region divider or route change. No canonical board/source or stock is changed.

The pinned regenerated baseline (Q_PRE only) is SHA-256
`3c3893e65100d51078e5f915e473585e4f38e3d6d34ef607992dcf6f2fc54cc8`;
the union is SHA-256
`20373950748ac51113b115b2d12d169160c24024a2a000572bb70c67b0f60919`.
`analyze.py` verifies exactly 569 refs, all 27 fixed poses, the exact 46-ref
pose delta against TI, and every pad number, net, layer, shape, drill, and
rotation-normalized local pad position. The full native cross-owner census has
zero envelope, body, or pad interaction pairs on both generated boards. The
union still has **115 outside-owner refs and 139 refs entering a foreign
planning rectangle**. The ADC7 access portal has no native footprint/pad hit.
The three rough timing mouth screens retain connected widths **2.600 mm**
(5 × 0.45-mm slots), **1.400 mm** (3 slots), and **2.995 mm** (6 slots),
respectively. These are aperture screens, not routable capacity or return
evidence.

**Hard stop:** native `kicad-cli pcb drc --format json` gives 699 violations
and 499 unconnected items on each regenerated board. The same
**0.100-mm actual versus 0.200-mm required** GND-via/signal-pad clearance
deficit persists: it is at `U_ISO8.2` (`AUDIO_EN`) and via `(202.7,58.4)` mm
in the baseline, then at `U_ISO8.4` (`ISO8P`) and via `(199.0,53.0)` mm in
the union. This is a changed DRC identity, not the first occurrence of the
defect or an increased violation count. Five `text_height` warning identities
(C_FSYNC_FF1, C_XU_VDD_54, C_XU_VDDIO_17, R_ADC_PD5P, R_IN7P) replace five
old warnings. The persistent native clearance failure rejects the integrated
placement; this study stops without claiming acceptance.

The [receipt](receipt.json) preserves all changed issue descriptions and native
coordinates, 23 moved XU bypass pad-to-owning-pin distances (none worsened),
and ADC/clock related-pad distances. The ADC8 cap's owner/USB margin remains
only **0.005 mm** in the 15-part research placement. The timing native probe's
28 reference-field moves to F.Fab were not encoded by these source placements:
none of those 28 reference fields is on F.Fab after regeneration. The saved
In1.Cu GND zone is unfilled, and there are no timing/analog routes or return
proof. The TI USB ESD pad corner style is roundrect; the current ordinary
netlist produces rect pads, so shape-sensitive promotion needs a current
governed-source rebaseline. USB ESD suitability remains a separate review.

Reproduce from this directory:

```sh
python3 build.py --baseline > /tmp/crow-integrated-baseline-build.log 2>&1
python3 build.py > /tmp/crow-integrated-candidate-build.log 2>&1
python3 analyze.py
```
