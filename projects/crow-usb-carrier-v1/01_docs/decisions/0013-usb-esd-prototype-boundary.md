# D13 — USB ESD prototype boundary

**Decision (2026-09-25):** Retain `TPD2EUSB30ADRTR / C94934` as Crow's
initial-stock-locked USB data ESD candidate under D12. Admit it for a
**schematic-only engineering prototype** with independent review, while
keeping XU316 transient coordination and exact-board ESD qualification open.
No release, fabrication, assembly, order or electrical survival claim follows
from this decision.

The published TI DRT pin map and connector-side placement guidance support a
specific passive candidate topology. The public XU316 TQ128 documentation does
not provide the USB DP/DM powered or rail-off transient/injection limit needed
to show that TI's component clamp protects this silicon on Crow. The
[independent review](../../08_reviews/2026-09-25_ti-usb-esd-prototype-only_terra.md)
therefore accepts bounded prototype design work only. The
[test plan](../research/2026-09-25-ti-usb-esd-prototype-test-plan.md) states
measurements and stops that must be completed by an electrical owner before
any test-article order; it is not a test result.

Move `USB-ESD-selection-transient` from due-at-selection to a named deferred
release finding. Its `state: open` and `blocks_at_or_above: DESIGN_CLEAN`
remain. This is a change in *when evidence can be acquired*, not a waiver or
closure: exact-board stress cannot be observed before the board exists. The
critical-selection manifest binds the independent review and test plan by
SHA-256; the prototype producer requires `PROTOTYPE_ONLY`; ordinary full/reuse
reject it. Release preflight, rehearsal, seal verification, publication,
freshness and manufacturing-order paths recheck selection and open
DESIGN_CLEAN findings independently.

Acceptance for a stated release target requires new public primary electrical
evidence or reviewed exact-board measurements sufficient for that target.
Changing the MPN/LCSC, quantity, pin map, footprint or source hash triggers a
new exact-part selection review. Later public stock changes do not reopen the
unchanged selected part under D12, though JLC allocation is still checked at
order time.
