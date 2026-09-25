# Source-controlled AUDIO_EN owner repair trial

**Rejected local trial; no P1/P2 credit.** The trial starts from unified packet
`9f8ca953` and its exact 15-part board SHA-256
`d0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7`.
That board was already rejected for P2 because the ADC8 cap has only 0.005 mm
owner/USB margins. This probe tests only the separate AUDIO_EN owner defect.

`generator_overlay.yaml` applies the previous four ADC7 and 15 channel-8
poses plus these three source `post_anchors` from `6fead4cc`:

| Ref | Prior origin (mm) | Trial origin (mm) |
| --- | --- | --- |
| `R_AUDIO_PD` | (22.7, 105.1, 90°) | (28.5, 106.3, 90°) |
| `U_AUDIO` | (22.7, 109.6, 0°) | (26.6, 114.0, 0°) |
| `U_ISO1` | (23.3, 67.6, 0°) | (27.2, 74.6, 0°) |

`regenerate.py` uses the frozen TI netlist, parts, library, assembly profile,
and source floorplan in a temporary project. Regenerating the 19-anchor
baseline gives all **569 footprint poses** and pad/net/layer/shape identities
identical to the exact 15-part board. The three-anchor trial changes only
those three poses; all 27 P1-fixed refs are unchanged. The generated trial
board SHA-256 is `f1f491c22b20c853fc9d208265237364cbcec3992e4818759281eaa32fc69eac`.
The generator's native P-COLLIDE pass reports zero inter-footprint pad shorts
and zero fixed-courtyard overlaps. `analyze.py` independently measures full
envelopes, pads, source regions, related distances, and native DRC.

All three AUDIO_EN pads and their full bodies now fit their declared source
owners. The proposed poses still fail exclusive physical ownership:
`R_AUDIO_PD`'s body enters `input_buck`, and `U_AUDIO`'s body enters
`hold_bank_left`; `U_ISO1` has no foreign-cell overlap. Their nearest native
envelope gaps are 0.260, 0.375, and 0.280 mm respectively. The already
declared `R_AUDIO_PU.2`/`input_buck` pad blocker also remains.

The local electrical distances reject the trial independently. `U_AUDIO.4`
to its same-net `C_AUDIO.1` bypass grows **1.400→5.078 mm** (3.63×).
`U_AUDIO.5` to timing capacitors `C_AUDIO_CT1.1` and `C_AUDIO_CT2.1` grows
2.853→8.685 mm (3.04×) and 2.304→4.998 mm (2.17×). `U_ISO1.8` to its
same-net `C_ISO1.1` improves 11.313→7.401 mm; its filter endpoints remain
roughly 20–22 mm away. These are measured pad-center distances, not
electrical acceptance limits; moving `U_AUDIO` without its local supports
abandons the compact decoupling/timing neighborhood.

Native KiCad DRC on both source-regenerated boards, with identical default
settings and no zone refill, reports **699 violations and 499 unconnected** on
each. Item-UUID comparison changes two 0.100-mm copper-clearance findings:
the trial flags `U_ISO1.2` AUDIO_EN against its GND via and `U_ISO5.4`
against its GND via, while the baseline flags `U_ISO1.6` and `U_ISO5.2`.
Thus the aggregate error count is unchanged, but the moved AUDIO_EN endpoint
still has an explicit native clearance error. Five text-height warning
identities also exchange after source silk regeneration. Generator silk-owner
warnings fall from 279 to 277; `C_HOLD2` and `R_ADC_BOT` are new degraded
reference owners, while four prior degraded refs disappear. Silk movement
does not repair body or pad ownership.

The unified checker rebuild changes `AUDIO_EN` from an owner-containment
failure to a valid **geometry-free, 11-terminal unresolved branch**. There
are now ten timing branch records instead of nine, but the four exact
two-terminal TDM/XU paths still have no witness. The full result remains
`FAIL`, `routing_realized=false`, `p1_accepted=false`, with ten derivative
denominator errors and nine independent power diagnostics. The new branch
has null capacity and retains P2 pad-to-tree, P3 connected-net, and filled
In1.Cu return obligations. The GND zone is unfilled.

Reproduce with `python3 regenerate.py --baseline > /tmp/audio-base.log`,
`python3 regenerate.py > /tmp/audio-trial.log`,
`python3 silk_summary.py /tmp/audio-base.log /tmp/audio-trial.log`,
`python3 analyze.py > receipt.json`, and `python3 rebuild_unified.py` from
this directory. `source_floorplan.yaml` is the unified checker view with the
same 22 post-anchors; its source-region and pattern updates do not alter the
frozen TI generator input. The accepted branch category is an accounting
improvement only. The foreign-cell crossings, local support distances, and
native clearance finding reject the placement.
