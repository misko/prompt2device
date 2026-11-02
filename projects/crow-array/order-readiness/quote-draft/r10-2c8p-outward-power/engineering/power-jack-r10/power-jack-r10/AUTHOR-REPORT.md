# Outward PJ-102AH native candidate — author handoff

SUPERSEDED: candidate3 below is retained engineering history, not the final
handoff. See `AUTHOR-FINAL-CANDIDATE4.md` for the separately authorized mechanical
margin repair, its clean checks and improved continuous cooling geometry.

Frozen candidate: `candidate3/native/pcb/carrier/carrier.kicad_pcb`.
SHA256: `42a51e3b180ccfa1d0aeda85e9131c292ee8e1c32b6db3cb0c3261f22f134a01`.
Source r9 SHA256: `ddc5f5b1c3cba999db77b1e2a0a8dd24f004579ec825ccec991169a0af3aa099`.
This is an engineering candidate, not acceptance, release, fabrication approval,
vendor process approval, or authorization to purchase.

## Manufacturer-based pose

Retained `PJ-102AH-maker-drawing.pdf` is CUI PJ-102AH drawing revision A,
SHA256 `74c35b925c9cbb3ded203afc33684eb76c538b0b99dc80e8500d5da8f1714e45`,
from https://cdn-shop.adafruit.com/datasheets/21mmdcjackDatasheet.pdf.
The maker's primary units are mm; PCB layout is TOP VIEW. Mouth-to-pin3 is10.7,
and pin1 is3.0 farther from the mouth than pin3. The14.4-deep body therefore
occupies localY[-0.7,13.7] with mouth at+13.7 for this native pin mapping.
Body width9.0, height11.0; these are maker nominal dimensions, not generic-model
physical-fit proof. Tolerances in drawing: X.X±0.2mm, X.XX±0.1mm.

J1 rotated180° about unchanged nominal body center(188,8.7):

| Item | r9 native mm | candidate3 native mm |
|---|---|---|
| Anchor / pin1 VIN12 |188,2.2|188,15.2|
| pin2 GND |188,8.2|188,9.2|
| pin3 NC switch |192.7,5.2|183.3,12.2|
| Mouth plane/direction |y15.9 / +Y inward|y1.5 / -Y outward|

Native footprint retains all pad identities, nets, sizes and drills. Existing
1.6mm round-hole substitution for maker1.00×1.60 slots is NOT waived. Retain
vendor mounting/solder/retention/process holds. Independent cable engagement,
clearance, access and enclosure review remain required. No generic local model
is used to prove those claims here.

## Exact changes and affected services

Only J1 changes among142 native footprints. All141 others are raw-node identical,
including the reviewed clock area. All185 vias, layer/stackup setup, graphics,
outline and radiused recesses remain raw-node identical. All1347 common track
items are unchanged; removed8 local VIN/FUSED segments are replaced by11.
Schematic, project, local libraries and all adjacent resources are byte-identical.
`candidate3/native-evidence.json` includes actual before/after pad/net/track data.

All new tracks are0.8mm F.Cu, no new via or reduced-width current bottleneck:

- VIN: (188,15.2)→(182.5,15.2)→(179.5,12.2)→F1.1(179.5,9.455).
- FUSED main: F1.2(179.5,4.545)→(179.5,2.5)→(192.5,2.5)→(194.5,4.5)
  →(194.5,15.1)→D3.2(190,19.6).
- FUSED left cooling reconnection: F1.2→(177.3,6.745)→(177.3,11.2)→(178.5,12.4).
- The existing FUSED cooling polygon's top-right two corners move fromy10 toy5.5;
  all other zone definitions/rules remain unchanged. Same-net tracks connect the
  two filled polygons. Other zone fills are regenerated, not inherited stale.

VIN authored length18.170→12.488mm; FUSED total19.404→44.101mm, the latter includes
the redundant cooling branch, so summing it as one series path is pessimistic.
Native external copper is35µm. Using copperρ20C=.01724Ω·mm²/m,0.393%/K temperature
coefficient,100°C trace sensitivity, and ignoring parallel zone copper gives new
VIN10.11mΩ, FUSED35.69mΩ; at retained680mA total both contribute31.14mV. At1A the
same pessimistic total dissipates45.80mW. No fuse rating or power allocation is
increased. These estimates do not establish IPC ampacity, process tolerances or
device/contact thermal qualification; inherited power/thermal holds remain.

Ground return is not just an opens count: J1.2 retains four45° thermal spokes
into each continuous inner GND polygon. In both old and new geometry, all12
samples at radii1.05,1.6,2.0mm over the four spoke directions are in the respective
single filled polygon on each inner layer. All ground vias and all other ground
pads/escapes are untouched. Each inner plane remains18585.956869mm² and one polygon.
The12V D3 output cooling zone remains232.785124mm², identical geometry.

FUSED thermal spreading required a real repair: first clean-DRC candidate1 cut
the inherited cooling lobe, leaving150.607884mm² vs206.407582mm² original. It is
not promotable. Candidate2 reconnects the lobe but its initial topy7 extension
produced193.387945mm², still insufficient area. Candidate3's topy5.5 extension
produces212.587945mm²: main D3 polygon200.216429mm² plus12.371516mm² lobe connected
by the0.8mm branch. The D3-adjacent rectangle[186,16.9,199,22.5] has71.670840mm²
filled vs71.974517mm² original (0.42% reduction at the upper edge near VIN pad).
No theta equivalence follows from area alone: independent review must judge the
actual spreading shape, the small local loss and remote extension against the
retained D3 power/thermal sensitivities. Two causal cooling repair attempts are
exhausted; further changes require coordinator reassessment.

## Checks and replay

`candidate3/drc.json`: KiCad10.0.4 strict all-severity, all-track, schematic-parity,
refill and save:0 violations,0 unconnected,0 parity,0 ignored checks.
`candidate3/routing-geometry.json`:0 drill/SMD overlaps,0 annulus-gap findings
under the inherited explicit0.15mm allocation. No new design-rule exclusions.

Reproduce from repository root using a new output name:

```sh
/usr/bin/python3 projects/crow-array/order-readiness/power-jack-r10/author_power_jack.py --output reproduce-final --preserve-cooling
/usr/bin/python3 projects/crow-array/order-readiness/power-jack-r10/inspect_power_jack.py reproduce-final
```

`replay3` was generated independently from exact r9 by the deterministic patch
and native CLI refill; its board SHA256 exactly matches candidate3. Replay1
likewise exactly matched candidate1. All source resources are hash-listed in
each patch record. The separate native evidence inspector is read-only.

Early `attempt1*` directories retain failed SWIG authoring diagnostics; some
contain copied or saved boards but are NOT accepted candidates or replay proof.
The final producer avoids those unstable mutation APIs with exact guarded native
text edits and strict CLI checks. No source r9, STATUS, quote package, repository
reference, JLC state or skill was modified by this author.
