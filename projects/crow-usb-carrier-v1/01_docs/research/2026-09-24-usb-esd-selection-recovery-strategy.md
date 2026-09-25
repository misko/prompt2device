# Crow release recovery at USB ESD selection

**Updated 2026-09-25 for D12.** Crow uses the original TI
`TPD2EUSB30ADRTR / C94934` candidate and its pinned initial public-stock
receipt. The later 5UX investigation is historical; it is not current source.

## Current stop

The full and reuse conductors both stop at `CRITICAL-SELECTION` before a
schematic producer. The exact TI source identity, dossier and locked initial
stock pass; `suitability: incomplete` and the open
`USB-ESD-selection-transient` finding fail. This is the earliest live release
boundary. The existing generated circuit and native schematic are diagnostic
and do not renew the accepted schematic/PDF checkpoint.

The independent [TI/XU316 prototype review](../../08_reviews/2026-09-25_ti-usb-esd-prototype-only_terra.md)
finds no published XU316 USB DP/DM transient limit for powered and rail-off
states. TI's component clamp and IEC rating cannot establish voltage at the
XU pads on Crow. The initial stock pass is locked by
[D12](../decisions/0012-initial-public-stock-lock.md); subsequent stock changes
do not reopen this selected part. Repeating part search or layout attempts
without a new electrical limit or test evidence will not close the finding.

## Bounded recovery

1. Keep the exact TI identity and initial-stock receipt pinned. A new MPN,
   LCSC code, quantity, footprint, pin map or source hash starts a fresh
   selection review; unchanged stock alone does not.
2. Add a typed, independently reviewed **prototype-only** source decision and
   a separate bounded producer path. This may generate a fresh schematic and
   candidate layout for an engineering test article, while the XU316 transient
   finding stays open. The ordinary full/reuse pipeline and every release
   preflight, rehearsal and publication gate must reject this state. Verify
   the rejection with negative integration tests before enabling the path.
3. Before any prototype fabrication, approve an exact-board test plan covering
   discharge level and polarity, powered and rail-off states, XU-side DP/DM
   and USB supply observations, return geometry, and pre/post functional and
   leakage checks. Fabrication or ordering is a separate decision. A passing
   test supports only its measured board and conditions, and cannot by itself
   invent a published silicon stress limit.
4. Use new public primary electrical evidence or reviewed exact-board test
   results to decide whether the TI candidate can be accepted for a stated
   release target. Close the finding only with a hash-bound independent review;
   otherwise revise the protection design and repeat its selection checkpoint.

After the prototype lane is guarded, the shortest design path is fresh
E-FAULT/IC applicability, then one coherent 569-part circuit/netlist/PDF
checkpoint with independent topology and render reviews; rebind route
authority to the exact TI part; then P1/P2 source-cell and connector FULL
proof, P3 native routing/return/SI. Electrical qualification and the ordinary
assembly/release checks still have to close before a release claim. Historical
5UX reviews and scratch boards do not transfer to TI.

## Work limit while held

Do not launch the ordinary full/reuse schematic, placement or route conductor
while selection remains red. A separately guarded prototype producer may run
after its release guard and negative tests exist; its output cannot claim P1,
P2, P3, release, or order readiness.
