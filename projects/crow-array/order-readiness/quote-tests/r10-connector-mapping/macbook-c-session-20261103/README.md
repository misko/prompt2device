# Pod J1 diagnostic C: saved placement verification pending

Report prepared 3 November 2026 (America/Los_Angeles). Base: `864783eb`.
**HOLD: diagnostic only, not for order or manufacturing approval.**

## Draft and prior-session observations

[New diagnostic pod draft](https://cart.jlcpcb.com/smt-order/?pcbFileNo=c11ad98ea0534ce78a6c3bc004515ffc).
The user requested a fresh diagnostic draft instead of modifying the existing
baseline-A draft. Original production-intent drafts and old diagnostic A were
not modified. This fresh draft retains trial C; do not treat the old restore-A
instruction as an instruction to overwrite this separate C draft.

The preceding 2 November browser session configured 10 fabricated / 8 assembled
pods, Standard top assembly, 4 layers, 1.6 mm, ENIG and JLC04161H-7628.
Both review preferences were set to Do not confirm automatically. JLC displayed
two 5 mm rails and an 85 x 88 mm modified size; manufacturing review remains open.
These are prior-session observations, not a fresh verification of saved settings.

The reviewed Gerber, merged BOM and trial-C CPL were uploaded. JLC reported
20 grouped BOM lines confirmed/selected, including RJHSE-5080 / C599441 for J1
(quantity 8; displayed component-line cost $7.5576). The placement preview loaded.
The CPL specifies J1 X 10.556 mm, Y -9.390 mm, rotation 180 degrees, Top.
This is input-file data, **not verified effective saved placement**.

During visual inspection the agent clicked viewer arrow controls twice without
establishing whether they affected placement. It then reopened the draft and
reprocessed the original trial-C BOM/CPL. The upload dialog retained both expected
filenames, and the preview loaded again. Effective coordinates after reprocessing
were not extracted. Do not infer that the clicks were harmless or that
reprocessing proved restoration. No further speculative adjustment is authorized.

The attached screenshot was captured on 2 November, not during the 3 November
attempt. It shows J1 selected in the top preview with the matching C599441 row.
It does not clearly expose the cable mouth, all eight tails, or both locator pegs.
It is not alignment or manufacturing-acceptance evidence.

## Current verification attempt: blocked

On 3 November the browser inventory tool repeatedly returned:
`Local browser use is disabled in Work settings`.
The user reports the setting is enabled; another retry returned the same error.
No browser tab, saved coordinates, live model, or current settings were accessed
in this attempt. No JLC mutations occurred in this attempt. Browser access must
be restored before the pending verification can be completed.

The earlier precheck report records a matching cached-model hash in the OLD
baseline-A draft. That result must not be represented as a fresh hash check in
this new draft. See ../macbook-c-precheck-20261102.md and ../LOADED-J1-REVIEW.md.

## Backend handoff

1. Preserve this diagnostic draft on HOLD; preserve native boards, r10 uploads,
   old baseline A, and production-intent drafts.
2. Once browser access works, read the saved/effective J1 comp_info/ec record,
   selection and panel transforms. Confirm X 10.556, Y -9.390, angle 180, Top,
   C599441, required parts selected, and no extra offset/rotation. Reopen and
   confirm persistence. Capture actual records, not the toolbar increment.
3. Match the already-loaded package/model and hash the relevant cached OBJ.
   Expected model UUID: 7d3d1c9e95104606a19576559311bb67; expected SHA-256:
   7e16867569831cd98a298dcf3dc5d4692343d067e36dc1aed26f7216d8ff39da.
   Use the existing documented read-only extraction; exclude credentials,
   unrelated account data, signed URLs and full HAR files.
4. Capture an oblique view proving the cable-entry mouth faces the native -Y
   edge. Replay all eight pins and both pegs with the verified effective
   transforms using the backend assessment. Nominal geometry is not production
   acceptance. Report any mismatch before changing anything.
5. Carrier J101-J108 and power J1 remain separate checks after pod review.
   Do not promote this diagnostic CPL to production or finalize placement.

No purchases, reservations, substitutions, vendor messages or manufacturing
commitments. A complete quote was not obtained in this verification attempt.

## Input-file hashes from the clean checkout

- `quote-draft/r10-2c8p-outward-power/pod-gerbers.zip`: `4e429cb5f7f21ab9927798d084e2be50e6525b395ab3f8059dbba714c7ffbb16`
- `quote-draft/r9-merged-bom-candidates/pod-bom-merged-v2.csv`: `d297047101ca69a0d3466518a5c2e85e9ab6f7d900e3f265640d1d1066b78131`
- `quote-tests/r10-connector-mapping/generated/pod-ALL-CONNECTORS-RAW-ORIGIN-TEST-ONLY.csv`: `eef7d7cb2029a0f8f75eb1fbc9a9fa1b2d76430c377893c146dd8c14f9199710`
