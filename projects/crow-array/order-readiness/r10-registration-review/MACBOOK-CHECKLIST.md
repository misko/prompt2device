# MacBook: authorized 7628A quote selection and connector evidence

The user explicitly authorized **quote-only selection of JLC04161H-7628A** after
reviewing the assessment of JLC's1.5542 mm ±10% warning. This supersedes only the
earlier instruction to leave that particular warning unaccepted. It does not
approve manufacture, finished-board compliance or connector placement.

**No purchases, payments, reservations, substitutions, noncancelable pre-orders,
vendor messages or manufacturing commitments.** Do not approve production files
or placements. Keep both automatic-confirmation options disabled.

## 1. Pull and verify

Use the existing repository/shared branch `codex/crow-jlc-source-review-20261030`.
Check for local work first; do not reset, overwrite or stash another task's work.
In a clean checkout already on the shared branch:

```sh
git status --short
git fetch origin codex/crow-jlc-source-review-20261030
git merge --ff-only origin/codex/crow-jlc-source-review-20261030
python3 projects/crow-array/order-readiness/r10_upload_check.py
```

For a dirty/different-branch checkout, use an isolated worktree or ask before
changing it. The portable check must pass213 r10 files,105 preserved r9 files,
136 carrier/29 pod factory references and476 SMT/28 factory THT/20 HOME parts.
No KiCad is needed for this integrity check; it is not an engineering replay.
Read the [assessment and coordinate table](REVIEW-AND-NEXT-STEPS.md) and
[original r10 upload handoff](../MACBOOK-R10-HANDOFF.md).

## 2. Select the intended carrier stack for quotation

Existing [r10 carrier draft](https://cart.jlcpcb.com/smt-order/?pcbFileNo=ace1600497a949bebfdd38f3ef826f7f):
**5 fabricated, 2 assembled**. Existing
[pod draft](https://cart.jlcpcb.com/smt-order/?pcbFileNo=71c384e886a94642a54e0c804cea3a97):
**10 fabricated, 8 assembled**. Preserve both drafts and their history.

- Select carrier **JLC04161H-7628A** with standard assembly. For the reported
  warning that actual thickness is **1.5542 mm ±10% rather than1.6 mm**, selecting
  **Yes solely to update this non-binding quote is authorized**. Capture the
  full warning and the resulting selected-stack screen. If its wording/range
  changes materially or adds a production/financial commitment, stop and report.
- Record the full range **1.39878–1.70962 mm**, not just the rounded0.05 mm
  nominal difference. This selection does not waive any retained hole, annulus,
  seating, local-top, Pico underside, process or retention limits.
- Reopen or revisit the settings to confirm7628A actually persisted; do not
  infer it from clicking Yes. Keep the pod on **JLC04161H-7628**.
- Recheck ENIG, four layers, required outline/rail settings, quantities and
  standard assembly. Do not accept a substitute stack or automatic production
  confirmation. Record unexpected resets or changed terms.
- The stack choice needs no new board revision. If JLC requires file re-entry,
  use only the unchanged matched r10 Gerbers/CPL and reviewed grouped-v2 BOMs
  specified in the original handoff. Never mix r9 carrier fabrication/CPL.
  Audit all136/29 references again after any reset or upload. Do not bypass a
  shortage with "Do not place"; only the existing HOME split is intentional.

## 3. One bounded connector evidence pass — no rotations

For **pod J1, carrier J101 and carrier power J1**, save actual screenshots of:

1. The selected exact catalog/manufacturer/MPN and placement-table XY, angle,
   side and reference.
2. An orthographic top view, an underside or transparent/hide-body view if
   available, and a tilted view showing the mouth. Include board features that
   establish which edge and side are being viewed.
3. Physical numbered terminals and locator pegs registered to the board holes:
   RJ pin1, pin8 and both pegs; power jack pins1,2,3. The generic preview red dot
   alone is not proof of physical pin1.

Use the assessment's exact coordinate table and [native audit](native-audit.json).
Normalize panel-origin shifts/mirroring from known board datums, not an assumed
5-mm rail offset. If the UI offers a read-only model/transform export, retain it.
Confirm the other seven carrier RJ instances share the same part/convention;
do not treat one screenshot as proof of all eight placements.

Do **not** rotate models or edit CPL angles to make openings look outward.
If pin/peg evidence shows a consistent vendor angle/centroid difference, return
the measured mapping for a reviewed vendor-specific correction. If pins align
but the mouth is wrong, report a possible model defect. If numbered witnesses
cannot be exposed, stop after this pass, state exactly what is missing, and
request authorization for a targeted JLC inquiry. Do not send it yourself.

## 4. Refresh price and return the evidence

Obtain the new itemized carrier and pod quote after the stack selection, wherever
the non-binding UI permits. Record PCB, components, SMT/THT, setup/stencil/feeders,
handling, sourcing, shipping and tax separately; mark unknown items unknown.
Check stock/gross quantities and lead-time observations without allocating parts
or entering noncancelable sourcing. The old **$390.97** is a comparison only,
not the price of a confirmed7628A job or a delivery promise.

Save a dated report with draft URLs, upload hashes, persisted stack/settings,
before/after prices, exact warning screenshots, connector witness screenshots,
reference coverage, missing evidence and remaining holds. Separate measured or
observed facts from hypotheses. Keep placement, process and production approval
on hold even if a complete quote is displayed. Do not alter the validated r10
package or its manifest, and do not purchase anything.
