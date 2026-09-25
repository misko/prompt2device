# Independent review: integrated TI placement union — 2026-09-25

This is a read-only review of the research packet
`2026-09-25-ti-integrated-placement-sol`, not a P1/P2 or routing disposition.
I reran its hash-bound `analyze.py`.  The packet reproduces the frozen TI
input `8e620def…d5eca10`, regenerated baseline
`3c3893e6…2fc54cc8`, and candidate `20373950…0f60919`.  It preserves 569
references, all 27 fixed poses, and all pad/net/layer/relative-pad identities.
The candidate has the claimed 45 research moves plus `Q_PRE`; its census has
no cross-owner full-envelope, body, or pad pairs.  It remains a research-only
geometry screen with an unfilled In1 zone and no route or return credit.

The DRC comparison needs a narrower statement than the packet's “new native
DRC” wording.  Both boards have 699 violations and 499 unconnected items.
The candidate replaces one identity-bearing 0.100-mm clearance item with
another:

| Board | 0.100 mm GND-via item |
| --- | --- |
| baseline | `U_ISO8.2` (`AUDIO_EN`) to GND via at `(202.7,58.4)` mm |
| candidate | `U_ISO8.4` (`ISO8P`) to GND via at `(199.0,53.0)` mm |

Both are 0.100 mm actual against the 0.200 mm board rule.  Thus it is a
changed-net DRC identity, not an increase in violation count or the first
instance of this via/pad geometry.  The candidate is still rejected as a
placement candidate because it retains a native clearance failure, but it
would be misleading to describe this as a newly created 0.100-mm clearance
defect without that qualification.  Five source-generated `text_height`
warnings also change identities: `C_FSYNC_FF1`, `C_XU_VDD_54`,
`C_XU_VDDIO_17`, `R_ADC_PD5P`, and `R_IN7P` replace five existing warnings;
they do not change the 699 total.

There is no safe local placement-only correction.  In each board the 0.35-mm
GND via is co-located with `U_ISO8.5` (0.35 mm square); its adjacent 0.25-mm
signal pad is 0.400 mm center-to-center, leaving 0.100 mm copper clearance.
Moving `U_ISO8` translates the via and preserves the deficit; rotating merely
moves the failure to a different adjacent signal pad.  Moving the via alone
breaks its direct pad-5 return unless a new route/return design is added.
Changing the via diameter, pad geometry, or the explicit rule exemption is a
source-policy/footprint action requiring a separate native and manufacturing
review.  It is not justified by the ownership/proximity improvements here.

The timing-mouth and ADC portal apertures do not alter this conclusion.  The
candidate's 2.600 mm, 1.400 mm, and 2.995 mm mouths are rough aperture results
only; the 0.005 mm ADC8 owner/USB margin, unfilled return, reference-field
debt, and the TI USB-ESD shape rebaseline remain open.
