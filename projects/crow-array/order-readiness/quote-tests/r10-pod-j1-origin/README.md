# Pod connector reference point test

**Diagnostic only. Native boards and original r10 files are unchanged.**
This follows the [MacBook A/B experiment](../../r10-pod-ab-session-20261102/REPORT.md)
at `a8e2cf84`. B visibly turned the model, but its pins and pegs were not verified;
A was restored. The next test distinguishes an origin offset from rotation alone.
No purchases, reservations, substitutions, vendor messages or manufacturing
approval. Keep all existing production-intent drafts untouched.

## What the geometry establishes

The native pod J1 electrical-pin centroid is `(10.556, 9.390)` mm in board
coordinates. The current CPL uses the body centre `(10.556, 8.373)` mm.
The retained C599441 catalog footprint places its electrical-pin centroid at
`(0, 0)`. At a fixed 180° rotation, aligning its numbered pins to the native pads
requires translation `(10.556, 9.390)` mm. This calculation comes from the
numbered pads, not from fitting the outside of a rendered housing.

**Unverified hypothesis:** JLC uses that catalog origin directly, without
recentering it. The public footprint does not prove the active draft's model
identity or placement convention. Under this hypothesis, B's solder tails and
pegs sit 1.017 mm too far toward the connector edge. C corrects that translation.
The resulting maximum nominal pin-centre residual is 0.014 mm; the independent
peg-centre residual is 0.004 mm. These are CAD registration residuals, not
manufacturing tolerances or proof that JLC will place the part correctly.

| Upload | J1 Mid X | J1 Mid Y | J1 Rotation |
| --- | ---: | ---: | ---: |
| [A restored baseline](../r10-pod-j1-180/pod-cpl-J1-000-BASELINE.csv) | 10.556 mm | −8.373 mm | 0° |
| [B rotation trial](../r10-pod-j1-180/pod-cpl-J1-180-TEST-ONLY.csv) | 10.556 mm | −8.373 mm | 180° |
| [C origin trial](pod-cpl-J1-180-Y9390-TEST-ONLY.csv) | 10.556 mm | **−9.390 mm** | 180° |

C changes only J1's Mid Y relative to B. All 29 references, other coordinates,
rotations, sides and byte formatting remain intact. Relative to original A,
C therefore changes two fields: J1 rotation and J1 Y. C is not a replacement
for the accepted source, an updated release, or a general JLC rotation rule.

## Reproduce and verify

From a clean checkout of `codex/crow-jlc-source-review-20261030`, record the
current commit and run:

```sh
python3 projects/crow-array/order-readiness/r10_upload_check.py
python3 -B projects/crow-array/order-readiness/quote-tests/r10-pod-j1-origin/origin_test.py verify
python3 -B -m unittest discover -s projects/crow-array/order-readiness/quote-tests/r10-pod-j1-origin -p test_origin.py
```

The standard-library generator reads the hash-bound native audit and catalog
pad coordinates, derives C, and verifies original A/B with their existing checker.
`build` reproduces missing identical outputs and refuses differing existing ones.
[manifest.json](manifest.json) retains the source hashes, predicted positions and
calculated residuals. Its prepared status must not be rewritten as approval.
These integrity checks do not perform a browser or manufacturing review.

## Next MacBook session

**Updated priority:** perform the [read-only scene capture](SCENE-CAPTURE.md)
first, leaving A restored. Public viewer-code review found model recentering
and effective/panel transforms that must be resolved before testing C's origin
hypothesis. The B/C sequence below remains conditional, not the next upload.

Use only the existing [POD J1 AB TEST NOT FOR ORDER diagnostic draft](https://cart.jlcpcb.com/smt-order/?pcbFileNo=1f8dfa850b474dc9b4ac3860b26bbd59).
It was last restored to A. Preserve 10 fabricated / 8 assembled, exact
RJHSE-5080 / C599441 matching, all 29 required references, and both
**Do not confirm automatically** review preferences. The original pod/carrier
drafts and native files are not test targets. Do not recreate the draft.

1. Record the current state and upload B to obtain a known comparison input.
   Do not also use the rotation toolbar. Check matching and exclusion settings
   after processing; grouped-row counters alone do not establish coverage.
2. First establish a useful observation method. Try a **2D pad-pattern view**
   that distinguishes vendor terminals from board holes, and orbit the camera
   **below the board** to expose solder tails and pegs. A Top/Bottom population
   selector may hide top-side components rather than show their underside;
   record what it actually does. Deselect J1 for a clear housing/mouth view.
   Do not confuse socket spring contacts or coloured orientation markers with
   PCB solder tails. Keep the board notch and D4 in a context image.
3. If physical registration can be observed, upload C and repeat the same
   views. Keep X, side and rotation unchanged; do not drag the model to fit.
   Check pin 1 identity, all eight terminals, both pegs and the outward mouth
   against the [numbered native geometry](../r10-pod-j1-180/README.md#reference-geometry)
   and [manufacturer drawing](../../r10-orientation-images/sources/rjhsex080.pdf).
   Numeric target: the peg row is native Y=5.960 mm, odd pins Y=8.500 mm and
   even pins Y=10.280 mm. Map the viewer coordinate frame before comparing.
4. Reopen and recapture any observed C state. **Restore A at the end of this
   diagnostic session, even if C looks better**, and confirm its appearance
   returns. Keep the draft on HOLD. Do not propagate C to original drafts.

If step 2 cannot expose the features, do not spend another session collecting
similar roof views. Leave/restore A and capture the actual scene data instead,
if accessible: the selected component's model identity, insertion/rotation/side,
its local numbered-pad and peg coordinates, and the board/panel transform.
Use existing export tools or read-only inspection of data already loaded by the
browser; do not guess private endpoints or publish cookies, tokens, signed URLs
or a full HAR. A sanitized geometry extract would let the backend compare every
pin numerically without occlusion. If neither method is available, report that
precise limitation; no further offset experiments or vendor messages.

## Return and interpretation

Save B/C context, underside and pad views, any sanitized geometry extract,
reopened C and restored A evidence in a new session folder. Record exact uploaded
file hashes, processing completion, draft URL, mapping to native axes, matching
changes and each pin/peg observation. Missing observations stay unknown.

- C aligns both the solder tails and pegs and opens outward: supports the
  origin hypothesis; submit evidence for review, not production approval.
- C moves the housing but pins remain hidden: still inconclusive.
- B is already aligned, C misaligns it, or model/pad channels disagree: reject
  the proposed conversion; investigate the actual model transform.

The previous eight images are useful ingestion evidence, but none supplies a
clear underside solder-tail view. The visible socket contacts in `B-angle.png`
must not be counted as the eight PCB tails. Do not promote a screenshot-only
conclusion to a verified factory placement.

## Carrier scope remains separate

A read-only check of each native carrier connector against retained catalog pads
gave the following **conditional** transforms. They are not upload files:

| References | Catalog-origin hypothesis | Next action |
| --- | --- | --- |
| Carrier J101–J108, C599441 | Same 1.017 mm origin difference as pod; fixed 180° catalog-to-board rotation fits all eight instances within 0.014 mm | Review pod evidence, then test J101 separately before any row-wide change |
| Carrier J1, C3096093 | Catalog-to-board rotation 0° and origin `(185.650, 11.700)` native mm align the three numbered terminals; current CPL is `(188.000, −8.200)`, 180° | Separate source-bound power-jack test; never reuse the RJ translation |

The carrier check loaded the original r10 native boards directly with pcbnew;
the public catalog is not evidence of the actual carrier draft's interpretation.
No carrier CPL or placement was changed. The home-installed Pico USB connector
is not in the factory CPL and is not affected by these catalog-origin trials.
