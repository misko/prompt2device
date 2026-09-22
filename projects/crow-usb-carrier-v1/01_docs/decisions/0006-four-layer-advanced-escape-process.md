---
id: 0006
date: 2026-09-22
status: accepted
---
# 0006 — Four-layer advanced escape process

## Context

The selected 85-part source inventory has thirteen packages whose dossiers require
`jlc_4layer_advanced` while the board declares `jlc_4layer_standard`: LT3045EDD#PBF,
TPS389018DSER, TPS389001DSER, TMUX2821DSGR, CS5308P-DNR,
XU316-1024-TQ128-C24, SN74AXC4T245PWR, TPS389030DSER, TPS26625DRCR,
TPS6282518DMQR, TPS6282533DMQR, TPS62825DMQR and TPSM63603V5RDHR. This is a source
admission result, not a routed-board impossibility proof.

The adopted LT3045 land is replaced by an owned no-hole footprint matching
the ADI/TSX copper geometry. Six source-owned 0.50/0.20 mm board vias are
generated inside EP11 with native fill/cap intent. Ordering that candidate
requires a selective via-in-pad process decision.
Other selected packages may launch outward on the surface, but
standard-tier completion would require package-specific placement corridors or
local-only routing that has not been demonstrated on a placed board. The
CS5308P land pattern has twelve 0.40 mm-pitch, 0.20 mm-wide perimeter lands per
side and a 4.6 mm EP; its dossier now records `escapes_worst_side: 12`, corrected from 10 in
commit d8389ee0. Neither that correction nor
the checker establishes that standard routing is physically impossible.

The board's nominal 1.63 mm JLC04161H-7628G stack and its locked 0.410/0.150 mm
USB geometry remain suitable for four-layer advanced fabrication. A 0.15 mm
through drill would have a 10.87:1 nominal aspect ratio and exceed the declared
10:1 ceiling. A 0.20 mm mechanical drill is 8.15:1 and clears it.

## Options

- **Retain four-layer standard.** Keep the repaired no-hole LT3045 land and move thermal vias outside the paste-covered EP, prove the regulator's thermal result again, add and verify escape
  corridors for dense packages, and demonstrate every small-DFN route condition
  on the placed board. This remains physically plausible for several packages,
  but it is not supported by current placement or thermal evidence.
- **Use the same four-layer stack with advanced track/space and a 0.20 mm
  mechanical-drill family.** Preserve the USB stack and geometry, reserve the
  0.20 mm family for filled/capped LT3045 EP vias, and use 0.30 mm ordinary vias
  unless realized escape forces additional paid 0.20 mm sites. This closes the
  declared tier mismatch with the least architecture change.
- **Move to six layers.** The standard six-layer tier keeps the same 0.30 mm
  drill and 0.50 mm hole-gap limits, so layer count alone does not close these
  escape findings. The small-via six-layer tier adds cost and a new stack/USB
  solve without present evidence that two more layers are needed.

## Decision

Select `jlc_4layer_advanced` on the unchanged JLC04161H-7628G four-layer stack,
use the KRT `advanced` preset with explicit 0.50/0.20 mm via overrides, and
record Type VII fill/cap for the complete 0.20 mm drill family as the proposed
uploader/order requirement, pending exact vendor acceptance evidence. Keep ordinary
routing and stitching on the 0.30 mm drill family where possible. Remove the
legacy collision-unchecked via-normalization pass; source and route settings
own the explicit two via families, with final geometry/process checks rejecting
unexpected geometry rather than silently enlarging copper.

## Consequences

This supersedes the process posture of ADR 0005, now marked
`superseded-by-0006`. It does not authorize an order. No cost
ceiling or vendor quote exists, so the paid small-drill and fill/cap options must
be priced and confirmed in the uploader before payment.

The USB pair retains the existing four-layer stack, 0.410 mm width, 0.150 mm gap,
continuous In1 reference and 90 ohm acceptance contract. Changing the actual
stack at quotation time requires a new impedance solve.

The final board must census every 0.20 mm hole, prove that every such site is in
the filled/capped order family, pass the 10:1 realized-via aspect check, and
prove package escape, connectivity, DRC, thermal performance and assembly. The
candidate 0.50/0.20 geometry is an admissible process choice, not a claim that
the current source is routed. The corrected CS5308P escape budget remains a
source screen; placed escape and routed geometry must still be verified.

The retained source does not establish that JLC has accepted this exact
selective process. “Type VII” is proposed engineering and order intent; uploader
confirmation and retained vendor acceptance evidence are required before payment.
