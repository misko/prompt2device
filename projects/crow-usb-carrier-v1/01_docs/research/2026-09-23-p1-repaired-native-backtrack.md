# Crow repaired native P1: measured result and upstream backtrack

The repaired native candidate eliminates the first trial's 32 shorts, but is
**REJECTED for placement**. No P2 block placement, P3 local routing, global
routing, release or ordering is admitted. This is cumulative P1 attempt 2 of 2;
changing the Circuit JSON, worker or task name does not reset that allowance.

## Exact subject and delivery

- Circuit JSON: `cf78dcb8d8c1fc7f696d6f5eaad20a0175c6b27ae0c193d6e1b67bb8937e9193`.
- Native candidate: `37b455203fcdae0c20880a94b17a4bcfb61103fa2b8b9df9ecf095c9c97aa519`.
- Candidate floorplan: `084063400a90dcaef9629ba8a98c3839d9ded6dbcb2431f551c2862fe5bc2bcd`.
- Generator: `e3ff4ad8bee88a926759f6f8db6ed4c40c854f7a80c33a784c31126dc0296fe3`.
- Closed task: `06_build/task_runs/crow-p1-repaired-trial-20260923-ccdbad9073ae40cca7dbd930b6cc26b3/attempt.json`.
- Evidence: `06_build/modular/repaired-trial/`; the immutable delivery also
  contains the board and producer report. Open native artifacts in their original
  `04_kicad` project layout for correct relative model resolution.

MEASURED: coordinator validated the exact subject, result schema, declared
output census, artifact hashes and host completion before runtime closure.
Runtime PASS establishes delivery only. Root reopened modular observations:
568/568 components and 59/59 crossing nets pass; WORK_RECORDED is not acceptance.
The authoritative floorplan and canonical board have not been replaced by this
rejected candidate. Generated evidence remains in the disposable build area;
this committed record retains identities and conclusions.

## Measurements

MEASURED by the producer under generated project rules and independently
recounted from the native DRC JSON by root:

| Predicate | Result |
|---|---|
| Different-net shorts | 0, previously 32 |
| Native violations | 155: 63 clearance, 36 hole clearance, 8 via diameter, 8 annular width, 40 silk |
| Schematic parity | 45 findings: 37 net conflicts, 8 field mismatches |
| Unrouted connections | 499; board is intentionally still unrouted |
| Component census | 568/568 |
| Declared multi-pin identity | 79 refs / 793 identities pass |
| Model coverage | 495/568, fails |
| Missing same-side courtyards | 16 assembled footprints |
| Placement routability | 5/8 checks passing or not applicable; rejected |

MEASURED: root separately reopened the saved PCB using native pcbnew. U_LDO is
at (132.5, 118.2) mm. All six GND vias now have exactly the authored offsets
X +/-0.575 mm and Y -0.94/0/+0.94 mm from that owner, with 0.50 mm diameter.
There are no U_LDO native DRC violation rows. This resolves the demonstrated
emission-order displacement; it does not prove thermal performance.

MEASURED by the producer: all 16 hold cans remain within the two assigned
islands, positive pad on the left, minimum drawn courtyard gap 0.41 mm.
However, support courtyards intersect the left island 23 times and the right
island once; five ADC courtyards also intersect the right island. Bank fit is
not block coexistence. The unchanged 18 electrical blocks have complete
ownership, but physical block placement and shared corridors remain unproved.

## D-BACK repair scope

Stop local P1 generation. Reopen the source owners together, preserving both
failed trials and the two-attempt spend:

1. **Part/process and via-field authority:** reconcile eight U_ISO thermal
   fields with the selected process, exposed-pad geometry and source rules.
   These are TMUX4827YBHR YBH0009 0.4-mm-pitch BGA parts, distinct
   from the three digital-regulator DMQ packages. Their 0.35/0.20 mm vias violate the generated 0.45 mm diameter and annular
   floors. Inspect the 56 ISO clearance and 32 ISO hole-clearance rows as one
   coupled geometry problem; enlarging a via alone is not a verified repair.
2. **Land/process compatibility:** retain manufacturer-backed land geometry;
   resolve seven digital-regulator clearance rows and four intrinsic USB
   pad-to-hole rows against exact selected fabrication capabilities. No blanket
   rule relaxation, deleted check or unsupported package edit is authorized.
3. **Footprint/model completeness:** supply evidenced courtyards for the 16
   missing instances, complete 73 model gaps, and fix required silk clearances.
4. **Endpoint/identity representation:** reconcile USB aliases with native
   schematic parity, eight TPS2662 field mismatches, the USB pair polarity
   contract and ESD endpoint topology metadata. Preserve intended connectivity;
   distinguish checker limitations from actual net errors before fixing either.
5. **Floorplan authority:** reserve real support/ADC space and enforce island
   exclusions with meaningful corridors, rather than merely anchoring the cans.
   Only after upstream repair, independent review and an explicit reassessment
   preserving prior spend may a new placement campaign be considered.

The read-only Terra census accompanying this record refines these owners; it
is advisory diagnosis, not a successfully admitted placement witness.

## Remaining release boundary

INHERITED from the retained connector boundary audit: CONNECTOR-FULL has 19
physical targets still owed. Public drawings and native CAD do not demonstrate
physical fit, reaction, installed-cable or service measurements. This remains a
placement/routing/release hold under the current project gates. Public-only
sourcing, the exact XMOS surplus exception, and manual assembly of the 24
approved through-hole refs remain unchanged. No physical evidence is invented.
