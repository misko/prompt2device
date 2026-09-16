# Crow audio carrier release deficiencies

This list separates work that must close before the immutable design release
from prototype and order-time work that may remain explicit. It is not a gate
waiver. The release scripts, native DRC, electrical contracts, and publication
checks remain authoritative.

## Must close before release

None. The design-side release gates are closed.

Closed on 2026-09-16: the authenticated 19-wave replay and layout seal pass at
0 native DRC violations / 0 unconnected / 0 parity findings, and the exact-board
locator plus three RJ45 oblique views passed review with the user's connector
approval retained.
Fabrication export, release rehearsal, and publication admission passed for the
unchanged board; `v0.1.6-2026-09-16` is the current immutable first-article order release.

## Explicit prototype and order-time deficiencies

| Deficiency | Disposition |
| --- | --- |
| Exact-part allocation | RESOLVED for design-time public availability: current authorized-channel evidence reports 1,965 exact LT3041ADE#TRPBF and DigiKey reports 2,449 exact TMUX2821DSGR, clearing the configured 155 and 190 thresholds. JLC uploader fulfillment remains a manual order-time check. D9 authorizes the five-board first-article purchase after that check; production remains unqualified. |
| First-article electrical captures | Rail startup, shutdown, reset, TDM timing, analog-path performance, fault behavior, and thermal measurements remain owed by the controlled first-article plan. No production qualification is claimed. |
| Physical copper and barrel validation | Calculated DCR, current, and via-capacity checks pass the design model; physical DCR and temperature-rise measurements remain first-article obligations. |
| Silkscreen locator fallbacks | Crowded references that cannot remain legible on F.SilkS are carried by the assembly locator/F.Fab evidence. This affects assembly convenience, not connectivity or fabrication geometry. |
| Fabricator upload checks | Exact selections are frozen by ADR0032. Gerber interpretation, BOM/CPL matching, stock allocation, substitutions, rotations and the twelve-site selective via process must still be confirmed in the fabricator uploader before payment. |

The initial five-board build remains a prototype lot. Closing these items may
change orderability or qualification status; it does not permit silently
changing the released schematic, PCB, BOM identity, or fabrication outputs.
