# Independent review: coupled VMID/channel-8 candidate

**Decision: reject this placement for further P2 exploration.** It is useful
as a geometry-screen result, but it does not meet the next gate in the
reject-first plan: a physically credible, exclusive owner cell with actual
pad-access and return evidence.  No canonical file or board was changed by
this review.

## Reproduced subject and invariants

`51fd2a6c` replays from four-part board SHA-256
`046019a13094764baef313d62611b137e0f0af971079734c71ab050dbf46b3a0`, itself
derived from the exact original TI board
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`.
Replaying its `probe.py` reproduced candidate SHA-256
`d0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7`.

The receipt's 15 moved footprints are exactly the eight `R_B1P`...`R_B8P`
plus `C_ADC_AC8N1`, `C_A8P`, `C_FILTER8N1`, `C_FILTER8N2`,
`C_FILTER8P2`, `C_SPOKE_IN8`, and `U_ISO8`.  It retains all 27 fixed poses,
all non-listed poses, outline/stack, rotations, and pad net/layer/shape and
relative-pad identities.  Under the checker's native `_physical_envelope`
and pad test, every moved item is contained in its listed analog owner and
does not intersect a foreign source rectangle.  The ADC7 access portal's
nearest real envelope remains `Y_AUDIO` at 0.255 mm; this candidate provides
no typed ADC7 face or route/return result.

The cap's related-pad distances are 7.846 mm to `U_ISO8.6` (improved from
9.142 mm) and 13.958 mm to `C_ADC_CM8N.1` (worse from 11.811 mm, 1.182x).
The seven moved VMID resistors are each 12.405 mm from their `C_A<n>P.2`
partner (8.771 mm before, 1.414x).  These are measurements only; no source
electrical limit authorizes them.

## Decisive margin failure

At `(198.2,60.25)`, `C_ADC_AC8N1` has native physical envelope
`[195.405,58.505,200.995,61.995]` mm.  It is only **0.005 mm** inside the
`analog_ch8` right boundary (201 mm), and only **0.005 mm** below the
`usb_vbus_sense` y=62 mm boundary.  This satisfies a zero-overlap predicate
only.  The 0.15-mm source rule is a copper rule, so it does not directly set a
region-edge clearance; nevertheless 5 micrometres cannot be credited as a
manufacturable placement tolerance, cell transition, trace entry, or return
corridor.  The 0.56-mm clearance to `C_A8P` does not repair the
owner/foreign-boundary pinch; nearby support gaps
also reach 0.19 mm (`C_A8P`/`R_OUT8N`) and 0.26 mm (`C_FILTER8N2`/`R_X8N`).

The candidate therefore demonstrates that a coordinated 15-footprint move
can eliminate the previous literal body overlaps.  It does **not** demonstrate
that the required channel-8 physical cell can be assigned with usable access.
Treating the 0.005-mm sliver as capacity would violate the no-false-credit
rule in the coupled plan.

## Native check and remaining gate

I reran `kicad-cli pcb drc --format json` on the four-part baseline and the
replayed candidate using the same defaults.  Baseline/candidate violations
are 714/730 and unconnected items are 499/499.  The candidate removes one
clearance and four hole-clearance errors, but introduces 21 silk warnings;
it has no demonstrated route, vias, fill, or return.  The GND reference zone
is still unfilled.

Before P2 can be reconsidered, a new coupled placement must give
`C_ADC_AC8N1` a real owner/foreign separation with documented tolerance and
pad entry, then prove the moved ISO `AUDIO_EN`/supply pads and cap pads can be
routed with a continuous return.  That requires a source-owned physical-cell
recut plus native full-envelope/pad validation; moving source boundaries over
this 0.005-mm sliver is not a corrective test.  P1 and P2 remain unaccepted.
