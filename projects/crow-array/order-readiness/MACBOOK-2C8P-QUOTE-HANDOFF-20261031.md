# MacBook handoff — complete 2-carrier / 8-pod quote, no purchases

**CURRENT PUBLICATION — OR22:** follow the full
[r5 instructions and placement guide](quote-draft/r5-2c8p-complete/README.md).
Complete per-board BOM/CPL pairs now cover 137 carrier / 29 pod parts. JLC batch:
478 SMT + 28 THT; home: two Picos, eight microphones/eight buzzers. Use
`python3 -B projects/crow-array/order-readiness/complete_tht_quote.py verify`.
This publication includes r5 and all its verification dependencies. The sealed
r5 README's local/unpushed wording describes its OR21 preparation snapshot;
this handoff supersedes that publication status, not its engineering holds.
Local THT body centers/pin geometry are verified; selected
JLC library orientations/centers and the full preview remain pending. Quote
upload readiness is not production approval. No purchases or submissions.

### MacBook: sync, verify, then use r5

Use `codex/crow-jlc-source-review-20261030`, not `main`. First check
`git status --short --branch`. If dirty or on another branch, preserve that
checkout and use a separate checkout; do not reset or automatically stash it.
In a clean checkout on the existing branch:

```sh
git fetch origin
git merge --ff-only origin/codex/crow-jlc-source-review-20261030
python3 -B projects/crow-array/order-readiness/complete_tht_quote.py verify
python3 -B projects/crow-array/publication.py verify
python3 -B -m unittest discover -s projects/crow-array/order-readiness -p 'test_*.py'
```

Record HEAD. The quote verifier must report `quote_upload_ready: true`,
`production_ready: false`, 137 carrier refs, 29 pod refs, 506 JLC batch parts,
18 home parts. Publication preservation must pass; DO-NOT-ORDER is expected.
If the known macOS temporary-directory symlink issue recurs in tests, retain
the original error and rerun with `TMPDIR=/private/tmp`.

For the authorized quote-only browser pass, use the complete r5 per-board
Gerber ZIP/BOM/CPL pairs. Set **2 assembled carriers / 8 assembled pods**;
candidate bare counts are 5/10 pending service-minimum confirmation. Follow
r5's matching, physical-orientation and full-preview checklist. Do not use r4
worksheets or old SMT-only CPLs. Keep all requested THT parts in scope.
No parts purchases, reservations, substitutions, paid/noncancelable quote
requests or production approval. If shortage procurement prevents a complete
price, capture the remaining costs and stop at that commitment boundary.

## Historical handoff below — superseded, not current instructions

Use r5's next-MacBook section instead. The historical r3 instructions below
must not restore home THT, omit JLC RECOM sourcing, or use SMT-only CPLs for
the current mixed population. Historical stock/fee observations remain evidence,
not current allocation or a complete mixed-assembly price.

Read `JLC-2C8P-RECONCILIATION-20261031.md` first. This handoff replaces older
1+8/5+8 instructions **for quote scope**, not the unchanged r3 upload data.
No complete quote is promised: the previous session could not advance with all
shortage parts selected. Preparation is not authority to buy stock to unblock it.

## 1. Sync and verify without disturbing user work

Use the existing `codex/crow-jlc-source-review-20261030` branch only after this
handoff has been published there. Check `git status --short --branch`; if dirty,
preserve changes and use a separate clean checkout rather than reset/stash them
automatically. In a clean checkout on that branch:

```sh
git fetch origin
git merge --ff-only origin/codex/crow-jlc-source-review-20261030
python3 -B projects/crow-array/order-readiness/home_assembly_plan.py verify
python3 -B projects/crow-array/publication.py verify
python3 -B -m unittest discover -s projects/crow-array/order-readiness -p 'test_*.py'
```

Record HEAD. Do not claim to have this revision if the new handoff is absent.
If the documented macOS temporary-directory symlink issue recurs, rerun the
affected tests with `TMPDIR=/private/tmp`; retain the original failure and fix.

## 2. One bounded account pass

At most **30 minutes of active browser work**, one normal retry per failed
screen. Do not repeat the completed 35-identity stock sweep. Work in existing
drafts with previously uploaded files; no new upload or vendor contact without
specific authorization. Read-only quote inspection is allowed; no cart additions,
payments, reservations, substitutions or manufacturing commitments. Do not submit
the pre-order quote form with the recorded noncancelability warning. Capture
that warning if it remains, and stop at it rather than assuming quotation is free.

1. Confirm **five bare / two assembled carriers** and **ten bare / eight
   assembled pods**, Economic/Standard as currently observed. Record private
   draft IDs locally (redact account details from public evidence). Do not change
   service, stack, tooling or approved scope merely to obtain a price.
2. Confirm 127 carrier and 28 pod SMT placements per board, all required rows
   selected. The r3 `carrier-bom.csv`, `pod-bom.csv`, CPLs and Gerber ZIPs remain
   the correct per-board data. Do not multiply BOM row quantities by batch size.
   Do not use r1 full BOMs or r2 manual-placement templates. RECOM and the other
   five home identities must not enter JLC's component charge.
3. For the six CSV identities only, capture **per-job installed, gross,
   allowance/minimum basis, pool/source eligibility, uniquely usable stock,
   final procurement quantity, supplier/pack, unit/line price, fees and validity**.
   Preserve source URLs, date/time and redacted evidence; an unknown remains blank.
   Confirm the two views of seven fuses are one pool. Compare regular fuse
   replenishment versus global full-job coverage; do not assume a 21-piece global
   top-up works. Ask whether the resettable fuse incurs the potential $40 charge.
   Do not add allowance twice. Keep Murata 20+20 unless JLC explains otherwise.
4. Recheck the TI ADC source once because public TI and the account offer differ.
   If unresolved, inspect exact **PCM1864DBT** from DigiKey inside Global Sourcing;
   no DBTR replacement. Confirm actual packing, handling fee and gross need for
   ADC/CTS, including whether the carrier's assembly service supports them.
5. Capture full component and service totals only if attainable with every part
   included and without a commitment. Keep component procurement/prepayment,
   assembly consumption/credits, surplus, setup, stencil, feeders, fab/engineering,
   packing/inspection/import fees and delivery separate. Get combined shipping
   and destination-specific tax/duty if the existing quote screens support it;
   do not publish the address. Distinguish included fees from extra charges.
6. Record supplier lead trigger and usable JLC inventory date, assembly completion
   and delivered date separately. If only ranges are supplied, preserve them.
   Capture placement previews and any process proposals, **without production
   approval**: CTS method, ADC packing, orientation, stack, rails, paste and
   finished mechanics. Refer unsupported requirements for review, not a waiver.
7. If no complete quote is possible, capture the exact blocking screen and list
   costs still unknown. Do not proceed with parts unselected. Prepare the message
   below for user approval; do not send it under this handoff's authority.

## 3. Optional non-binding support inquiry — UNSENT

This is a proposed alternative to a committing order-parts workflow. Obtain user
authorization to contact JLC before sending; first establish that answering does
not create an order, reservation or noncancelable procurement quotation.

> Please provide information only for our existing two PCBA drafts: five bare
> carriers with two SMT assembled, and ten bare pods with eight SMT assembled.
> Do not initiate procurement, reserve stock, create a noncancelable quotation,
> charge us, substitute parts or start fabrication/assembly. If answering requires
> any such action, please identify that boundary without taking it.
>
> We need all 127 SMT placements per carrier and 28 per pod. All RJ45/power jacks,
> RECOM, Pico, microphones and buzzers are supplied/installed at home. Can you
> provide a non-binding all-in estimate while the six exact shortage parts remain
> unpurchased, with any unquotable costs explicitly marked?
>
> Please reconcile gross demands by carrier/pod job: CB3LV-3I-12M288000 2/0;
> 1206L010/30WR 18/10; GRM21BR71A105KA01L 20/20; C2012X7R1V225K125AE 0/10;
> C3216X7R1V106K160AC 4/0; PCM1864DBT 4/0. Are these still correct for the
> selected packing, and do they already include every allowance/minimum?
> Both fuse screens show seven available: is this the same pool, usable with
> regular replenishment or Global Sourcing in each job? Please give permitted
> source allocation and final buy quantities, not summed screen shortfalls.
>
> Please compare regular fuse replenishment with its Global Sourcing offer,
> including whether PPTC 1206L010/30WR attracts inspection/3C fees and how often.
> For all six parts confirm exact maker/MPN, supplier, packing, charges, quote
> validity and usable warehouse date. Please verify the TI-origin ADC offer or
> exact DigiKey DBT alternative; do not replace it with DBTR.
>
> CTS X1 is a 7x5mm SMD oscillator (manufacturer reflow limit 260 C / 20 s),
> although the catalog labels it Wave Soldering. What actual compatible assembly
> process, service and fee will you use? For PCM1864DBT TSSOP-30, what packing,
> handling, moisture controls and allowance apply to this small lot?
>
> Please separate components/prepaid stock and credits, fab, engineering,
> setup/stencil/feeders/labor, sourcing/packing/import charges, combined delivery
> and tax. State what cannot be quoted before paying and the exposure at that
> point. Give supplier, warehouse-ready, assembly and delivery timing separately.
>
> Process review remains conditional: released four-layer 1.6mm construction,
> carrier 7628A / pod 7628, finish, tooling/rails, no contour/datum changes,
> home-pad paste exclusions and retained assembly/mechanical controls. Please
> identify unsupported controls rather than silently substituting defaults.
> This message is neither production-preview approval nor authority to buy.

For an authorized technical review, identify the exact existing draft IDs and
six r3 data filenames. Detailed mechanical/paste controls are in the retained
release; any additional attachment requires an explicit scope check. These
brief notes are not a claim that JLC has received or agreed to the full controls.

## 4. Return one usable decision packet

Save a new dated account report, keep previous evidence unchanged, and update
STATUS. Report: exact build scope; six-line quantities/source/fees; other SMT
price; fab/assembly/setup/stencil; combined shipping/tax; home-kit cost separately;
prepaid inventory credits; total or explicitly incomplete subtotal; dated schedule;
open placement/process conditions; commitment boundary; and two ranked paths.
Do not put personal/account information or authentication data in Git.

Preferred: JLC-managed exact sourcing with confirmed quantities/fees/dates and
no source-pool mixing assumption. Fallback: targeted exact consignment or a
separate user decision about staged procurement if a complete quote requires
prepayment. Stop after this pass; no new search loop, purchase or automatic
production approval. Validate unchanged r3/release and report test results.
Publishing the new account evidence requires the user's existing applicable
publication authority or a new request; no main merge is implied.

Suggested MacBook prompt:

> Follow vNext and MACBOOK-2C8P-QUOTE-HANDOFF-20261031.md in
> projects/crow-array/order-readiness. Perform its bounded read-only quote pass
> for 2 carriers and 8 pods using the existing JLC drafts. Reconcile all six
> shortages, shared inventory, fees and assembly conditions without omitting
> components. No purchases, cart additions, reservations, substitutions,
> noncancelable quote submission, vendor contact or manufacturing approval.
> Return a complete non-binding quote if accessible, otherwise the exact
> commitment barrier and an unsent inquiry for my approval. Preserve the release.
