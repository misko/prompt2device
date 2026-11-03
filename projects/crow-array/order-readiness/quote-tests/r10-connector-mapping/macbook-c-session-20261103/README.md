# Pod J1 trial C: saved coordinates verified, mechanical review open

3 November 2026. **Diagnostic draft only; HOLD. Not for order or manufacturing
approval.** The 3 November read-only capture verifies J1's saved coordinate
record after reopening. It does not establish mechanical acceptance.

## Draft identity and uploaded files

The [new trial-C diagnostic draft](https://cart.jlcpcb.com/smt-order/?pcbFileNo=c11ad98ea0534ce78a6c3bc004515ffc)
is `c11ad98ea0534ce78a6c3bc004515ffc`. It is **not** the earlier
[baseline-A diagnostic draft](https://cart.jlcpcb.com/smt-order/?pcbFileNo=1f8dfa850b474dc9b4ac3860b26bbd59),
`1f8dfa850b474dc9b4ac3860b26bbd59`. Following the user's request for a fresh
draft, the agent started a new JLC quote, uploaded the pod Gerbers, configured
10 fabricated / 8 assembled boards and uploaded the reviewed BOM and trial-C
CPL. In the initial session the upload dialog showed the expected BOM and CPL
filenames; after two viewer-arrow clicks whose effects were uncertain, the agent
reprocessed the same files. Production-intent drafts and the older baseline-A
draft were not deliberately modified.

The exact uploaded filenames and SHA-256 hashes of the corresponding local
input files, independently rechecked for this report, are:

| Input | Repository-relative file under `projects/crow-array/order-readiness/` | SHA-256 |
| --- | --- | --- |
| Gerbers | `quote-draft/r10-2c8p-outward-power/pod-gerbers.zip` | `4e429cb5f7f21ab9927798d084e2be50e6525b395ab3f8059dbba714c7ffbb16` |
| BOM | `quote-draft/r9-merged-bom-candidates/pod-bom-merged-v2.csv` | `d297047101ca69a0d3466518a5c2e85e9ab6f7d900e3f265640d1d1066b78131` |
| Trial-C CPL | `quote-tests/r10-connector-mapping/generated/pod-ALL-CONNECTORS-RAW-ORIGIN-TEST-ONLY.csv` | `eef7d7cb2029a0f8f75eb1fbc9a9fa1b2d76430c377893c146dd8c14f9199710` |

These are hashes of the local input files, not hashes independently returned by
JLC for the server-side copies. The initial quote specified Standard top-side
assembly, four layers, 1.6 mm, ENIG and JLC04161H-7628, with both production-file
and placement review settings set to **Do not confirm automatically**. JLC
displayed two 5 mm rails and an 85 x 88 mm modified size. Those are observations
from initial setup, not a fresh verification of saved quote settings.

## Saved J1 placement

In the continuation, the draft was reopened and the existing JLC `loadMerge()`
console object was expanded without executing console commands. The captured
`designator_info[0].top[25]` record identifies J1 / `C599441` and reports:

| Field | Captured value |
| --- | --- |
| Effective placement `ec` | X **10.556 mm**, Y **−9.390 mm**, angle **180°** |
| Mount flags | `is_mount: true`, `sel_mount: true` |
| Board datums | X 0, Y 0; `flipped_from_orig: false`; mirror datums null |
| Default panel set | X offset 0, Y offset 0, angle 0 |

See the [sanitized record](j1-effective-record.json) and the
[J1 accessibility capture](j1-effective-record-ax.txt). The latter contains
the J1 row with trailing whitespace normalized; the JSON separately transcribes
the observed board and panel fields.
The [sanitized preview](j1-effective-preview-sanitized.png) shows J1 selected
but is not evidence of its numerical coordinates, pin/peg alignment or mouth
direction. Browser chrome, unrelated console contents and metadata were removed
from the preview.

**Trial C remains loaded in the new diagnostic draft; baseline A was not
restored there.** This differs from the earlier same-draft restore-A procedure:
the user subsequently requested a fresh draft for each test. Keep the new C
draft on HOLD and do not overwrite the separate old baseline-A draft. The
verified coordinate record supersedes the earlier coordinate-access blocker;
do not repeat that investigation merely to establish the same values.

## Diagnostic omission

The continuation reported a shortage of BAT54S-7-F / `C83574`: JLC displayed
21 needed including allowance, 4 available, and a shortfall of 17. To inspect
the diagnostic preview, D2 and D3 were omitted in **this diagnostic draft only**;
the continued BOM showed 19 confirmed grouped lines. **Both D2 and D3 remain
required for production.** This draft is not a complete assembly quote or a
production-ready BOM. Resolve the shortage without substitution before any
production proposal.

## Next backend check

1. Verify the **actual loaded model identity and cached OBJ hash in this new
   draft**, rather than assuming the old draft's asset matches. The previously
   assessed UUID is `7d3d1c9e95104606a19576559311bb67`; the expected SHA-256
   is `7e16867569831cd98a298dcf3dc5d4692343d067e36dc1aed26f7216d8ff39da`.
   The prior matching cache observation was from the older A draft and does not
   prove the new draft's loaded asset.
2. Replay all eight pins and both locator pegs using that verified model and the
   captured trial-C placement and panel transforms. Verify that the actual
   cable-entry mouth faces the native −Y board edge. Record any mismatch before
   changing anything. Nominal geometry checks do not constitute manufacturing
   acceptance.
3. Review carrier J101–J108 individually and power J1 separately after the pod
   result. Do not copy the diagnostic CPL into production-intent drafts.

Use only relevant sanitized records; exclude unrelated account information,
credentials, signed URLs and full HAR files. No purchases, reservations,
substitutions, vendor messages or manufacturing approvals were made in the
reported session. Native boards and production files remain unchanged.
