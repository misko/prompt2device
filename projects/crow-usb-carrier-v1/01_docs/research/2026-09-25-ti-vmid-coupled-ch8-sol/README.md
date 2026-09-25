# Isolated coupled VMID/channel-8 placement screen

Research board only, replayed from the exact four-part candidate SHA-256
`046019a13094764baef313d62611b137e0f0af971079734c71ab050dbf46b3a0`.
Run `python3 probe.py` from this packet directory to reproduce `candidate.kicad_pcb`
and `receipt.json`. The script fails closed on input-hash drift, any of the 27
fixed poses, pad/net/layer/shape/relative-pad change, any unrelated pose change,
moved-envelope owner/foreign-cell failure, a moved pad outside its full physical
envelope, or a moved-envelope gap below 0.15 mm. It uses the native
`_physical_envelope` helper, not silk/text boxes.

The candidate moves eight `R_BnP` resistors and seven local channel-8 parts:

| Ref(s) | New origin (mm) | Reason |
| --- | --- | --- |
| `R_B1P`…`R_B7P` | each original x − 1.6, y = 68.5 | Complete VMID2 pad and envelope containment; nearest body gap 0.56 mm. |
| `R_B8P` | (193.75, 61.0) | Avoid `usb_vbus_sense` while retaining 0.58 mm to `U_SPOKE8` and 0.68 mm to the cap. |
| `C_ADC_AC8N1` | (198.2, 60.25) | Escape the USB foreign cell with 0.56 mm to `C_A8P`. |
| `C_A8P` | (188.45, 57.0) | Open the cap mouth; 0.56 mm to cap, `C_FILTER8N1`, and `C_FILTER8N2`. |
| `C_FILTER8N1`, `C_FILTER8N2` | (197.15, 56.5), (184.75, 54.8) | Relieve the cap and `C_A8P` envelopes. |
| `C_FILTER8P2`, `C_SPOKE_IN8` | (198.5, 48.0), (191.8, 52.6) | Make room for the ISO endpoint and `C_A8P`. |
| `U_ISO8` | (199.0, 53.0) | Put the entire ISO footprint inside `analog_ch8` and clear the cap/filter envelopes. |

All 15 moved full envelopes and pads are inside their analog owner and outside
all foreign source rectangles. All other footprint poses, the 27 fixed refs,
outline, layer stack, rotations, and pad identities are unchanged. The ADC7
access-only portal remains physically empty; its nearest full envelope is
`Y_AUDIO`, 0.255 mm away. The cap's related pad distances become 7.846 mm to
`U_ISO8.6` (9.142 mm before) and 13.958 mm to `C_ADC_CM8N.1` (11.811 mm
before, 1.182×). `R_B1P`…`R_B7P` to their bias capacitors rise from 8.771 to
12.405 mm (1.414×); `R_B8P` to `C_A8P` falls to 4.006 mm. Exact per-part
margins and all measured related pairs are in `receipt.json`.

Native DRC was run without a sidecar project, using the same KiCad defaults for
both boards:

```
kicad-cli pcb drc --format json --output /tmp/crow-vmid-base-drc.json projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-adc7-four-part-margin-sol/candidate.kicad_pcb
kicad-cli pcb drc --format json --output /tmp/crow-vmid-candidate-drc.json projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-vmid-coupled-ch8-sol/candidate.kicad_pcb
```

Baseline: 714 violations, 499 unconnected. Candidate: 730 violations, 499
unconnected. Comparing violation type, description, and item UUIDs shows **no
new native DRC errors**: one clearance error and four hole-clearance errors
at the old `U_ISO8`/GND-via pose disappear. There are 21 new silk warnings
(16 silk-over-copper and five silk-overlap). This is a geometry probe, not
P2/assembly acceptance.

The cap's east owner margin and its south margin to the USB foreign cell are
both only 0.005 mm, despite the measured 0.56 mm gap to `C_A8P`. Several local
support gaps remain below 0.56 mm, including `C_A8P` to `R_OUT8N` at 0.19 mm
and `C_FILTER8N2` to `R_X8N` at 0.26 mm. The existing GND reference zone is
unfilled; the source board has 499 unconnected items. No trace path, via,
continuous return, capacitive loop, or usable timing/analog corridor capacity
has been proved. The next design step would need a physical-cell recut and
route/return access demonstration, especially for the cap's ADC8N pad and the
moved ISO `AUDIO_EN` and supply pads. P1 and P2 remain unaccepted.
