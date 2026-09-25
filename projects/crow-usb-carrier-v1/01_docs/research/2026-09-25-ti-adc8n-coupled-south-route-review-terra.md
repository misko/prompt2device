# Independent review — coupled ADC8N south route

**Subject:** SOL packet `d6879321`,
`2026-09-25-ti-adc8n-coupled-south-route-sol`.

## Reproduced evidence

The receipt's frozen-source, netlist, integrated-pose, and governed-generator
hashes match the pinned inputs.  Direct inspection of the saved full-profile
board confirms 569 footprints, unchanged pad number/net/layer/shape/size
identities against both the southwest-cap baseline and frozen TI board, and
complete parity for all 27 `p1_fixed_refs`.

There are exactly three pose deltas from the southwest-cap baseline:

| Reference | Baseline pose (mm) | Candidate pose (mm) |
| --- | --- | --- |
| `C_ADC_AC8N1` | (198.00, 60.05) | (198.00, 59.65) |
| `U_SPOKE8` | (190.00, 63.00) | (189.60, 63.00) |
| `R_B8P` | (193.75, 61.00) | (193.75, 60.80) |

All three native body/courtyard envelopes remain within `analog_ch8`, and the
packet's full-envelope collision screen reports none.  The eight-segment,
0.20-mm F.Cu `C_ADC_AC8N1.2`→`C_ADC_CM8N.1` link is **15.977464 mm**.
Excluding its named launch/receiver, it clears full envelopes by at least
**0.205001 mm** (`C_A8N`); `U_SPOKE8` and `R_B8P` clear by 0.260626 and
0.285001 mm.  The post-launch cap and `usb_vbus_sense`-rectangle margins are
0.205001 and **0.200001 mm**, respectively.  The latter and the C_A8N margin
only exceed the stated 0.20-mm research screen by 1 and 5 micrometres.

The receipt's source-region screen reports every foreign rectangle at least
0.20 mm away, with `usb_vbus_sense` limiting at 0.200001 mm.  This is a
rectangle separation result; it does not create an exclusive physical cell or
settle the pre-existing channel-8/J8 ownership model.

I independently replayed the archived full profile in a temporary directory:
archived project/rules, generated POFV areas, via-process check, zone refill,
and native DRC.  Baseline and candidate both return **199 violations and 499
unconnected items**, with **+0/-0** violation identities and no via-process
failures.  The candidate contains one filled In1.Cu GND zone (nine outlines).
The receipt's return screen puts both GND stitches and the signal ribbon in
filled outline 8, with zero uncovered area for all eight 0.20-mm segments.
Native connectivity proves only the two named ADC8N pads; other ADC8N
terminals remain unresolved.

## Locality and disposition

The coupled geometry does not move U_SPOKE8's support group.  Its resulting
pad-center separations remain: input 9.766/11.534 mm, output 12.412/9.992 mm,
ILIM 10.801/11.291 mm, dVdT 10.848/8.166 mm, and UVLO 11.065 mm (the two
numbers in each pair are the asserted support contacts where applicable).
Moving U_SPOKE8 by 0.40 mm improves some distances by at most 0.244 mm and
worsens others by up to 0.158 mm; it does not establish a local input/output,
control, or return support group.

Therefore this is a useful **research-only geometry and filled-return
witness**, not a viable source-placement promotion.  Its 0.20-mm non-launch
screen is passed but has negligible reserve at the USB/C_A8N pinch, and the
unmoved U_SPOKE8 support group independently fails the claimed whole-group
locality objective.  It also leaves the J8 physical-cell obstruction, ADC8
owner/endpoint model, remaining ADC8N branches, and return/thermal review
open.  No P1 or P2 acceptance is implied.
