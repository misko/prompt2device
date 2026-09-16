# Fresh conductor regeneration after package-clearance corrections

Recorded 2026-09-09 03:15 UTC (September 8, 20:15 Pacific). This is a
schematic regeneration boundary, not placement acceptance or a release.
Engineering source: `c29cb85e497cc347f02d1c98e66474909e4894a4`.

## Measured execution

The full `03_src/rebuild_all.sh` ran without a resume flag, after the previous
checkpoint cohort had been explicitly archived. It completed its source and
electrical battery and stopped at its deliberate prelayout checkpoint:
2026-09-09T03:11:41Z to 03:12:56Z, 74.886 seconds, exit 2. No gate was bypassed.

- Source governance: 846/846 declared keys, 741 proven readers, zero orphans.
- Producer diagnostics: zero embedded errors; 1,681 advisory warnings retained.
- Freshness: 9/9 assertions; rendered PDF and converter use this run's JSON.
- Component census: 302/302 in JSON, manifest, schematic and native netlist.
- Connectivity invariants: 115/115; label survival: 165/165 with 209/209 pin-map assertions.
- Electrical closure: 9/9 specialist gates; source sourcing selection: 2/2.
- PDF: 19 pages, 302 components. Native schematic: 877 pins, 1,707 wires.
- Independent node comparison against the unchanged PCB: 166 named nets,
  836 connected nodes and 41 intentional no-connects; zero differences.

A fresh public catalog check completed at 03:15:13Z: 52/52 exact codes meet
five-board quantity, with no substitution. C53283916 remains 60 catalog units
against 40 required. This is LCSC catalog stock, not JLCPCB assembly inventory,
allocation, price, or order authority. All operator response fields remain blank;
no authenticated receipt was created and nothing was uploaded.

`rebuild_all.sh --resume-after-public-prelayout` ran 03:15:29Z–03:15:32Z:
11/11 checkpoint files and 422/422 complete input-census files verified;
public-only prelayout readiness 4/4; ERC zero errors, 2,100 warnings retained
(1,605 endpoint-off-grid and 495 embedded-symbol-library configuration warnings).
The schematic checkpoint pins 7/7 files. Exit 1 is the expected stale-review
refusal: topology's rules hash, and readability's rules and PDF hashes changed.
Those witnesses have NOT been restamped or treated as accepted.

## Exact regenerated subjects

| Subject | SHA-256 |
|---|---|
| `03_tscircuit/build/circuit.json` | `2e22dabb12a502e4f0a2a1fa7ebf0aa45f1ebaf2b57b3f76b48c1d13a6e9724b` |
| `03_tscircuit/build/schematic.pdf` | `8b90682c4bf56f4d4b4411f98d9a94f2abb3d4b3fda32ac10adc942679aef68e` |
| `04_kicad/crow_audio_carrier_v1.kicad_sch` | `d9091238205d81fd7af3427d6ef4afe0242e22df9de809865bf324c43ba1fe72` |
| `06_build/netlists/crow_audio_carrier_v1.net` | `ed9b7b79d5f47178f7814ef5541609629c616c93506ffd0ac896d537a92f693f` |
| Unchanged, unaccepted current PCB | `66003462ab2221377fd8ad54fdeabe3097983e496f1fe7b22c345fd7843c3060` |

The older pinned schematic under `03_tscircuit/kicad/` is intentionally NOT
promoted before independent review. The producer's UUID churn does not change
the independently compared electrical node map.

## Retained execution evidence

Bounded attempt logs/result/state records are captured under
`06_build/verification/schematic-review-20260909-c29cb85e/capture/`.
The original runner records remain under
`/tmp/carrier-fresh-build-20260908.4RBsSy/`.

| Attempt | Log SHA-256 |
|---|---|
| `conductor-c29cb85e-20260909-r1` | `8aa68cad1a3a592de4d63e3dd1e460e8257e0a0e878c5952c808c94ffdcdda48` |
| `conductor-public-stock-20260909-r1` | `757d9ce55e8ae30df0731c5bfc63801e5d43aebc46b6cb210fef21f71a7397cb` |
| `conductor-public-resume-20260909-r1` | `575647ab4ef4da4921d117d0a03c32b91e7f5438dd27f8f6e6497d8d874a63ea` |
| `conductor-node-parity-20260909-r1` | `f6d02396ad62a86ab70f32cff3ba13f99d9d3b65073750aa99e0c0d65a8fc33e` |

Before regeneration, the generated JSON/PDF, pinned/current native project,
netlists and prior build-provenance record were recoverably archived in
`/tmp/carrier-conductor-20260908.8eGI7v/prior-generated.tar`, also copied into
the capture directory. Archive SHA-256:
`c168a2d590a181e4a83e14145bddd619546a75e13969867c4f0f583f3b9726d2`.
The conductor removed/replaced only its generated schematic SVG/PDF outputs;
their previous available bytes remain in this archive and Git history.

## Next boundary and limits

Fresh exact-subject topology and all-page readability reviews are required.
Only after adoption may the checkpoint-aware conductor promote the reviewed
schematic and regenerate placement. Do not rerun TSX merely to continue.

INHERITED from the committed clearance experiment: 224 source tests pass and
the disposable native-filled board has 0 violations / 498 opens / 0 parity.
This new full run has not regenerated or accepted that board. Silk ownership,
routing, final 0/0/0, fresh placement/release reviews and carrier sealing remain.
The four broader contract-suite failures remain recorded in the preceding
source-backtrack report, not waived by this narrower build.

The pod's immutable design release is unchanged. Both designs remain
DO-NOT-ORDER; TOP77/0.20 A first-power and all physical, sourcing and
publication holds remain. No main push or release seal occurred.

## Independent review in progress / supplemental silk diagnosis

The exact generated subject was committed as
`6cb756c92e34b7faa81544beb2b9a0d03c52ddb1`. Two independent fresh/read-only
commissions were issued at03:19:09Z with a hard03:39:09Z deadline and461-file
packets. The 19-page readability reviewer completed at03:25:44Z; root observed
and admitted it at03:30:21Z after rechecking every packet/artifact hash and all
8 checklist rows. Verbatim witness SHA:
`8d610eb401e95a6b9db3f7061c9d9949026400d124ca6e11c6a2e8c81c07bd6c`.
Two nonblocking P2 presentation suggestions are in `08_reviews/DISPOSITIONS.md`.
Topology remains pending at this record. No placement permission is inferred.

While waiting, a read-only native-board diagnostic independently reproduced
the earlier generator's exact30 missing and102 misowned reference sets over
302 fitted components. Four holes and three bare fiducials are not components;
the first diagnostic attempt incorrectly included the fiducials, and its
33/104 output is retained but not used as the component census.

The second diagnostic clips continuous nearest-component regions against
expanded native pad/body/ink bounding boxes. It found a positive available
area for existing full-length labels in36/132 cases (with other ink fixed),
and74/132 when only physical obstacles are considered. Hypothetical four-character
labels increase those counts to94/132 and117/132 respectively. This is a
conservative geometric diagnosis, NOT a DRC, simultaneous placement solution,
or permission to rename references; zero bounding-box area cannot prove actual
glyph placement impossible. It distinguishes coarse search/label competition
from label-length/physical-density issues. No board or source byte was changed.
The next owner should test local placements and a clear labeling scheme,
not globally shrink text or accept distant ambiguous references.

Diagnostic subject PCB SHA:
`8634227fe41772225b7bcad8bc96ed9e830179af050acc665f0ef9b0ad0e7e23`.
Attempt `silk-capacity-diagnostic-20260909-r2`,6.981seconds, logSHA:
`3675c7c0fad2b7e630582a5c5b55e2b9236e628ce6bd29b3e954c0d4a3910fc9`.
The diagnostic and native F.Silkscreen/F.Fab/F.Mask context plot are retained
under `/tmp/carrier-conductor-20260908.8eGI7v/`; the overlay's grey F.Fab text is
assembly-document ink, not a claim that all displayed text prints on the board.

## Review closeout: source backtrack supersedes placement resume

Readability remains adopted8/8 SOUND. Topology supplied a substantiated
cold-start candidate but missed03:39:09Z final deadline; root interrupted at
03:39:11Z and recorded all8 formal rows INCOMPLETE. No completed verdict was
fabricated from messages. Root independently confirmed the source input path
and absent startup bound. PR-REVIEW remains FAIL; placement is not admitted.
See [source-backtrack record](2026-09-09-cold-start-input-protection-backtrack.md)
for primary limits, preserved messages, timeout and work order. No PCB regenerated.
