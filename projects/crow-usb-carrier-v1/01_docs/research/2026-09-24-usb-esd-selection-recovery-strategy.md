# Crow release recovery at USB ESD selection

**Historical 5UX branch, superseded for stock selection by D12.** Crow has
returned to the original TI part using its initial public-stock lock. The
TI/XU transient question remains an independent open electrical finding; this
note does not designate 5UX as current source.

## Current stop

The full and reuse conductors both stop at `CRITICAL-SELECTION` before a
schematic producer. The exact 5UX source identity, dossier and observed public
stock pass; `suitability: incomplete` and the open
`USB-ESD-selection-transient` finding fail. This is the earliest live release
boundary. The existing generated circuit and native schematic are diagnostic
and do not renew the accepted schematic/PDF checkpoint.

The independent [5UX/XU316 transient screen](2026-09-24-pesd2usb5ux-xu316-transient-hold-terra.md)
finds no published XU316 USB DP/DM transient limit for powered and rail-off
states. Nexperia's typical component clamp and IEC rating cannot establish
voltage at the XU pads on Crow. Repeating part search or layout attempts
without a new limit or test evidence will not close this finding.

## Bounded recovery

1. Search only public XMOS primary design files, schematic/manual revisions and
   application guidance for the exact XU316 USB interface and an explicitly
   recommended protection topology or powered/rail-off stress envelope. Record
   exact document revision and page/figure. Stop this search when those
   sources are exhausted; a similar board's part is precedent, not an exact
   Crow qualification. The [XMOS multichannel hardware manual](https://www.xmos.com/documentation/XM-014727-PC/html/doc/rst/index.html)
   lists eight public reference schematics, but direct retrieval returned
   HTTP 406 here, so their component identities have not been verified.
2. If no public limit exists, retain 5UX as provisional and prepare an
   **engineering prototype**, separate from a release. Its test plan must
   specify connector contact-discharge level and polarity, powered and
   VBUS/rail-off states, XU-side DP/DM and USB supply measurements, ground
   return geometry, pre/post USB enumeration and leakage checks, and pass/fail
   authority. Fabrication or ordering remains a separate decision. A passing
   prototype supports a bounded empirical claim; it does not turn a typical
   clamp graph into a guaranteed silicon limit.
3. Reopen selection only on new evidence. Independently review an exact-part
   decision, close the tagged finding with a hash-bound record, refresh the
   public stock receipt against Crow's five-board plus-150 policy, then allow
   the conductor to advance. If the evidence rejects 5UX, replace only the
   source candidate and repeat this same selection checkpoint.

After selection, the shortest release path is fresh E-FAULT/IC applicability,
then one coherent 569-part circuit/netlist/PDF checkpoint with independent
topology and render reviews; rebind route authority to that exact part; then
P1/P2 source-cell and connector FULL proof, P3 native routing/return/SI, and
the ordinary assembly and release checks. Historical UV reviews and scratch
boards do not transfer to 5UX.

## Work limit while held

Do not launch another full schematic, placement or route attempt while this
selection gate is red. Read-only public reference research and prototype test
planning are useful; neither spends a P1/P2/P3 attempt or claims release.
