# Independent review: TI USB ESD prototype-only selection boundary

**Verdict: CONDITIONALLY SOUND FOR A BOUNDED ENGINEERING PROTOTYPE; NOT
ELECTRICALLY ACCEPTED FOR RELEASE.**

This review addresses only a source decision that permits bounded prototype
schematic/layout work for `U_USB_ESD = TPD2EUSB30ADRTR / C94934`. It grants no
claim of XU316 protection, USB compliance, system IEC performance, production
manufacturability, P1/P2/P3 acceptance, or order readiness.

## Primary evidence

TI's retained `SLVSAC2G` exact-part data sheet, SHA-256
`a2c0dd845043a5bbfe610f673879c29e38649544385dea51dbe0a4c49df39136`,
establishes the A-suffix DRT device's pin map (1 D+, 2 D-, 3 GND), 0--3.6 V
operating range, 4 V IO absolute maximum, 4.5 V typical breakdown, 8 V
maximum clamp at 1 A, 0.7 pF typical capacitance, 8 kV IEC 61000-4-2 contact
component rating, and 5 A 8/20-us component surge rating. Its layout guidance
requires connector-adjacent, flow-through routing and a low-impedance GND
connection. These facts support an exact, passive two-line USB-data ESD
candidate and a concrete prototype topology.

XMOS's retained XU316-1024-TQ128 v2.0.0 data sheet, SHA-256
`a2ce2dc835df06793a4e1aa6c5d226c6a01c25c979a63b09a2b57059c17321cf`,
identifies USB_DM/USB_DP as TQ128 pins 59/60 and USB_VDD33 as 3.00--3.60 V.
It specifies generic I/O AMR `V(Vin) = -0.5 V .. VDDIO + 0.5 V`, plus
handling HBM/CDM ratings, but does not identify the relevant rail for the
USB-PHY pads or publish powered/off-state DP/DM injection or transient
limits. Its USB section says extra components can be required for EMC/ESD;
its self-powered VBUS circuit protects a *GPIO VBUS-sense path*, not DP/DM.

The public XMOS XK-AUDIO-316-MC platform is a relevant XU316-TQ128 USB
reference platform, but the official design-file download could not be
retrieved in this review (HTTP 406). No ESD MPN, schematic topology, or
measured ESD result from that platform is therefore used as evidence.

Consequently, TI's maximum 1-A clamp value and component IEC rating cannot be
compared to an XMOS DP/DM survival envelope or transferred through Crow's
connector/trace/return inductance. This is an unclosed release question, not
a known contradiction to using the passive TI candidate in a controlled
prototype.

## Required meaning of `prototype_only`

A prototype-only selection must mean all of the following:

1. The exact source identity, DRT pin map, locked initial stock receipt, and
   data-sheet/footprint provenance are accepted **only to generate and inspect
   a prototype subject**.
2. The decision explicitly retains the XU316 powered/off transient and
   exact-board ESD finding as open and release-blocking.
3. It permits neither a release seal nor wording such as “ESD-qualified”,
   “protects XU316”, “system IEC compliant”, “production-ready”, or
   “orderable”.
4. Any fabricated prototype is an engineering test article. Its test plan must
   define allowed discharge setup/level/polarity, powered and rail-off states,
   instrumentation bandwidth and probes, DP/DM, local GND, USB_VDD33 and
   USB_VDD18 measurements at the XU-side pads, return geometry, and
   pre/post-enumeration and leakage checks. Separate authorization remains
   needed before placing a fabrication/assembly order.

## Required fail-closed implementation

The current
`skills/pcb-design/scripts/critical_part_selection_admission.py` accepts
only `suitability.status: accepted|incomplete`; an open
`due_at_selection_findings` entry unconditionally fails. The current Crow
full/reuse conductors invoke that checker before the producer and later
execute ordinary P1/P2/P3-style acceptance steps. Thus prose alone cannot
create a safe prototype exception.

Use a typed `prototype_only` status and an explicit, hash-bound
`deferred_release_findings` list. The checker must:

- require an independent reviewer, exact source/dossier/stock bindings and a
  nonempty test-plan/evidence binding;
- require every deferred ID to exist and remain open with an explicit
  release-blocking classification;
- emit a distinct `PROTOTYPE_ONLY` result rather than `PASS`;
- reject `prototype_only` in ordinary full/reuse/release conductors; and
- allow it only in a separately named bounded prototype producer/layout
  command that cannot write a layout/release seal or a production-order
  verdict.

The release gate must independently reject every subject carrying
`prototype_only` or an open deferred-release finding, regardless of DRC,
route, stock, or review results. This guard does not currently exist:
`release_freshness_check.py` and `release_review_preflight.py` do not consume
Crow's findings ledger or selection status. `project_state.py` does consume the
ledger and, while Crow targets `DESIGN_CLEAN`, its open finding leaves derived
maturity at `DRAFT`; the full conductor invokes it only at its end. That is a
useful maturity stop, but it is not a seal-time prototype guard. Implement the
seal-time reader before a prototype status can replace the current red
selection gate. Changing an MPN/LCSC, quantity, pin map, footprint, or source
hash invalidates this decision and requires a fresh selection review.

## Disposition

The retained facts are sufficient for prototype-only source continuation under
the implementation boundary above. They are insufficient for ordinary
selection acceptance or for closing
`USB-ESD-selection-transient`.
