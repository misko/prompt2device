# Crow carrier board views

Native oblique views show the two opposing rows of RJ45 connectors. Front-left
and front-right expose the south row; rear-left exposes the north row. These
connectors carry the Crow analog/power interface.

The current image set and its exact producer are recorded in manifest.json.
These final routed-board views establish visual connector evidence only; fabrication and release acceptance remain governed by their own gates.

## Reproduce

Run each command in manifest.json `views[].reproduce_command` from the repository root,
using the recorded KiCad version and model bytes. The commands include the
model-directory substitutions actually used. On another machine, map those
paths to byte-identical model files first; retain their SHA-256 identities.

All views use native KiCad perspective rendering at 2400 by 1600 pixels, high
quality, opaque background and floor. Board rotations are 315,0,325 for
front-left, 315,0,35 for front-right and 315,0,145 for rear-left, with zoom 0.85.
The camera leaves margin around the full board and its connectors.

Compare the board, model and tool hashes before replay; compare image hashes
afterward. Rendering may vary across graphics environments. Different pixels
require a new manifest and visual inspection, not a copied acceptance claim.

## Current final-board views

**Layout is sealed; fabrication and release acceptance are pending.** Exact current board SHA-256:
`0776f364424282a7924266450f899ce69bf28cf95a602ca74d92b86fd91c164d`.

[Front-left](front-left.png) · [Front-right](front-right.png) · [Rear-left](rear-left.png)

## Required connector orientation review

The gate passes 9/9 connector geometry checks. Human orientation review is approved for
subject `a278a3bd182ee10ae8dad309e70ac5719a849b7774641e26befbc5bf7746a55b`.
Review the visible mouths, mounting side, keying and cable approach.
The north RJ45 row is J1–J4; the south row is J5–J8; J9 is the west power inlet.
Rear RJ45 shell lower sections are partly obscured by coupling capacitors.
The full-scene rear and oblique views retain these real obstructions.

| Connector group | Top | Cable side | Inside/rear | Additional profiles |
|---|---|---|---|---|
| North RJ45 row, J1–J4 | [Top](../../06_build/pre_route/orientation/views/J1_top.png) | [Outside](../../06_build/pre_route/orientation/views/J1_outside.png) | [Inside](../../06_build/pre_route/orientation/views/J1_inside.png) |  —  |
| South RJ45 row, J5–J8 | [Top](../../06_build/pre_route/orientation/views/J5_top.png) | [Outside](../../06_build/pre_route/orientation/views/J5_outside.png) | [Inside](../../06_build/pre_route/orientation/views/J5_inside.png) |  —  |
| Power inlet, J9 | [Top](../../06_build/pre_route/orientation/views/J9_top.png) | [Outside](../../06_build/pre_route/orientation/views/J9_outside.png) | [Inside](../../06_build/pre_route/orientation/views/J9_inside.png) | [A](../../06_build/pre_route/orientation/views/J9_profile_a.png), [B](../../06_build/pre_route/orientation/views/J9_profile_b.png) |

The review images under 06_build are the current gate-produced bundle; they
are not substitutes for the tracked obliques or immutable release evidence.
