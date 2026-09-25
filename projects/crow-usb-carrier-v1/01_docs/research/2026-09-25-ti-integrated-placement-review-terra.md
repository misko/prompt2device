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

## Correction: full-profile replay supersedes the ISO8 rejection

The preceding clearance interpretation used a bare-board DRC harness and is
withdrawn.  The governed `TMUX4827_YBH_B2_POFV` authority in
`assembly.yaml` binds the exact eight U_ISO pad-5 GND vias to Type-VII
filled-and-capped POFV: 0.35 mm copper, 0.20 mm drill, 0.075 mm annulus, and
a deliberately scoped 0.100 mm via-to-pads 2/4/6/8 clearance.  Its native
DRU rule also requires the named, pad-bound POFV area; the isolated boards
used above contained neither those generated areas nor the matching project
and DRU files.

I independently reran
`2026-09-25-ti-iso8-profile-replay-sol/replay.py`.  It applies the producer,
then the independent process census: both SHA-pinned boards have all eight
areas, the expected eight 0.350/0.200 filled+capped B2 vias and six
0.500/0.200 LDO vias, 213 DRC issues, 499 opens, no ISO8 clearance issue,
and an exact zero added/removed DRC-identity delta.  The candidate U_ISO8.5
via is correctly centred at `(199.0,53.0)` mm.  This removes the alleged ISO8
native DRC blocker; it does not grant P1/P2, route, return, or vendor/CAM/PCBA
acceptance.

I also reviewed the TI pad-authority trace `f9d05e6d`.  Its fresh governed
native TI witness and frozen board agree on TI identity, 0.30 mm pad extents,
centres, and KiCad roundrect ratio 0.25.  The TSX `rect` declaration is not
the final KiCad copper-shape authority.  Since the TI drawing supplies no
corner-radius requirement and the fresh native witness matches the frozen
board, this does not reopen D13.  Shape-sensitive future work must retain the
hash-bound fresh TI native rebaseline rather than use the stale Nexperia
ordinary netlist.
