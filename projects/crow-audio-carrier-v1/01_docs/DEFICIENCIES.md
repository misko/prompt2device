# Crow audio carrier release deficiencies

This list separates work that must close before the immutable design release
from prototype and order-time work that may remain explicit. It is not a gate
waiver. The release scripts, native DRC, electrical contracts, and publication
checks remain authoritative.

## Must close before release

| Item | Exit condition |
| --- | --- |
| Fabrication and publication | Export and inspect the fabrication/BOM/CPL package, pass release rehearsal and publication gates, create the immutable release, then merge, tag, push, and verify the remote commit and tag. |

Closed on 2026-09-16: the authenticated 19-wave replay and layout seal pass at
0 native DRC violations / 0 unconnected / 0 parity findings, and the exact-board
locator plus three RJ45 oblique views passed review with the user's connector
approval retained.

## Explicit prototype and order-time deficiencies

| Deficiency | Disposition |
| --- | --- |
| Exact LT3041ADE#TRPBF allocation | Fresh public evidence shows the selected tape-and-reel identity at stock 0. The design release may seal only as `DO-NOT-ORDER / BLOCKED-SOURCING`; an order requires a fresh exact-identity allocation or a separately reviewed source change. |
| TMUX2821DSGR allocation | Fresh LCSC catalog evidence shows 16 units against 40 required for five carriers. This is also `BLOCKED-SOURCING`; ordering requires sufficient exact stock or a separately reviewed source change. |
| First-article electrical captures | Rail startup, shutdown, reset, TDM timing, analog-path performance, fault behavior, and thermal measurements remain owed by the controlled first-article plan. No production qualification is claimed. |
| Physical copper and barrel validation | Calculated DCR, current, and via-capacity checks pass the design model; physical DCR and temperature-rise measurements remain first-article obligations. |
| Silkscreen locator fallbacks | Crowded references that cannot remain legible on F.SilkS are carried by the assembly locator/F.Fab evidence. This affects assembly convenience, not connectivity or fabrication geometry. |
| Fabricator upload checks | Gerber interpretation, BOM/CPL matching, stock allocation, substitutions, and panel/order options must be reconfirmed in the fabricator uploader before purchase. |

The initial five-board build remains a prototype lot. Closing these items may
change orderability or qualification status; it does not permit silently
changing the released schematic, PCB, BOM identity, or fabrication outputs.
