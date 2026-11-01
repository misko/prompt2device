# MacBook handoff — Crow r9 quote only

Use branch `codex/crow-jlc-source-review-20261030` in the existing
`misko/prompt2device` repository. Do not use main or a historical r7 upload set.
User authorized publishing this package and preparing the JLC quote, **not
purchasing, reserving parts, noncancelable preorders or manufacturing**.

## 1. Obtain and verify the exact package

Preserve any local edits. From the existing repository, a new isolated checkout
avoids mixing them with this task (choose a different new directory if taken):

```sh
git fetch origin codex/crow-jlc-source-review-20261030
git worktree add --detach ../crow-r9-quote origin/codex/crow-jlc-source-review-20261030
cd ../crow-r9-quote
python3 projects/crow-array/order-readiness/r9_quote.py verify
python3 -B projects/crow-array/order-readiness/test_r9_quote.py
```

These r9 checks require Python's standard library, not KiCad or Linux-specific
paths. Expect PASS, 113 payload files, 105 preserved r8 files, and five tests.
The packaged r8 baseline and its manifest are required; do not copy r9 alone
and then interpret a failed dependency check as permission to bypass validation.
KiCad-dependent r8 engineering tests were run separately on the server.

Current r9 manifest SHA256:
`4a06ac75b6c606f7b0b9ddff38122c5cf533315c8fda409c5c28278ff598cd36`.

All upload files are in:
`projects/crow-array/order-readiness/quote-draft/r9-2c8p-home-clock/`.
Read that folder's [README](quote-draft/r9-2c8p-home-clock/README.md) before editing
the JLC drafts. Package manifests describe quote artifacts, not order approval.

## 2. Upload matched files, preserve earlier drafts

| Job | Fabricated | Factory assembled | Required matched files |
| --- | ---: | ---: | --- |
| Carrier | 5 | 2 | `carrier-gerbers.zip`, `carrier-bom.csv`, `carrier-cpl.csv` |
| Pod | 10 | 8 | `pod-gerbers.zip`, `pod-bom.csv`, `pod-cpl.csv` |

Each BOM/CPL describes one board; do not multiply its quantities manually.
Existing drafts, still historical r7 at the last check:

- [Carrier](https://cart.jlcpcb.com/smt-order/?pcbFileNo=d36999d20e3d4544a4e7d21e9b703b41)
- [Pod](https://cart.jlcpcb.com/smt-order/?pcbFileNo=71c384e886a94642a54e0c804cea3a97)

Prefer a new carrier quote draft, retaining the old draft as history. If using
an existing draft, preserve its prior configuration/evidence and replace ALL
THREE carrier files, not merely its BOM. Record new draft IDs and filenames.
Pod files are byte-identical to the previous set; verify identity and quantities
if retaining its existing draft. Do not delete unrelated drafts or cart items.

Carrier upload SHA256 checks:

| File | SHA256 |
| --- | --- |
| carrier-gerbers.zip | `7df8b8832b4f146386dbc7000d3d3279a52350c2062234e0358f42b4478ed918` |
| carrier-bom.csv | `9231f878b734c8ffe7e7a61270cfed65e850a23c7efc7f94b33cacd429a5c668` |
| carrier-cpl.csv | `41764feb77702af7d047f89caa9f94c800c17eb328da7fd13f5431ffefeb0e94` |

**Do not simply mark CTS X1 "Do not place" on the old r7 carrier:** r9 has the
new TI footprint/copper and moved C4. The correct r9 factory files contain no
X1. The final circuit still requires the user-installed TI clock.

## 3. Reconcile population and preview

- Factory: 476 SMT + 28 THT across the two jobs. Exactly 136 factory reference
  placements per carrier and 29 per pod (not BOM group/portal confirmed counters).
- Home: 2 original SC0915 Picos with retained D1-only modification, 2 exact
  TI LMK6CE012288CDLFR oscillators, 8 CMA-4544PF-W microphones and 8 CPE-203 buzzers.
- Carrier X1 must be absent from factory BOM/CPL. Do NOT upload
  `home-clock-placement.csv` or `home-install-parts.csv` as factory inputs.
- C4 must remain factory fitted as Samsung CL21B105KBFNNNE / C28323, 1uF 50V
  X7R 0805, CPL (83.46,-82.9)mm, rotation0, Top. Aggregate need for this MPN is14.
- Factory THT remains 24 Amphenol RJHSE-5080 jacks, 2 PJ-102AH power jacks and
  2 TRACO TSR1-2450 regulators. Match full actual MPN spelling from the BOM;
  no YLPTEC match or newly suggested equivalent is authorized.
- Match every factory reference, manufacturer, MPN, package and C-code to the
  supplied BOM, including repeated rows. Recheck the pod R5/R9/R10 common-part
  inventory warning; the last browser's "21 confirmed" was not proof of stock.
- Obtain full top-side previews for both boards; inspect retained THT positions,
  orientation/polarity, C4 position and empty X1. Document discrepancies rather
  than silently editing CAD/CPL. Keep production-file and placement review set
  to **Do not confirm automatically**. Viewing a preview is not approving it.

## 4. Quote and stop boundary

Preserve the README's stack, ENIG, precision-outline, rail/finished-edge,
localized THT, seating, stencil/reflow, no-unqualified-wash and first-article
controls. Carrier stack JLC04161H-7628A thickness warning remains unresolved;
do not approve mechanical tolerance concessions simply to advance. Pod requested
stack is JLC04161H-7628. Record any auto-added rails, finished dimensions and
delivery/depanel choices. Confirm empty X1 pads remain suitable for home reflow.

Read-only inspection and ordinary quote-draft file uploads/matching are allowed.
Historical authorization covered ordinary assembly-service terms for quotation;
new liability waivers, manufacturing approvals or noncancelable sourcing are not
covered. Stop if the UI requires such a commitment or an unresolved stack/process
acknowledgement. Do not omit any other required factory part to bypass shortages.

Collect itemized PCB, SMT/THT assembly, parts, setup/extended fees, sourcing,
shipping and tax; record currency, date and estimated lead times. Distinguish
installed counts, procurement gross quantities/MOQs/attrition and actual inventory.
Do not call a partial board-screen figure a complete populated-board quote.

Return draft URLs, uploaded file identities, quantity selections, exact matches,
warnings, placement evidence, price breakdown and open production holds. No
payment, purchase, reservation, vendor message, order submission or manufacturing
commitment. TinyFish can inspect the uploaded drafts afterward; its server-file
transfer limitation, not authentication, prevented this upload on the server.

## Engineering provenance note

The r8 engineering record and reviewed draft7 are included. Earlier failed
draft1 through draft6 remain preserved locally, not included in this publication.
Historical absolute `/tmp` paths in its independent review identify the original
review run; the reviewed evidence bytes are also retained inside the quote
packages' `engineering/` folders. Do not rerun historical build scripts or alter
hash-bound manifests just to upload the already verified r9 artifact. This
handoff does not claim a portable clean rebuild of every historical draft.

Validation note: new handoff and r9 code/instructions pass scoped whitespace
checks. Full staged `git diff --check` reports whitespace in preserved native
CAD/CSV and research artifacts; these hash-bound bytes were deliberately not
reformatted. This does not replace the passing manifest/population checks.
