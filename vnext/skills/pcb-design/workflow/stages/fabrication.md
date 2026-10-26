# JLC-FABRICATION — complete manufacturer package

Local integration pilot with explicit adoption and independent admission through
[staging tooling](../../procedures/fabrication/tooling.md). Requires current
`layout_sealed` for all board types and phase resume. Preserve graph identity and
dependencies. A component export or synthetic fixture is not stage acceptance.

Produce a fresh, source-derived package for every board: exact layer/drill zip,
separate assembly BOM/CPL, retained standalone native libraries/settings,
schematic and PCB/assembly PDFs, mechanical views, process selections, assembly
instructions and measured sourcing evidence. Copy, never symlink. Include the
whole system's board quantities and any manual/consigned/DNP population.

The native component `tools/fab_payload.py --project ABS --output NEW_REL` reruns
layout acceptance, exports from isolated copies, checks the layer/drill census
and packages plots atomically. It deliberately reports DO-NOT-ORDER and cannot
issue any stage receipt. It does not yet implement assembly or release staging.

The [population component](../../procedures/fabrication/population.md) derives
per-reference population, whole-system demand and native positions from accepted
inputs, and optionally translates an explicit source-bound identity/centroid/
rotation mapping into separate factory/consigned BOM/CPL files. Native positions
are not CPL; supplied geometry mapping is not an independent assembly verdict.
It also cannot issue stage acceptance.

The [native replay component](../../procedures/fabrication/native-replay.md)
copies PCB sources/libraries/settings and the supported flat schematic's
declared authoring source. It validates relocated circuit/native replay,
schematic-to-PCB identity, plots/DRC and schematic/PCB PDFs. This is not 3D
portability, complete staging, or release acceptance.

The joined `tools/fabrication.py` adapter integrates source-exact per-reference
BOM/CPL generation, quantity-aware supplied stock observations, retained process/
assembly/mechanical evidence and standalone replay. Its `issue` and `check`
operations require independent exact-subject review; `build` and `replay` alone
never accept a stage. Positive/corrupt isolated tests validate implementation,
not the truth of stock observations or any live project's upstream engineering.
Preserve exact MPN/code/value/package identity and distinguish vendor placement
rotation/datum from KiCad's footprint anchor. Never infer vendor rotation merely
from a plausible render. Failures return to their source owner.

Design soundness, catalog availability and order allocation are separate claims.
Missing actual uploader selections must remain a named order hold, not a made-up
process guarantee. A stack assumption needed for electrical design must already
have a sound engineering basis; order paperwork cannot excuse missing design
proof. No upload, vendor contact or purchase follows from local export authority.

Next owner: [assembly verification](assembly-verify.md). Stop on unsupported
geometry or missing assembly evidence, not with a fabricated staging receipt.
Stop for phase reflection after staging acceptance. Export/policy failures return
here; sourcing substitutions reopen sourcing and affected circuit consumers;
native document defects return to layout; copper/stack or circuit contradictions
backtrack to routing or schematic under the existing orchestrator recovery rules.
