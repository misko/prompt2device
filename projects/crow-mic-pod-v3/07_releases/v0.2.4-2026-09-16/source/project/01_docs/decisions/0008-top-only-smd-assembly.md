---
id: 0008
date: 2026-09-13
status: accepted
---
# 0008 — top-only SMD assembly

## Context

The user explicitly requested single-side SMD assembly to simplify assembly and
reduce cost, and authorized a modest board expansion if it helps. The previous
carrier layout has sixteen underside SMD components (F1–F8 and U_ESD1–U_ESD8);
the pod has one (U3). Those generated layouts do not satisfy the new requirement.

## Options

- Retain mixed-side SMD: rejected by the user manufacturing requirement.
- Move every fitted SMD component to the top and expand the board where needed:
  selected. This requires a new connector/protection layout because flipping
  an underside component beneath a jack would collide with its body.

## Decision

All fitted SMD components on both boards shall mount on F.Cu. This includes
machine-placed, consigned and manually fitted SMD components. No manual-fit
exception permits bottom SMD population. Unpopulated copper test pads, vias,
through-hole solder joints and copper routing are not SMD component population.
The factory RJ45 jack, patch cord, pin map and analog/DC interface remain selected.

This decision supersedes the mixed-side manufacturing and placement portions
of prior factory-RJ45 decisions, including carrier ADR0028 and pod ADR0007;
the historical records and their remaining interface decisions are retained.
Assembly policy must declare sides: [top]. Modest board growth is authorized;
its exact dimensions will follow measured body, tool and copper clearances.

## Consequences

Do not flip components in place under the jack. Rework source placement and
source-owned protection paths together, checking real pad, body, tail and rework
clearances. Prior geometry-specific bottom-layer ESD path requirements must be
reconciled explicitly with the new physical layout and primary protection
requirements before adoption. Existing limits remain in force until a justified,
independently reviewed replacement is adopted; changing a limit to pass is not
an acceptable repair. No release gate is waived by this manufacturing decision.

Previous layouts, route trials and reviews remain historical evidence. Regenerate
both boards and renew all affected source, placement, routing, BOM/CPL, twin and
release checks. Changed connector scenes need current orientation review and any
required human approval. The required result is no fitted SMD on B.Cu, verified
from native board bytes and the exported CPL, including manual-fit population.
This records accepted intent; it is not a claim of completed layout or assembly
savings measured by an assembler. FIRST-ARTICLE-ONLY / DO-NOT-ORDER remains.
