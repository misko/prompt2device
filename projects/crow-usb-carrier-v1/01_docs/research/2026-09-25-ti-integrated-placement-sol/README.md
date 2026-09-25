# Integrated TI placement union: research-only geometry screen

This is a reproducible **research-only placement**, not a P1 or P2 board. The
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

The original bare-board `kicad-cli pcb drc --format json` screen gives 699
issues and 499 unconnected items on each board. It flags the intentional
0.100-mm B2 via-to-signal-pad gap against 0.200-mm *default* clearance, with
the issue identity moving from `U_ISO8.2` to `U_ISO8.4`. That screen omitted
the project `.kicad_pro`, `.kicad_dru`, and post-generator POFV rule areas.
The [exact TI profile replay](../2026-09-25-ti-iso8-profile-replay-sol/README.md)
applies all three and independently validates all 14 protected vias. Both
boards then have **213 identical native DRC issue identities**, 499 opens,
and no ISO8 clearance error. No via move is needed. The profile replay
supersedes the bare-board clearance interpretation; conditional vendor/CAM/
PCBA acceptance remains open.

The [receipt](receipt.json) preserves the incomplete bare-board issue identities and native
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
